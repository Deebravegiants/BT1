# [M] M-10 | Migrations May Lock Other Markets

## Summary
Severity: Medium
Contest weight: 0.1635
Dataset id: 2582
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the V3 system all markets which are connected to a single pool affect each other’s creditCapacity with the amount of debt they report. This is because the totalVaultDebtsD18 is distributed evenly amongst all markets with the debtPerShareD18 and effectiveMaxShareValueD18 calculations in the rebalanceMarketsInPool function. This is the expected architecture of the V3 system, however when performing migrations this allows a large migration of debt to potentially lock other markets as their minimumCredit threshold can be broken. Normally healthy accounts will increase the delegated creditCapacity to other markets. However due to the minLiquidityRatio the creditCapacity that is allowed to be delegated to markets may actually be reduced after a migration. In the worst case the other markets will become locked as their creditCapacity goes below the minimumCredit.

## Proof of Concept
https://github.com/GuardianAudits/legacy-1/pull/new/202408_Add_MarketCreditCapacityEffectPoC

## Recommendation
On the engagement kickoff it was mentioned that the BFP market and Spot market would be attached to the spartan council pool during the migration, however consider keeping the Legacy Market attached to a pool all by itself to avoid locking other markets until the migration is completed. Otherwise consider validating that the migration does not put the pool in a capacity locked state, e.g. with the pool.findMarketWithCapacityLocked() function.
