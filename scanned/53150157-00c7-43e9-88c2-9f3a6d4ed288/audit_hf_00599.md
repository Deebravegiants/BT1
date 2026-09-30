# [H] H-07 | Delegators Cannot Cancel All Orders

## Summary
Severity: High
Contest weight: 0.1251
Dataset id: 2098
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Delegator.cancel() function allows delegators to cancel orders on behalf of the delegation's
owner. This works ﬁne for position orders, because LibOrderBook._cancelPositionOrder allows the
delegator to execute the certain action.
However, both _cancelLiquidityOrder and _cancelWithdrawalOrder require the msgSender (which is
the delegator) to be equal to the position owner, which will always revert for delegated calls.

## Recommendation
Add the isDelegator check to _cancelLiquidityOrder and _cancelWithdrawalOrder functions.
