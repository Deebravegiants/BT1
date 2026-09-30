# [H] DPCU-3 | Unliquidatable Position Due to PriceImpactDiff

## Summary
Severity: High
Contest weight: 0.1863
Dataset id: 18516
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a position is liquidated with getLiquidationValues the pnlAmountForPool is set to
params.position.collateralAmount() - fees.funding.fundingFeeAmount.
However, this value does not account for the amount incremented for the claimable collateral with
incrementClaimableCollateralAmount in the event that the price impact is capped.
This will result in a revert since the claimableCollateralAmount is included in the
getExpectedMinTokenBalance. Therefore making a position unliquidatable when the price impact is
capped.

## Proof of Concept
https://github.com/GuardianAudits/GMX-4/blob/033061d771f2b327c2fbd4ab59e960109ee85dc2/test/guardian/PoCs.ts#L599

## Recommendation
Be sure to appropriately set aside the collateralCache.pnlDiffAmount in the cache.pnlToken when
liquidations enter the getLiquidationValues function.
