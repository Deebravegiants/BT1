# [H] H-01 | Keeper's Not Remunerated For Cancellation Callback

## Summary
Severity: High
Contest weight: 0.0937
Dataset id: 21453
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The callback gas amount is included inside an order’s executionFee, however the payExecutionFee function will refund the not used part of executionFee to the user. Since this unused part includes callback gas, the keeper will not be remunerated for the gas spent during the cancellation callback.

## Recommendation
Change the places for order cancellation callback call and execution fee payment.
