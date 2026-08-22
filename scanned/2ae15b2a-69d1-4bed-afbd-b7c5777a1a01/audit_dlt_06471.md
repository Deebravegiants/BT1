# [M] BBLiquidation::_updateBorrowAndCollateralShare Liquidator can avoid having his bonus reduced when position is close to bad-debt

## Summary
Severity: Medium
Chain: Smart contract
Component: Tapioca--Lending-Engine-
Published: 2024-06-03
Source: https://github.com/hats-finance/Tapioca--Lending-Engine--0x5bee198f5b060eecd86b299fdbea6b0c07c728dd/issues/14
Type: hats-finding

## Details
**Github username:** @CergyK
**Twitter username:** --
**Submission hash (on-chain):** 0x2cfe926149c7050450f63055e2978066a8d53d048aaf708ffe9e9b96eb5297a9
**Severity:** medium

**Description:**
**Description**: During the calculation of the computeLiquidationFactor, a condition is enforced on `collateralPartInAsset` and `borrowPartWithBonus`, to ensure that a liquidator cannot bypass the bad-debt which should be handled separately.
    The condition enforced is:
    https://github.com/hats-finance/Tapioca--Lending-Engine--0x5bee198f5b060eecd86b299fdbea6b0c07c728dd/blob/8920782db6044643fd0c682f58ef37f7e59f99b1/contracts/markets/bigBang/BBLiquidation.sol#L200

However this is insufficient to ensure that a liquidator passes a `maxBorrowAmount` big enough and that liquidation is handled under this condition:
    https://github.com/hats-finance/Tapioca--Lending-Engine--0x5bee198f5b060eecd86b299fdbea6b0c07c728dd/blob/8920782db6044643fd0c682f58ef37f7e59f99b1/contracts/markets/bigBang/BBLiquidation.sol#L220-L233

Indeed in the case where `collateralPartInAsset > userTotalBorrowAmount` but `collateralPartInAsset < userTotalBorrowAmount + liquidationBonus`, the liquidation bonus should be reduced (according to the above snippet).

To avoid this the liquidator can pass in a `maxBorrowAmount` such as `borrowPartWithBonus` is reduced here:
    https://github.com/hats-finance/Tapioca--Lending-Engine--0x5bee198f5b060eecd86b299fdbea6b0c07c728dd/blob/8920782db6044643fd0c682f58ef37f7e59f99b1/contracts/markets/bigBang/BBLiquidation.sol#L203

In that case the second condition is used:
    https://github.com/hats-finance/Tapioca--Lending-Engine--0x5bee198f5b060eecd86b299fdbea6b0c07c728dd/blob/8920782db6044643fd0c682f58ef37f7e59f99b1/contracts/markets/bigBang/BBLiquidation.sol#L234-L238

and the borrower receives a bigger share of the liquidation bonus, and can leave the protocol with pure bad-debt (uncollateralized debt).

## Attack scenario:
```markdown   

Params:
        - liquidationBonus = 10%

Scenario:
  - Alice has a position which has:
                `collateralPartInAsset = userTotalBorrowAmount + 1`

  - Bob liquidates the position, by using `maxBorrowAmount` == collateralPartInAsset / (1 + liquidationBonus), such as when liquidation bonus is added, `borrowPartWithBonus < collateralPartInAsset`.

  - Bob receives the full liquidation bonus, and all of the Alice's collateral is extracted out of the position. However 10% of Alice's debt remains unpaid, and is fully uncollateralized.
```
**Recommendation**:

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Tapioca--Lending-Engine--0x5bee198f5b060eecd86b299fdbea6b0c07c728dd/issues/14_
