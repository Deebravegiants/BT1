# [C] C-02 | Liquidity Is Stuck After Epoch Is Settled

## Summary
Severity: Critical
Contest weight: 0.2178
Dataset id: 22060
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The only way to decrease liquidity of a position is through the decreaseLiquidityPosition function. This has a check epoch.validateEpochNotSettled which will revert if the epoch has settled. The settlePosition function is supposed to allow you to exit liquidity positions through a branch which calls _settleLiquidityPosition(). However, this calls the collect function in the NonFungiblePositionManager which will collect the tokens owed from fees and previous liquidity burns, but does not burn/decrease the liquidity still in the pool. The user may still get their collateral back, but does not get the value of their liquidity if it exceeds the loan value. It should be expected that the liquidity is worth than the loan value, since the LP positions are overcollateralized. When settling a liquidity position, consider ﬁrst burning all the liquidity and the calling collect.

## Recommendation
When settling a liquidity position, consider ﬁrst burning all the liquidity and then calling collect.
