# [M] IF THE UNDERLYING ASSET IS A FEE ON TRANSFER TOKEN IT COULD BREAK THE INTERNAL ACCOUNTING OF THE VAULT

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-pooltogether
Published: 2023-07-14
Source: https://github.com/code-423n4/2023-07-pooltogether-findings/issues/470
Type: code-finding

## Details
# Lines of code

https://github.com/GenerationSoftware/pt-v5-vault/blob/b1deb5d494c25f885c34c83f014c8a855c5e2749/src/Vault.sol#L951-L956
https://github.com/GenerationSoftware/pt-v5-vault/blob/b1deb5d494c25f885c34c83f014c8a855c5e2749/src/Vault.sol#L959
https://github.com/GenerationSoftware/pt-v5-vault/blob/b1deb5d494c25f885c34c83f014c8a855c5e2749/src/Vault.sol#L1026-L1027


# Vulnerability details

## Impact
The `Vault._deposit` function is used by the users to deposit `_assets` to the vault and mint vault shares to the `recipient` address. The amount of `_assets` are transferred to the `Vault` as follows:

      SafeERC20.safeTransferFrom(
        _asset,
        _caller,
        address(this),
        _assetsDeposit != 0 ? _assetsDeposit : _assets
      );

The `Vault.deposit` function uses this `_assets` amount to calculate the number of `shares` to be minted to the `_recipient` address.

The issue here is if the underlying `_asset` is a fee on transfer token then the actual received amount to the vault will be less than what is referred in the `Vault.deposit` function `_assets` input parameter. But the shares to mint is calculated using the entire `_assets` amount.

This issue could be further aggravated since the `_asset` is again `deposited` to the `_yieldVault` and when needing to be redeemed will be `withdrawn` from the `_yieldVault` as well. These operations will again charge a fee if the `_asset` is a fee on transfer token. Hence the actual left `_asset` amount for particular user will be less than the amount he initially transferred in.

Hence when the user `redeems` the minted shares back to the `_assets`, the contract will not have enough assets to transfer to the `redeemer` thus reverting the transaction. 

## Proof of Concept

```solidity
      SafeERC20.safeTransferFrom(
        _asset,
        _caller,
        address(this),
        _assetsDeposit != 0 ? _assetsDeposit : _assets
      );
```


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-pooltogether-findings/issues/470_
