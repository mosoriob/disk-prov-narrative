from typing import List
import jinja2
from prov.model import ProvDocument, ProvRecord, ProvBundle
from prov.dot import prov_to_dot
from prov.constants import PROV_MEMBERSHIP, PROV_DERIVATION, PROV_GENERATION
from termcolor import cprint

from constants import HYPOTHESIS_BUNDLE_IDENTIFIER, TRIGGER_BUNDLE_IDENTIFIER, QUESTION_BUNDLE_IDENTIFIER, HYPOTHESIS_VARIABLES_BINDING, QUESTION_VARIABLES_BINDING, META_WORKFLOW_VARIABLES_BINDING
from templateHandler import render_template


class DataNarrative:
    def __init__(self, provDocumentWrapper, hypothesisName):
        self.provDocumentWrapper = provDocumentWrapper
        # Variables values selected by the user
        self.questionVariables = None
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
        self.workflowParameters = None
        self.workflowVariables = None
        self.optionalParametersNotUsed = None
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
            'workflowValues': self.workflowVariables,
            'optionalParametersNotUsed': self.optionalParametersNotUsed,
            # Added by Maximiliano
            'questionVariables': self.questionVariables,
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
        triggerLineOfInquiryIdentifier = "http://disk-project.org/ontology/disk#TriggeredLineOfInquiry"
        triggerLineOfInquiries: ProvRecord = self.provDocumentWrapper.get_records_by_type(
            TRIGGER_BUNDLE_IDENTIFIER, triggerLineOfInquiryIdentifier)

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
            print(questionVariableLabel + ' = ' + hypothesisVariableLabel)

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

            # Get MetaWorkflow Bindings
            metaWorkflowBindingId = triggerLineOfInquiry.identifier.localpart + \
                '/' + META_WORKFLOW_VARIABLES_BINDING
            metaWorkflowBindings: ProvRecord = self.provDocumentWrapper.get_record(
                TRIGGER_BUNDLE_IDENTIFIER,  metaWorkflowBindingId)
            metaWorkflowBindingsMembersId = self.provDocumentWrapper.get_records_associated(
                TRIGGER_BUNDLE_IDENTIFIER, metaWorkflowBindings, PROV_MEMBERSHIP, True)

            cprint("The question was answered by the following data source: ",
                   None, attrs=['bold'])
            print(dataSourceLabel)

            cprint("The run is: ", None, attrs=['bold'])
            print(execution.label)

            cprint("The meta workflow bindings are: ", None, attrs=['bold'])
            for metaWorkflowBindingId in metaWorkflowBindingsMembersId:
                metaWorkflowBinding: ProvRecord = self.provDocumentWrapper.get_record(
                    TRIGGER_BUNDLE_IDENTIFIER, metaWorkflowBindingId.localpart)
                metaWorkflowBindingLabel: str = metaWorkflowBinding.value
                print(metaWorkflowBindingLabel)


def validate_values(values):
    # Loop through the values and check if they are valid
    for key, value in values.items():
        if value is None:
            print('The value for ' + key + ' is null')
