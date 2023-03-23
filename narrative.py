import json
import logging
from os import system
import re
from typing import List
import jinja2
from prov.model import ProvDocument, ProvRecord, ProvBundle
from prov.dot import prov_to_dot
from prov.constants import PROV_MEMBERSHIP, PROV_DERIVATION, PROV_GENERATION

from constants import DISK_ONTOLOGY_CONFIDENCE_REPORT, DISK_ONTOLOGY_CONFIDENCE_REPORT_LOCALNAME, DISK_ONTOLOGY_TRIGGER_LINE_OF_INQUIRY, HYPOTHESIS_BUNDLE_IDENTIFIER, META_WORKFLOW_INPUT_FILE_BINDING, PROV_GENERATED_AT_TIME, TRIGGER_BUNDLE_IDENTIFIER, QUESTION_BUNDLE_IDENTIFIER, HYPOTHESIS_VARIABLES_BINDING, QUESTION_VARIABLES_BINDING, META_WORKFLOW_VARIABLES_BINDING
from templateHandler import render_template
from triggerSummary import TriggerSummary


class DataNarrative:
    def __init__(self, provDocumentWrapper, hypothesisName):
        self.provDocumentWrapper = provDocumentWrapper
        self.questionVariables = {}
        self.dataSource = None
        self.dataQueryVariables: List = None
        self.dataQueryDeltaLocations = None
        self.dataQueryDelta = None
        self.numberSetsReturned = {}
        self.totalNumberSets = {}
        self.workflowName = None
        self.workflowParameters = {}
        self.workflowInputFiles = {}
        self.optionalParametersNotUsed = None
        self.workflowInputFilesBinding = {}
        self.confidenceValue = None
        self.diffs = []

        triggers = self.getTriggers(hypothesisName)
        trigger = TriggerSummary(self.provDocumentWrapper, triggers[0])

        self.arguments = {
            'dataSource': trigger.dataSource,
            'dataQueryVariables': self.dataQueryVariables,
            'dataQueryDelta': self.dataQueryDelta,
            'dataQueryDeltaLocations': self.dataQueryDeltaLocations,
            'numberSetsReturned': trigger.numberSetsReturned,
            'totalSets': trigger.totalNumberSets,
            'workflowName': trigger.workflowName,
            'workflowParameters': trigger.workflowParameters,
            'optionalParametersNotUsed': self.optionalParametersNotUsed,
            # Added by Maximiliano
            'questionVariables': self.questionVariables,
            'workflowInputFiles': trigger.workflowInputFilesBinding,
            'confidenceValue': trigger.confidenceValue,
            'diffs': self.diffs,
        }

        newTriggers = []
        for newTrigger in triggers[1:]:
            trigger = TriggerSummary(self.provDocumentWrapper, newTrigger)
            newTriggers.append(trigger)
            diff = {
                'numberSetsReturned': trigger.numberSetsReturned,
                'totalSets': trigger.totalNumberSets,
                'confidenceValue': trigger.confidenceValue,
                'generatedAtTime': trigger.generatedAtTime,
            }
            self.diffs.append(diff)
        self.text = self.render_template2('cohort.txt.jinja')

    def render_template2(self, template_name):
        template_dir = 'templates'
        template_loader = jinja2.FileSystemLoader(searchpath=template_dir)
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template(template_name)
        return template.render(self.arguments)

    def getTriggers(self, hypothesis_name):
        # Hypothesis
        hypothesis: ProvRecord = self.provDocumentWrapper.get_record(
            HYPOTHESIS_BUNDLE_IDENTIFIER, hypothesis_name)
        hypothesis_label: str = hypothesis.label
        # Hypothesis Variables
        hypothesisVariablesCollection: ProvRecord = self.provDocumentWrapper.get_record(
            HYPOTHESIS_BUNDLE_IDENTIFIER, HYPOTHESIS_VARIABLES_BINDING, hypothesis_name)
        hypothesisVariablesMembersId = self.provDocumentWrapper.get_records_associated(
            HYPOTHESIS_BUNDLE_IDENTIFIER, hypothesisVariablesCollection, PROV_MEMBERSHIP, True)
        # Question Entity
        questionMatch: ProvRecord = self.provDocumentWrapper.get_records_associated(
            QUESTION_BUNDLE_IDENTIFIER, hypothesis, PROV_DERIVATION, False)
        uniqueQuestionMatch = list(set(questionMatch))
        if len(uniqueQuestionMatch) == 0:
            raise Exception(
                'No question entity found for hypothesis: ' + str(hypothesis.identifier))
        if len(uniqueQuestionMatch) > 1:
            raise Exception(
                'Multiple question entities found for hypothesis: ' + str(hypothesis.identifier))
        questionEntity: ProvRecord = self.provDocumentWrapper.get_record(
            QUESTION_BUNDLE_IDENTIFIER, uniqueQuestionMatch[0].localpart)
        # Question Variables
        questionVariablesCollection: ProvRecord = self.provDocumentWrapper.get_record(
            QUESTION_BUNDLE_IDENTIFIER, QUESTION_VARIABLES_BINDING, questionEntity.identifier.localpart)
        questionVariablesMembersId = self.provDocumentWrapper.get_records_associated(
            QUESTION_BUNDLE_IDENTIFIER, questionVariablesCollection, PROV_MEMBERSHIP, True)

        # Trigger properties
        triggerLineOfInquiries: ProvRecord = self.provDocumentWrapper.get_records_by_type(
            TRIGGER_BUNDLE_IDENTIFIER, DISK_ONTOLOGY_TRIGGER_LINE_OF_INQUIRY)

        for hypothesisVariableId in hypothesisVariablesMembersId:
            hypothesisVariable: ProvRecord = self.provDocumentWrapper.get_record(
                HYPOTHESIS_BUNDLE_IDENTIFIER, hypothesisVariableId.localpart)
            hypothesisVariableLabel: str = hypothesisVariable.label
            questionVariableQualifiedName = self.provDocumentWrapper.get_records_associated(
                HYPOTHESIS_BUNDLE_IDENTIFIER, hypothesisVariable, PROV_DERIVATION, False)
            questionVariable: ProvRecord = self.provDocumentWrapper.get_record(
                QUESTION_BUNDLE_IDENTIFIER, questionVariableQualifiedName[0].localpart)
            questionVariableLabel: str = questionVariable.label
            self.questionVariables[questionVariableLabel] = hypothesisVariableLabel

        triggerLineOfInquiriesSorted = sortedByDate(triggerLineOfInquiries)
        if len(triggerLineOfInquiriesSorted) == 0:
            raise Exception('No trigger line of inquiry found')
        return triggerLineOfInquiriesSorted


def extra_attribute(entity, name):
    attribute_name = entity.extra_attributes[0][0].uri
    attribute_value = entity.extra_attributes[0][1]
    if attribute_name != name:
        logging.error('The attribute name is not ' +
                      name + ' but ' + attribute_name)
        system.exit(1)
    return attribute_value


def getDateEntities(entities):
    dateEntities = []
    for entity in entities:
        entityDate = extra_attribute(entity, PROV_GENERATED_AT_TIME)
        if entityDate is not None:
            dateEntities.append(entity)
    return dateEntities


def sortedByDate(triggers):
    sorted_triggers = {}
    for trigger in triggers:
        triggerDate = extra_attribute(trigger, PROV_GENERATED_AT_TIME)
        triggerDate = triggerDate.replace(tzinfo=None)
        triggerDate = triggerDate.replace(microsecond=0)
        sorted_triggers[triggerDate] = trigger
    sorted_list = sorted(sorted_triggers.items(),
                         key=lambda x: x[0], reverse=False)
    # map a list of tuples to a list of values
    sorted_list = list(map(lambda x: x[1], sorted_list))
    return sorted_list
