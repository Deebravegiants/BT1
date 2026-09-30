# [H] The redeemDyad() Function Does Not Adjust Decimals Prop- erly

## Summary
Severity: High
Contest weight: 0.7517
Dataset id: 7612
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The redeemDyad() function can be called to burn up DYAD tokens to free up collateral, and then pay out that collateral to the owner.
```solidity
burnDyad(id, amount);
Vault _vault = Vault(vault);
uint asset = amount
* 10**_vault.oracle().decimals()
/ _vault.assetPrice();
withdraw(id, vault, asset, to);
```
The issue is that this only works for assets which are in 18 decimals. For assets like USDC (6 decimals) or WBTC (8 decimals), the math is incorrect since the decimals are not adjusted.

For example, let’s say a Chainlink oracle is used for a vault with USDC (6 decimals) and the price feed has 8 decimals. So the price feed returns 1e8. Say the amount of DYAD repaid = 100 dollars = 100e18, since the DYAD is in 18 decimals. Then asset is calculated as = 100e18 * 1e8 / 1e8 = 100e18 So 100e18 USDC is going to be removed instead of 100e6. This can lead to reverts, or unintentional collateral withdrawals which can lead to unintentional liqui-dations.

## Recommendation
Adjust with the asset decimals.
```solidity
function redeemDyad(
    uint id,
    address vault,
    uint amount,
    address to
) external isDNftOwner(id) returns (uint) {
    burnDyad(id, amount);
    Vault _vault = Vault(vault);
    uint asset = amount
    * (10**(_vault.oracle().decimals() + _vault.asset().decimals()))
    / _vault.assetPrice()
    / 1e18;
    withdraw(id, vault, asset, to);
    emit RedeemDyad(id, vault, amount, to);
    return asset;
}
```
