# [M] Fee receiver does not get paid when collateral is liquidated

## Summary
Severity: Medium
Contest weight: 0.4429
Dataset id: 19845
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a position is liquidated, and there is enough collateral to cover the outstanding funding fee, the fee receiver does not get paid its fee. All of the remaining collateral is given to the pool, rather than paying the portion of position fees owed to the fee receiver.

Fee receiver does not get paid its share, which is instead given to the pool. The PnL funds are all given to the pool, and the _fees variable, which contains the fee receiver portion remains uninitialized.
```solidity
// File: gmx-synthetics/contracts/position/DecreasePositionCollateralUtils.sol : DecreasePositionCollateralUtils.getLiquidationValues()
} else {
    values.pnlAmountForPool = (params.position.collateralAmount() - fees.funding.fundingFeeAmount).toInt256();
}
PositionPricingUtils.PositionFees memory _fees;
PositionUtils.DecreasePositionCollateralValues memory _values = PositionUtils.DecreasePositionCollateralValues(
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
        0,
        address(0),
    )
);

return (_values, _fees);
}
```
cts/position/DecreasePositionCollateralUtils.sol#L342-L372

The empty fees are returned, and the function exits, skipping the paying of the fee receiver's portion of the position fees that are owed.

## Recommendation
Split the fees properly in getLiquidationValues() and don't return early after the call to getLiquidationValues()
