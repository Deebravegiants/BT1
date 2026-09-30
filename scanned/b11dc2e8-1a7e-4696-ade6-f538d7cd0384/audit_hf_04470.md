# [M] M-12 | Oracle Price Counts Ignored In Gas Estimation

## Summary
Severity: Medium
Contest weight: 0.0885
Dataset id: 21966
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the GMxUtils contract, when creating orders for GMX the Oracle price count is not accounted for when determining the size of the executionFee. However in GMX V2.1 an additional amount of executionFee is necessary to account for the number of oracle prices to execute the order. This logic is seen here: [https://github.com/gmx-io/gmx-synthetics/blob/1938e365dc009342aa288aa6b42fc1fd3cd9e45d/contracts/gas/GasUtils.sol#L212](https://github.com/gmx-io/gmx-synthetics/blob/1938e365dc009342aa288aa6b42fc1fd3cd9e45d/contracts/gas/GasUtils.sol#L212)

## Recommendation
Include the oracle price count estimated costs in the execution fee sent to GMX.
