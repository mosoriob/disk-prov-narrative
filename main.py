import argparse
from src.provDocumentWrapper import ProvDocumentWrapper
from src.narrative import DataNarrative


# Parse argument from command line
# -i {path_to_prov_document}
# -o {path_to_output_file}
# -h {hypothesis_name}
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Path to input file", required=True)
    parser.add_argument("-n", "--hypothesis", help="Hypothesis name", required=True)
    parser.add_argument("-o", "--output", help="Path to output file")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    arguments = parse_args()
    doc_path = arguments.input
    hypothesisName = arguments.hypothesis
    provDocumentWrapper = ProvDocumentWrapper(doc_path)
    dataNarrative = DataNarrative(provDocumentWrapper, hypothesisName)
    print(dataNarrative.text)
