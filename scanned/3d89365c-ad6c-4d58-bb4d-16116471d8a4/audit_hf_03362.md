# [M] ORDH-5 | Gas Used Is Overestimated

## Summary
Severity: Medium
Contest weight: 0.0782
Dataset id: 18216
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When passing the startingGas to the this._executeOrder external call, it is assumed that all of the startingGas is available for the execution of the external call. However, due to the 63/64 rule, only 63/64 of the startingGas will be available in the subsequent call to this._executeOrder. Therefore when the executionFee is paid in the external call to this._executeOrder, the gas used will be overestimated, and the user will be errantly charged for a false 1/64 expenditure.

## Recommendation
Account for the 63/64 rule when estimating the gas consumption.
