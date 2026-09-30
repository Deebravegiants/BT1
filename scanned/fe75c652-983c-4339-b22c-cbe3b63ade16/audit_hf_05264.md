# [M] CollateralLiquidityProvider AvailableLiquidity Miscalculation

## Summary
Severity: Medium
Contest weight: 0.0000
Dataset id: 23475
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Description: The CollateralLiquidityProvider::availableLiquidity function incorrectly returns the balance of the collateral asset held by the collateral provider, assuming a 1:1 ratio between the collateral asset and the liquidity tokens that will actually be provided to redeemers. This assumption is flawed because the actual liquidity supplied to redeemers goes through the externalCollateralRedemption.redeem() function, which may apply fees, exchange rates, or other conversion mechanisms that break the 1:1 assumption.

```solidity
function availableLiquidity() external view returns (uint256) {
    return IERC20(externalCollateralRedemption.asset()).balanceOf(collateralProvider);
}
function _availableLiquidity() private view returns (uint256) {
    return IERC20(externalCollateralRedemption.asset()).balanceOf(collateralProvider);
}
function supplyTo(
    address redeemer,
    uint256 amount,
    uint256 minOutputAmount
) public whenNotPaused onlySecuritizeRedemption {
    if (amount > _availableLiquidity()) {
        revert InsufficientLiquidity(amount, _availableLiquidity());
    }
    // ... collateral transfer and redemption logic ...
    // The actual liquidity provided is calculated here, not the raw collateral amount
    uint256 assetsAfterExternalCollateralRedemptionFee =
        externalCollateralRedemption.calculateLiquidityTokenAmount(,!
        amount
    );
    liquidityToken.transfer(redeemer, assetsAfterExternalCollateralRedemptionFee);
}
```

When CollateralLiquidityProvider::supplyTo is called, the flow involves: transferring collateral assets from the collateral provider, calling externalCollateralRedemption.redeem() to convert collateral to liquidity tokens, calculating the actual liquidity amount using externalCollateralRedemption.calculateLiquidityTokenAmount(), and finally transferring the calculated liquidity tokens to the redeemer.

The availableLiquidity() function should query the external redemption contract to determine the actual liquidity that can be provided, rather than using the raw collateral asset balance. (e.g. `externalCollateralRedemption.calculateLiquidityTokenAmount(IERC20(externalCollateralRedemption.asset()).balanceOf(collateralProvider)`)

Additionally, the external availableLiquidity() function duplicates the logic of the internal _availableLiquidity() function instead of calling it, which goes against the intended design pattern and creates unnecessary code duplication.

## Recommendation
Recommended Mitigation: Update the availableLiquidity() function to calculate the actual liquidity that can be provided by querying the external redemption contract, and fix the function to call the internal _availableLiquidity() function as intended:

```solidity
function availableLiquidity() external view returns (uint256) {
    // return IERC20(externalCollateralRedemption.asset()).balanceOf(collateralProvider);
    return _availableLiquidity();
}
function _availableLiquidity() private view returns (uint256) {
    // return IERC20(externalCollateralRedemption.asset()).balanceOf(collateralProvider);
    uint256 collateralBalance =
        IERC20(externalCollateralRedemption.asset()).balanceOf(collateralProvider);
    return externalCollateralRedemption.calculateLiquidityTokenAmount(collateralBalance);
}
```
