# [M] M-26 | User Can’t Close Rebalanced Position

## Summary
Severity: Medium
Contest weight: 0.1256
Dataset id: 163
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol has specific logic to ensure that any user can fully close their position if the position is apart of the rebalancer. The logic is intended to ignore the min long position amount if the user is coming from the rebalancer and the close amount is the full amount from that user.
However, the check fails to take into account any change in the users position value. So when the rebalancer is in profit the close amount will be greater than the position amount used in the check and visa versa for when the rebalancer is at a loss.
Because of this users will not be able to close their position if any pnl is experienced and there is only a small amount of assets in the rebalancer. Given that the rebalancer is a long position that can face liquidation having only a small amount in it is a real possibility.

## Recommendation
When closing a position consider checking if the user is making a full close and if so, let the user bypass this check.
