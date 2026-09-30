# [M] M-05 | Orders Which Close Positions May Be Censored

## Summary
Severity: Medium
Contest weight: 0.1513
Dataset id: 21433
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If a decreaseOrder will close the position altogether, the autoCancelList will be cleared out during that order's execution. But gas provided by the keeper won't be checked if it is suﬃcient to handle the gas required for cancellations of these orders that are in autoCancelList. If keepers don't provide enough gas for all auto-cancellation logic, since the gas provided is not validated to cover these auto-cancellations with validateExecutionGas, a position closing order created by the user will be cancelled instead of reverting. This can lead to the censoring of closing orders for users and can lead to unfair liquidations and loss of funds.

## Recommendation
There are different possible solutions that comes with some caveats.
1- Query the position to see if order size is the entire position. If so, increase the result of estimateExecuteOrderGasLimit when the decrease order has auto cancel orders.
2- Before starting clearAutoCancelOrders() check if there is enough gas, if not revert such that order is not cancelled and the error is caught in the _handleOrderError function as a keeper mistake. Note that both of these ﬁrst two solutions has a grieﬁng vector whereby someone can frontrun the execution transaction and update an order to be an auto-cancel one such that the required gas for both will change. Which can lead to revert for keeper's execution error.
3- Separating the logic of auto cancellation from order execution. Emitting an event after position is completely closed and letting keepers to call clearAutoCancelOrders in a seperate transaction can solve the problem in a safer way, which will also address high gas usage concerns. The caveat for this is the execution logic change itself.
