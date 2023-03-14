from provDocumentWrapper import ProvDocumentWrapper
from narrative import DataNarrative
from templateHandler import render_template

if __name__ == '__main__':
    hypothesisName = 'Hypothesis-geEzxPNJ9c8a'
    doc_path = "../DISK-OPMW-Mapper/examples/document.json"
    provDocumentWrapper = ProvDocumentWrapper(doc_path)
    dataNarrative = DataNarrative(provDocumentWrapper, hypothesisName)
    print(dataNarrative.text)
    #provDocumentWrapper.draw()


