# [M] M-03 | Callback Gas Validation Ignores 63/64 Rule

## Summary
Severity: Medium
Contest weight: 0.0612
Dataset id: 21431
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
validateGasLeftForCallback() veriﬁes that the gas left in the transaction is enough to call the callback contract. However, validateGasLeftForCallback() checks gasLeft() and forgets to account that 1/64th of the gas is reserved when making an external call. Although this case is less likely to occur, it has the same impact as H-06.

## Recommendation
Verify that the gasLeft() subtracted by the gas withheld from making an external call is greater than the callback gas limit.
