# [C] C-03 | Callback Check Bypassed Via Self Liquidation

## Summary
Severity: Critical
Contest weight: 0.2375
Dataset id: 21956
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
GMX allows users to set their callback contract in case of liquidation through the
setSavedCallbackContract function.
function setSavedCallbackContract(address market,address callbackContract) external payable
nonReentrant
This feature can be leveraged to bypass the validCallback function because the order is a liquidation
which GMXUtils will not prevent.
An attacker would do so by executing the following attack:
• Attacker will set the callback contract to GMXUtils
• Open small highly leveraged position
• Attacker gets liquidated and the GMXUtils contracts afterOrderExecution will be called
• queue will be deleted, removing the pending order.
• PerpetualVault contracts afterOrderExecution will then be called and all conditionals will be skipped
leaving the protocol in a ﬂow state
• Protocol is bricked as it is stuck in a ﬂow state, and no pending deposits/withdrawals.
The result of this attack would be DoS of the protocol as well as a lost order from the deleted queue.

## Recommendation
Validate that the liquidation is for the vault positionKey rather than any arbitrary position in the
validCallback modiﬁer.
