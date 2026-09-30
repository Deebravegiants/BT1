# [M] M-08 | MEV Bribes Allow Grieﬁng Of Keepers

## Summary
Severity: Medium
Contest weight: 0.1102
Dataset id: 21449
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
On Avalanche C-Chain a user can use providers such as flashbots or snowsight to set the gas price to the lowest acceptable gas price and still have their transaction executed via a bribe. Inside of validateExecutionFee(), the validation for the execution fee checks if execution fee is less than gasLimit * tx.gasprice. Setting a lower tx.gasprice will allow a user to pay less than the expected amount for an execution fee and force the keeper to draw on treasury reserves to subsidize the transaction. It may be possible for a malicious actor to submit many orders this way in order to grief the keepers. Or users may use this to pay less execution fees on the exchange consistently.

## Recommendation
Set a value for the lowest acceptable gas price, and verify that the value of tx.gasprice is greater than this value in validateExecutionFee().
