# [M] Withdrawal fee receiver can DoS withdrawals

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-knox
Published: 2022-10-18
Source: https://github.com/sherlock-audit/2022-09-knox-judging/issues/133
Type: sherlock-finding

## Details
berndartmueller

medium

# Withdrawal fee receiver can DoS withdrawals

## Summary

The withdrawal fee receiver can DoS withdrawals by reverting the `POOL` token transfer within the `onERC1155Received` transfer hook.

## Vulnerability Detail

Withdrawal fees are transferred to the fee `receiver` in the `VaultInternal._withdraw` function. Internally, this function calls the `VaultInternal._collectWithdrawalFee` function. Then within this function, the `VaultInternal._transferCollateralAndShortAssets` function is called.

Fees are then transferred by using `Pool.safeTransferFrom`. `POOL` itself is an `ERC1155` token, hence, due to using the `safeTransferFrom` function, the `onERC1155Received` hook is called on the `receiver`. If the `receiver` is a smart contract, it is therefore possible to revert the transfer and prevent withdrawals.

## Impact

The withdrawal fee receiver can prevent withdrawals.

## Code Snippet

[vault/VaultInternal.\_withdraw](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L277)

```solidity
function _withdraw(
    address caller,
    address receiver,
    address owner,
    uint256 assetAmount,
    uint256 shareAmount
) private {
    [..]

    // calculate the collateral amount and short contract amount distribution
    (uint256 collateralAmount, uint256 shortContracts) =
        _calculateDistributions(l, assetAmount);

```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-09-knox-judging/issues/133_
