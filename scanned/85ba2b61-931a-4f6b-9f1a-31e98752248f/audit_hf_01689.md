# [M] The borrower can be instantly liquidated

## Summary
Severity: Medium
Contest weight: 0.6035
Dataset id: 9238
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The IonPool.sol allows the creation of unsafe positions that can be liquidated instantly. When a user creates a position only basic position checks are performed:
```solidity
function _modifyPosition(
    // ---SNIP---
    uint256 newTotalDebtInVault = ilkRate * _vault.normalizedDebt;
    uint256 ilkSpot = $.ilks[ilkIndex].spot.getSpot();
    // vault is either less risky than before, or it is safe
    both(
        either(changeInNormalizedDebt > 0, changeInCollateral < 0),
        newTotalDebtInVault > _vault.collateral * ilkSpot
    ) revert UnsafePositionChange(newTotalDebtInVault, _vault.collateral, ilkSpot);
}
```
Compare it to verification in Liquidation.sol:
```solidity
function liquidate(
    // ---SNIP---
    uint256 collateralValue = (collateral * exchangeRate).rayMulDown(configs.liquidationThreshold);
    uint256 healthRatio = collateralValue.rayDivDown(normalizedDebt * rate); // round down in protocol favor
    if (healthRatio >= RAY) {
        revert VaultIsNotUnsafe(healthRatio);
    }
}
```
Notice, the additional value configs.liquidationThreshold. This discrepancy allows immediate liquidation of a position that was considered healthy when it was created.
Coded POC for Liquidation.t.sol:
```solidity
function test_InstaLiq() public {
    uint256 keeperInitialUnderlying = 100 ether;
    // calculating resulting state after liquidations
    DeploymentArgs memory dArgs;
    StateArgs memory sArgs;
    sArgs.collateral = 100e18; // [wad]
    sArgs.exchangeRate = 1e18; // [wad]
    sArgs.normalizedDebt = 50e18; // [wad]
    sArgs.rate = 1e27; // [ray]
    dArgs.liquidationThreshold = 0.5e27; // [ray]
    dArgs.targetHealth = 1.25e27; // [ray]
    dArgs.reserveFactor = 0.02e27; // [ray]
    dArgs.maxDiscount = 0.2e27; // [ray]
    dArgs.dust = 0; // [rad]
    Results memory results = calculateExpectedLiquidationResults(dArgs, sArgs);
    liquidation = new Liquidation(
        address(ionPool),
        protocol,
        exchangeRateOracles[0],
        dArgs.liquidationThreshold,
        dArgs.targetHealth,
        dArgs.reserveFactor,
        dArgs.maxDiscount
    );
    ionPool.grantRole(ionPool.LIQUIDATOR_ROLE(), address(liquidation));
    // set exchangeRate
    reserveOracle1.setExchangeRate(uint72(sArgs.exchangeRate));
    // create position
    borrow(borrower1, ILK_INDEX, 100 ether, 100 ether);
    // liquidate
    underlying.mint(keeper1, keeperInitialUnderlying);
    vm.startPrank(keeper1);
    underlying.approve(address(liquidation), keeperInitialUnderlying);
    liquidation.liquidate(ILK_INDEX, borrower1, keeper1);
    vm.stopPrank();
}
```

## Recommendation
Consider implementing the same position safety verification, as in Liquidation.sol, in _modifyPosition.
Ion Protocol comments
This does depend on the liquidationThreshold and the LTV (max LTV upon position creation) values being configured correctly.
Consider the following:
IonPool position creation enforces debtQuantity <= collateralQuantity * min(marketPrice, exchangeRate) * LTV
Liquidation is not possible if debtQuantity < collateralQuantity * exchangeRate * liquidationThreshold
As long as liquidationThreshold > LTV, then it is impossible for a position to be immediately liquidatable.
Looking at the two equations above, assuming liquidationThreshold > LTV, since min(marketPrice, exchangeRate) < exchangeRate, it is impossible for equation 2 to be true if 1 is true.
Acknowledged that this depends on correct parameters, will not fix.
