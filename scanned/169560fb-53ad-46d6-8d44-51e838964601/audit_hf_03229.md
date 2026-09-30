# [C] MKTU-1 | Unliquidateable Short With Long Collateral

## Summary
Severity: Critical
Contest weight: 0.1661
Dataset id: 17848
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
It is possible for user to create unliquidateable short positions with long collateral because when computing the openInterestWithPnL the Calc.sum operation underflows and reverts when the PnL is negative with magnitude greater than the open interest of the pool. When a pool reaches this state, it is impossible to increase or decrease any positions within the pool, as the openInterestWithPnL is calculated during both actions.

## Proof of Concept
https://github.com/GuardianAudits/GMX_2/blob/98d8c7dfe47f58e9c0b2efe74575795e928e5643/test/guardian/PoCs.ts#L1213

## Recommendation
Do not allow shorts to be able to lose more than the open interest in the pool or rectify these outstanding losses somehow.
