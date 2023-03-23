from prov.model import ProvDocument, ProvRecord, ProvBundle
from prov.identifier import QualifiedName,  Identifier
from prov.dot import prov_to_dot
from prov.constants import PROV_MEMBERSHIP, PROV_DERIVATION, PROV_GENERATION
from termcolor import colored, cprint
import os
from src.constants import LOIS_BUNDLE_IDENTIFIER, HYPOTHESIS_BUNDLE_IDENTIFIER, TRIGGER_BUNDLE_IDENTIFIER, QUESTION_BUNDLE_IDENTIFIER, HYPOTHESIS_VARIABLES_BINDING, QUESTION_VARIABLES_BINDING, META_WORKFLOW_VARIABLES_BINDING


class ProvDocumentWrapper:
    # constructor
    def __init__(self, doc_path):
        self.doc = ProvDocument()
        self.doc_path = doc_path
        self.bundles = {}

        lois_bundle = None
        hypothesis_bundle = None
        trigger_bundle = None
        question_bundle = None

        bundles = {
            LOIS_BUNDLE_IDENTIFIER: lois_bundle,
            QUESTION_BUNDLE_IDENTIFIER: question_bundle,
            HYPOTHESIS_BUNDLE_IDENTIFIER: hypothesis_bundle,
            TRIGGER_BUNDLE_IDENTIFIER: trigger_bundle
        }
        self.load_document()

    def load_document(self):
        doc = ProvDocument()
        # read json file
        with open(self.doc_path, 'r') as f:
            self.doc = ProvDocument.deserialize(f, format='json')
        self.doc.get_provn()
        for bundle in self.doc.bundles:
            bundle_identifier = str(bundle.identifier.localpart)
            default_namespace = bundle.get_default_namespace()
            self.bundles[bundle_identifier] = bundle

    def get_record(self, bundle_identifier, name, parent=None):
        bundle: ProvBundle = self.bundles[bundle_identifier]
        default_namespace = bundle.get_default_namespace()
        if parent is not None:
            name = parent + '/' + name
        record_identifier = QualifiedName(default_namespace, name)
        if len(bundle.get_record(record_identifier)) == 0:
            raise Exception(
                'No record found for identifier: ' + str(record_identifier))
        record: ProvRecord = bundle.get_record(record_identifier)[0]
        return record

    def get_records_associated(self, bundle_identifier, withRecord, relationshipType, leftToRight=True):
        bundle: ProvBundle = self.bundles[bundle_identifier]
        default_namespace = bundle.get_default_namespace()
        records = []
        for record in bundle.get_records():
            if leftToRight:
                if record._prov_type == relationshipType and record.attributes[1][1] == withRecord.identifier:
                    records.append(record.attributes[0][1])
            else:
                if record._prov_type == relationshipType and record.attributes[0][1] == withRecord.identifier:
                    records.append(record.attributes[1][1])
        return records

    def get_records_by_type(self, bundle_identifier, record_type):
        bundle: ProvBundle = self.bundles[bundle_identifier]
        default_namespace = bundle.get_default_namespace()
        records = []
        # Create qualified name for rdf:type

        for record in bundle.get_records():
            if record.get_asserted_types():
                types = record.get_asserted_types()
                for prov_type in types:
                    if str(prov_type) == record_type:
                        records.append(record)
        return records

    def draw(self):
        print("Drawing prov document...")
        for key, item in self.bundles.items():
            figures_dir = os.path.join('examples', 'figures')
            if item is not None:
                dot = prov_to_dot(item)
                pdf_name = str(key) + '.pdf'
                path = os.path.join(figures_dir, pdf_name)
                dot.write_pdf(path)
