# Variables

The generator identifies the available variables to use on your Narrative Template

## Question

Works with DISK system.

| Name                 | Description                    | Value |
| -------------------- | ------------------------------ | ----- |
| `question.text`      | The scientific question.       |
| `question.template`  | Template of the question       | `""`  |
| `question.variables` | Variables used on the question | `""`  |
| `question.notes`     | Notes about the question       | `""`  |

# Variables definition

| Name               | Description                       | Value |
| ------------------ | --------------------------------- | ----- |
| `variable.name`    | Name of the variable              | `""`  |
| `variable.type`    | Type of the variable              | `""`  |
| `variable.units`   | Units of the variable             | `""`  |
| `variable.source`  | Source of the variable            | `""`  |
| `variable.notes`   | Notes about the variable          | `""`  |
| `variable.value`   | Value of the variable             | `""`  |
| `variable.defined` | If the variable is defined or not | `""`  |

## Workflow

| Name                          | Description                                  | Value |
| ----------------------------- | -------------------------------------------- | ----- |
| `workflow.name`               | Name of the workflow                         | `""`  |
| `workflow.description`        | Description of the workflow                  | `""`  |
| `workflow.inputs`             | Workflow inputs (files)                      | `""`  |
| `workflow.outputs`            | Workflow outputs                             | `""`  |
| `workflow.parameters`         | Workflow parameters                          | `""`  |
| `workflow.annotations`        | Workflow annotations                         | `""`  |
| `workflow.confidenceValue`    | Confidence value of the workflow             | `""`  |
| `workflow.confidenceInterval` | Confidence interval of the workflow          | `""`  |
| `workflow.dataQuery`          | Data query used to obtain the workflow input | `""`  |

## Data set

| Name                  | Description                       | Value |
| --------------------- | --------------------------------- | ----- |
| `dataSet.name`        | Name of the data set              | `""`  |
| `dataSet.description` | Description of the data set       | `""`  |
| `dataSet.source`      | Source of the data set            | `""`  |
| `dataSet.variables`   | Variables used on the data set    | `""`  |
| `dataSet.notes`       | Notes about the data set          | `""`  |
| `dataSet.value`       | Value of the data set             | `""`  |
| `dataSet.defined`     | If the data set is defined or not | `""`  |

|
This document

## Data Query

| Name                          | Description                                            | Value |
| ----------------------------- | ------------------------------------------------------ | ----- |
| `dataQuery.text`              | The query send it to find the data sets                | `""`  |
| `dataQuery.description`       | A explanation of the query                             | `""`  |
| `dataQuery.source`            | The data source                                        | `""`  |
| `dataQuery.dataSetsReturned`  | The number of the datasets that match with the query   | `""`  |
| `dataQuery.dataSetsAvailable` | The number of the datasets available on the datasource | `""`  |

## Methods

| Name                            | Description             | Value |
| ------------------------------- | ----------------------- | ----- |
| `method.workflow[].name`        | Workflow name           | `""`  |
| `method.workflow[].parameters`  | Workflow parameters     | `""`  |
| `method.workflow[].inputs`      | Workflow inputs (files) | `""`  |
| `method.workflow[].outputs`     | Workflow outputs        |       |
| `method.workflow[].annotations` |                         | `""`  |

## Report

| Name                                    | Description                           | Value |
| --------------------------------------- | ------------------------------------- | ----- |
| `report.statisticalTests[].type `       | Type of the statistical test          |       |
| `report.statisticalTests[].description` | A description of the statistical test |       |
| `report.statisticalTests[].value`       | The value of the statistical test     |       |
