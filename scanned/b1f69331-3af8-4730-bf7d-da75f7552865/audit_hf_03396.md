# [H] MKTU-1 | Malicious Actor Can Break Markets

## Summary
Severity: High
Contest weight: 0.2062
Dataset id: 18504
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The uint poolValue is decreased by the impact pool value before the PnL is added to the poolValue.
Additionally, the impact pool value is not capped to avoid underflow.
Because of this, there are some cases where the market can be entirely bricked when the value of
the impact pool surpasses the value of the backing tokens — even if it was meant to offset a positive
pool PnL.
A malicious actor can engineer this outcome in certain scenarios, especially when the pool is initially
deployed.

## Proof of Concept
https://github.com/GuardianAudits/GMX-4/blob/033061d771f2b327c2fbd4ab59e960109ee85dc2/test/guardian/PoCs.ts#L327

## Recommendation
Consider moving the poolValue -= result.impactPoolAmount * indexTokenPrice.pickPrice(maximize);
line to after the PnL is added to the poolValue, as the impactPoolAmount is meant to offset initial
positive pnl. Otherwise, consider making the poolValue an int within the getPoolValueInfo function.
Additionally, consider capping the value of the impact pool (similarly to the capping of PnL) that is
subtracted from the poolValue to avoid any cases where the market is bricked.
