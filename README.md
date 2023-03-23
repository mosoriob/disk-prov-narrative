# PROV Narratives Generator

PROV Narratives generator is a Python project that generates human-readable narratives via PROV documents, explaining how a question or hypothesis was accepted or rejected by workflow executions. It is a useful tool for anyone looking to understand their workflow better.

### How Does It Work?

PROV Narratives generator takes a PROV document and a Data Narratives template as inputs. The PROV document contains the provenance information of workflow executions while the Data Narratives template specifies how the narratives should be generated based on the provenance information.

The generator uses the PROV document to extract relevant information about the workflow executions, such as the inputs, outputs, and activities involved. It then uses the Data Narratives template to generate human-readable narratives that explain how a question or hypothesis was accepted or rejected by the workflow executions.

The PROV Narratives generator identifies information by searching for the rdf:type in the PROV entities.

To use the PROV Narratives generator, you need to provide both a PROV document and a Data Narratives template. The generator will generate the narratives based on the specified template and the provenance information in the PROV document. [Learn more](docs/analyze-structure.md)

## Installation

To use this project, you need to have Python installed on your computer. You can download and install Python from the official website. After installing Python, you can clone this project from GitHub using the following command:

```
git clone <https://github.com/{username}/{repository}.git>

```

## Usage

To use the PROV Narratives generator, follow these steps:

1. Open the command prompt or terminal on your computer.
2. Navigate to the directory where the project was cloned.
3. Run the following command to install the required dependencies:

```
pip install -r requirements.txt

```

1. Once the dependencies are installed, run the following command to generate narratives:

```
python prov_narratives_generator.py -i {path_to_prov_document} -o {path_to_output_file}

```

Replace `{path_to_prov_document}` with the path to your PROV document, and `{path_to_output_file}` with the path to the output file where the narratives will be written.

## Contributing

If you want to contribute to this project, feel free to create a pull request with your changes. Please make sure to follow the guidelines in the [CONTRIBUTING.md](http://contributing.md/) file.

## License

This project is licensed under the MIT License - see the [LICENSE.md](http://license.md/) file for details.
