# [M] Liquidation is not executable when debt asset is collateral asset

## Summary
Severity: Medium
Contest weight: 0.4071
Dataset id: 5253
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In AAVE V3, a borrower can provide multiple assets as collateral and borrow these same assets. For example, a user may deposit 20 USDC and other assets to borrow 100 USDC. Then, a liquidator should be able to liquidate the position when passing the same asset as debt and collateral. However, the collateral asset and the debt asset are expected to be different in the liquidate function. It executes a swap which does not support having the same input and output assets. Such liquidation attempt will fail, the T::Router::sell call will return an Error::<T>::NotAllowed triggered from RouteExecutor::do_sell.
```solidity
fn do_sell(
    origin: T::RuntimeOrigin,
    asset_in: T::AssetId,
    asset_out: T::AssetId,
    amount_in: T::Balance,
    min_amount_out: T::Balance,
    route: Vec<Trade<T::AssetId>>,
) -> Result<(), DispatchError> {
    let who = ensure_signed(origin.clone())?;
    ensure!(asset_in != asset_out, Error::<T>::NotAllowed); // @POC: Debt can't be Collateral.
```

## Recommendation
The swap logic should not be executed when the debt asset is also the collateral asset.
