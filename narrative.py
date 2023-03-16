import json
import logging
from os import system
import re
from typing import List
import jinja2
from prov.model import ProvDocument, ProvRecord, ProvBundle
from prov.dot import prov_to_dot
from prov.constants import PROV_MEMBERSHIP, PROV_DERIVATION, PROV_GENERATION
from termcolor import cprint

from constants import DISK_ONTOLOGY_CONFIDENCE_REPORT, DISK_ONTOLOGY_CONFIDENCE_REPORT_LOCALNAME, DISK_ONTOLOGY_TRIGGER_LINE_OF_INQUIRY, HYPOTHESIS_BUNDLE_IDENTIFIER, META_WORKFLOW_INPUT_FILE_BINDING, TRIGGER_BUNDLE_IDENTIFIER, QUESTION_BUNDLE_IDENTIFIER, HYPOTHESIS_VARIABLES_BINDING, QUESTION_VARIABLES_BINDING, META_WORKFLOW_VARIABLES_BINDING
from templateHandler import render_template


class DataNarrative:
    def __init__(self, provDocumentWrapper, hypothesisName):
        self.provDocumentWrapper = provDocumentWrapper
        # Variables values selected by the user
        self.questionVariables = {}
        # Variables values found by the data query
        self.dataQueryVariables: List = None
        # The data source used to find the data
        self.dataSource = None
        # ????????
        self.dataQueryDeltaLocations = None
        # ????????
        self.dataQueryDelta = None
        self.fileFormat = None
        self.numberSetsReturned = None
        self.totalNumberSets = None
        self.workflowName = None
        self.workflowParameters = {}
        self.workflowInputFiles = {}
        self.optionalParametersNotUsed = None
        self.workflowInputFilesBinding = {}
        self.confidenceValue = None
        self.create_hypotheses_narrative(hypothesisName)

        self.arguments = {
            'dataSource': self.dataSource,
            'dataQueryVariables': self.dataQueryVariables,
            'dataQueryDelta': self.dataQueryDelta,
            'dataQueryDeltaLocations': self.dataQueryDeltaLocations,
            'numberSetsReturned': self.numberSetsReturned,
            'fileFormat': self.fileFormat,
            'totalSets': self.totalNumberSets,
            'workflowName': self.workflowName,
            'workflowParameters': self.workflowParameters,
            'optionalParametersNotUsed': self.optionalParametersNotUsed,
            # Added by Maximiliano
            'questionVariables': self.questionVariables,
            'workflowInputFiles': self.workflowInputFilesBinding,
            'confidenceValue': self.confidenceValue,
        }
        validate_values(self.arguments)
        self.text = self.render_template2('cohort.txt.jinja')

    def render_template2(self, template_name):
        template_dir = 'templates'
        template_loader = jinja2.FileSystemLoader(searchpath=template_dir)
        template_env = jinja2.Environment(loader=template_loader)
        templates = template_env.list_templates()
        template = template_env.get_template(template_name)
        return template.render(**self.arguments)

    def create_narrative(self):
        # Hypothesis
        hypothesis_name = 'hypothesis1'
        self.create_hypotheses_narrative(hypothesis_name)

    def create_hypotheses_narrative(self, hypothesis_name):
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
        if len(questionMatch) == 0:
            raise Exception(
                'No question entity found for hypothesis: ' + str(hypothesis.identifier))
        if len(questionMatch) > 1:
            raise Exception(
                'Multiple question entities found for hypothesis: ' + str(hypothesis.identifier))
        questionEntity: ProvRecord = self.provDocumentWrapper.get_record(
            QUESTION_BUNDLE_IDENTIFIER, questionMatch[0].localpart)
        # Question Variables
        questionVariablesCollection: ProvRecord = self.provDocumentWrapper.get_record(
            QUESTION_BUNDLE_IDENTIFIER, QUESTION_VARIABLES_BINDING, questionEntity.identifier.localpart)
        questionVariablesMembersId = self.provDocumentWrapper.get_records_associated(
            QUESTION_BUNDLE_IDENTIFIER, questionVariablesCollection, PROV_MEMBERSHIP, True)

        # Trigger properties
        triggerLineOfInquiries: ProvRecord = self.provDocumentWrapper.get_records_by_type(
            TRIGGER_BUNDLE_IDENTIFIER, DISK_ONTOLOGY_TRIGGER_LINE_OF_INQUIRY)

        cprint("The user selects a question template: ", None, attrs=['bold'])
        print(questionEntity.label)

        cprint("The user selects the following values to fill the question template: ",
               None, attrs=['bold'])
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

        cprint("The question to be answered is: ", None, attrs=['bold'])
        print(hypothesis_label)
        for triggerLineOfInquiry in triggerLineOfInquiries:
            cprint("The trigger line of inquiry is: ", None, attrs=['bold'])
            print(triggerLineOfInquiry.label)

            dataQuery: ProvRecord = self.provDocumentWrapper.get_record(
                TRIGGER_BUNDLE_IDENTIFIER, 'dataQuery')
            dataSource: ProvRecord = self.provDocumentWrapper.get_record(
                TRIGGER_BUNDLE_IDENTIFIER, 'dataSource')
            dataQueryLabel: str = dataQuery.label.replace(
                '\\n', '\n').replace('\\t', '\t')
            dataSourceLabel: str = dataSource.label

            # Get execution
            createRunActivity = self.provDocumentWrapper.get_record(
                TRIGGER_BUNDLE_IDENTIFIER, 'createRun')
            executionQualifiedName: ProvRecord = self.provDocumentWrapper.get_records_associated(
                TRIGGER_BUNDLE_IDENTIFIER, createRunActivity, PROV_GENERATION, True)[0]
            execution: ProvRecord = self.provDocumentWrapper.get_record(
                TRIGGER_BUNDLE_IDENTIFIER, executionQualifiedName.localpart)

            # Get MetaWorkflow Variables Bindings
            metaWorkflowBindingId = triggerLineOfInquiry.identifier.localpart + \
                '/' + META_WORKFLOW_VARIABLES_BINDING
            metaWorkflowBindings: ProvRecord = self.provDocumentWrapper.get_record(
                TRIGGER_BUNDLE_IDENTIFIER,  metaWorkflowBindingId)
            metaWorkflowBindingsMembersId = self.provDocumentWrapper.get_records_associated(
                TRIGGER_BUNDLE_IDENTIFIER, metaWorkflowBindings, PROV_MEMBERSHIP, True)

            # Get MetaWorkflow InputFile Bindings
            metaWorkflowInputFileBindingId = triggerLineOfInquiry.identifier.localpart + \
                '/' + META_WORKFLOW_INPUT_FILE_BINDING
            metaWorkflowInputFileBindings: ProvRecord = self.provDocumentWrapper.get_record(
                TRIGGER_BUNDLE_IDENTIFIER,  metaWorkflowInputFileBindingId)
            metaWorkflowInputFileBindingsMembersId = self.provDocumentWrapper.get_records_associated(
                TRIGGER_BUNDLE_IDENTIFIER, metaWorkflowInputFileBindings, PROV_MEMBERSHIP, True)

            # Get confidence value
            confidenceValueId = triggerLineOfInquiry.identifier.localpart + \
                '/' + DISK_ONTOLOGY_CONFIDENCE_REPORT_LOCALNAME
            confidenceValue = self.provDocumentWrapper.get_record(
                TRIGGER_BUNDLE_IDENTIFIER, confidenceValueId)
            self.confidenceValue = list(confidenceValue.value)

            # Print the data query
            cprint("The question was answered by the following data source: ",
                   None, attrs=['bold'])
            print(dataSourceLabel)

            cprint("The run is: ", None, attrs=['bold'])
            print(execution.label)

            for metaWorkflowInputFileBindingId in metaWorkflowInputFileBindingsMembersId:
                metaWorkflowInputFileBinding: ProvRecord = self.provDocumentWrapper.get_record(
                    TRIGGER_BUNDLE_IDENTIFIER, metaWorkflowInputFileBindingId.localpart)
                value: str = metaWorkflowInputFileBinding.value
                label: str = metaWorkflowInputFileBinding.label
                value = handle_set(value)
                new_label = label.split('#')[-1]
                self.workflowInputFiles[new_label] = value
            self.numberSetsReturned = find_file_extension_by_string(
                self.workflowInputFiles)

            cprint("The meta workflow bindings are: ", None, attrs=['bold'])
            for metaWorkflowBindingId in metaWorkflowBindingsMembersId:
                metaWorkflowBinding: ProvRecord = self.provDocumentWrapper.get_record(
                    TRIGGER_BUNDLE_IDENTIFIER, metaWorkflowBindingId.localpart)
                value: str = metaWorkflowBinding.value
                label: str = metaWorkflowBinding.label
                value = handle_set(value)

                if len(value) > 0:
                    if value[0] not in self.workflowInputFiles:
                        self.workflowParameters[label] = value
                    else:
                        self.workflowInputFilesBinding[label] = value

        self.dataSource = dataSourceLabel


def validate_values(values):
    # Loop through the values and check if they are valid
    for key, value in values.items():
        if value is None:
            logging.warning('The value for ' + key + ' is null')


def handle_set(data: set):
    value_list = None
    # convert set to list
    try:
        value_list = list(data)[0]
    except:
        logging.error("Unable to convert the set to list: " + str(data))
        system.exit(1)

    try:
        # remove the first and last character
        if value_list.startswith('['):
            value_list = value_list[1:]
        if value_list.endswith(']'):
            value_list = value_list[:-1]
        values = value_list.split(', ')
    except:
        logging.error("Unable to split the value: " + value_list)
        system.exit(1)
    return values


def find_file_extension_by_string(filenames: List[str]):
    # Find the file extension
    file_extension_counter = {}
    for filename in filenames:
        file_extension = filename.split('.')[-1]
        if file_extension in file_extension_counter:
            file_extension_counter[file_extension] += 1
        else:
            file_extension_counter[file_extension] = 1
    return file_extension_counter
