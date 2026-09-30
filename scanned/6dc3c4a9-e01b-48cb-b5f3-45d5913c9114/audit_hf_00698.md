# [H] H-01 | Liquidity Providers Can Control Markets

## Summary
Severity: High
Contest weight: 0.2593
Dataset id: 2249
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Liquidity providers can mintUsd and burnUsd without any restrictions with an atomic action which will rebalance collaterals for markets. The problem with these functions is that while it is rebalancing collaterals for markets, it doesn't validate if there is enough creditCapacity to back the markets after the action. Hence LPs can mintUsd such that market's creditCapacity will drop below their minimumCredit which in turn will lead to not executable orders. Since minting and burning are interest-free actions, liquidity providers can use this system to lock and unlock markets whenever they want. This can be used in several ways such as:
1. Risk free trades via preventing settleOrder calls by other keepers and only executing the order when it is proﬁtable
2. Preventing some order's execution while executing some other orders
Among many other things. With these vectors LP's can extract a signiﬁcant amount from the BFP market.

## Recommendation
Add _verifyNotCapacityLocked() to mintUsd() similar to how delegateCollateral() incorporates it so that LP's can't mint USD if it will invalidate market's minimumCredit checks. Additionally consider adding a buffer between the minimumCredit deﬁned by a market and the creditCapacity delegation mintUsd is allowed to leave markets at. This buffer would be useful as an LP would still be able to mintUsd up to the minimumCredit limit right before an order becomes executable to prevent it’s execution, which can also lead to risk free trades and extractable value.
