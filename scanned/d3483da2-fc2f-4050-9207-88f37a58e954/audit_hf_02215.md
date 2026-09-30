# [H] Flawed Logic Of Holdefi::depositLiquidationReserve()

## Summary
Severity: High
Contest weight: 0.7840
Dataset id: 12254
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Holdefi protocol is designed to work with both ETH and ERC20 tokens. While all flows consider this aspect and treat the markets and collateral differently for ETH and ERC20 tokens, only the depositLiquidationReserveInternal() function is missing the differential treatment of ERC20 tokens.
```solidity
/// @notice Perform deposit liquidation reserve operation
function depositLiquidationReserveInternal(address collateral, uint256 amount)
    internal
    collateralIsActive(ethAddress)
{
    if (collateral == ethAddress)
        transferToHoldefi(address(holdefiCollaterals), collateral, amount);
    else
        transferFromHoldefi(address(holdefiCollaterals), collateral, amount);
    collateralAssets[ethAddress].totalLiquidatedCollateral =
        collateralAssets[ethAddress].totalLiquidatedCollateral.add(msg.value);
    emit LiquidationReserveDeposited(ethAddress, msg.value);
}
```
To elaborate, we show above the collateralIsActive() routine.
Apparently, only ethAddress collateral is considered for checks and msg.value is used. However, this function can be called by two callers, the first of which deposits ERC20 assets as liquidation reserve and the second deposits ETH assets, as shown below:
```solidity
/// @notice Deposit ERC20 asset as liquidation reserve
/// @param collateral Address of the given collateral
/// @param amount The amount that will be deposited
function depositLiquidationReserve(address collateral, uint256 amount)
    external
    isNotETHAddress(collateral)
{
    depositLiquidationReserveInternal(collateral, amount);
}

/// @notice Deposit ETH asset as liquidation reserve
/// @notice msg.value The amount of ETH that will be deposited
function depositLiquidationReserve()
    external
    payable
{
    depositLiquidationReserveInternal(ethAddress, msg.value);
}
```
It comes to our attention that the calls depositing ERC20 tokens as the liquidation reserve will revert because depositLiquidationReserveInternal() assumes only ETH deposits.

## Recommendation
No data
