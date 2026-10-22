# [M] Positions can still be liquidated even if orders

## Summary
Severity: Medium
Contest weight: 0.4541
Dataset id: 19829
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Positions can still be liquidated even if orders to close positions or add collateral
can't execute, because liquidation does not transfer tokens
Liquidation orders do not transfer tokens - they just use the
increment*()/applyDelta*() functions to update the portions allotted to the various
parties. Orders to close positions, on the other hand, actually transfer the tokens
so if the transfer reverts, the position can't be closed. If the collateral token is
paused (e.g. USDC), a user won't be able to close their position, or add collateral to
it, in order to prevent it from being liquidated, but the liquidation keeper will be able
to liquidate without any issue.
Users will be liquidated without being able to prevent it
Liquidation doesn't actually transfer any funds - it just updates who got what:
```solidity
// File: gmx-synthetics/contracts/position/DecreasePositionCollateralUtils.sol :
DecreasePositionCollateralUtils.getLiquidationValues()
    } else {
        values.pnlAmountForPool = (params.position.collateralAmount()
        - fees.funding.fundingFeeAmount).toInt256();
    }
    PositionPricingUtils.PositionFees memory _fees;
    PositionUtils.DecreasePositionCollateralValues memory _values =
    PositionUtils.DecreasePositionCollateralValues(
        values.pnlTokenForPool,
        values.executionPrice, // executionPrice
        0, // remainingCollateralAmount
        values.positionPnlUsd, // positionPnlUsd
        values.pnlAmountForPool, // pnlAmountForPool
        0, // pnlAmountForUser
        values.sizeDeltaInTokens, // sizeDeltaInTokens
        values.priceImpactAmount, // priceImpactAmount
        0, // priceImpactDiffUsd
        0, // priceImpactDiffAmount
        PositionUtils.DecreasePositionCollateralValuesOutput(
            address(0),
```
And then increments/applies delta to the accounting.

## Recommendation
Keep user collateral at a separate address from the pool address, so that
liquidations have to do an actual transfer which may revert, rather than just
updating internal accounting
