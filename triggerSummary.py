import logging
from os import system
from typing import List
from typing import List
from prov.model import ProvRecord
from prov.constants import PROV_MEMBERSHIP, PROV_DERIVATION, PROV_GENERATION

from constants import DISK_ONTOLOGY_CONFIDENCE_REPORT, DISK_ONTOLOGY_CONFIDENCE_REPORT_LOCALNAME, DISK_ONTOLOGY_TRIGGER_LINE_OF_INQUIRY, HYPOTHESIS_BUNDLE_IDENTIFIER, META_WORKFLOW_INPUT_FILE_BINDING, PROV_GENERATED_AT_TIME, TRIGGER_BUNDLE_IDENTIFIER, QUESTION_BUNDLE_IDENTIFIER, HYPOTHESIS_VARIABLES_BINDING, QUESTION_VARIABLES_BINDING, META_WORKFLOW_VARIABLES_BINDING


class TriggerSummary:

    def __init__(self, provDocumentWrapper, trigger) -> None:
        self.provDocumentWrapper = provDocumentWrapper
        self.dataQueryDelta = None
        self.numberSetsReturned = None
        self.totalNumberSets = None
        self.workflowName = None
        self.workflowParameters = {}
        self.workflowInputFiles = {}
        self.optionalParametersNotUsed = None
        self.workflowInputFilesBinding = {}
        self.confidenceValue = None
        self.generatedAtTime = None

        dataSource: ProvRecord = self.provDocumentWrapper.get_record(
            TRIGGER_BUNDLE_IDENTIFIER, 'dataSource')
        dataSourceLabel: str = dataSource.label
        # Get execution
        createRunActivity = self.provDocumentWrapper.get_record(
            TRIGGER_BUNDLE_IDENTIFIER, 'createRun')
        executionQualifiedName: ProvRecord = self.provDocumentWrapper.get_records_associated(
            TRIGGER_BUNDLE_IDENTIFIER, createRunActivity, PROV_GENERATION, True)[0]
        execution: ProvRecord = self.provDocumentWrapper.get_record(
            TRIGGER_BUNDLE_IDENTIFIER, executionQualifiedName.localpart)
        # Get MetaWorkflow Variables Bindings
        metaWorkflowBindingId = trigger.identifier.localpart + \
            '/' + META_WORKFLOW_VARIABLES_BINDING
        metaWorkflowBindings: ProvRecord = self.provDocumentWrapper.get_record(
            TRIGGER_BUNDLE_IDENTIFIER,  metaWorkflowBindingId)
        metaWorkflowBindingsMembersId = self.provDocumentWrapper.get_records_associated(
            TRIGGER_BUNDLE_IDENTIFIER, metaWorkflowBindings, PROV_MEMBERSHIP, True)
        # Get MetaWorkflow InputFile Bindings
        metaWorkflowInputFileBindingId = trigger.identifier.localpart + \
            '/' + META_WORKFLOW_INPUT_FILE_BINDING
        metaWorkflowInputFileBindings: ProvRecord = self.provDocumentWrapper.get_record(
            TRIGGER_BUNDLE_IDENTIFIER,  metaWorkflowInputFileBindingId)
        metaWorkflowInputFileBindingsMembersId = self.provDocumentWrapper.get_records_associated(
            TRIGGER_BUNDLE_IDENTIFIER, metaWorkflowInputFileBindings, PROV_MEMBERSHIP, True)
        # Get confidence value
        confidenceValueId = trigger.identifier.localpart + \
            '/' + DISK_ONTOLOGY_CONFIDENCE_REPORT_LOCALNAME
        confidenceValue = self.provDocumentWrapper.get_record(
            TRIGGER_BUNDLE_IDENTIFIER, confidenceValueId)
        self.confidenceValue = list(confidenceValue.value)
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
        self.generatedAtTime = getGenerateAtTime(trigger)


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


def extra_attribute(entity, name):
    attribute_name = entity.extra_attributes[0][0].uri
    attribute_value = entity.extra_attributes[0][1]
    if attribute_name != name:
        logging.error('The attribute name is not ' +
                      name + ' but ' + attribute_name)
        system.exit(1)
    return attribute_value


def getGenerateAtTime(entity):
    return extra_attribute(entity, PROV_GENERATED_AT_TIME)


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
