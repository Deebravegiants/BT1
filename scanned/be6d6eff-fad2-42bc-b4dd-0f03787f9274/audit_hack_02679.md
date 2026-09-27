# [M] `VaultAdmin.initializeEpoch()` might revert with some weird ERC20 tokens.

## Summary
Severity: Medium
Reporter: hansfriese
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L234
Type: audit-issue

## Details
# `VaultAdmin.initializeEpoch()` might revert with some weird ERC20 tokens.

## Summary
`VaultAdmin.initializeEpoch()` might revert with some weird ERC20 tokens.

## Vulnerability Detail
`VaultAdmin.initializeEpoch()` might revert with some weird ERC20 tokens.

Currently, [VaultAdmin.initializeEpoch()](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L234) calls [_collectPerformanceFee()](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L504) to collect the performance fees for the epoch.

In the `_collectPerformanceFee()`, it calculates `feeInCollateral` only for the positive net income and transfers to recipient [here](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L515-L526).

```solidity
if (adjustedTotalAssets > l.lastTotalAssets) {
    // collect performance fee ONLY if the vault returns a positive net income
    // if the net income is negative, last week's option expired ITM past breakeven,
    // and the vault took a loss so we do not collect performance fee for last week
    netIncome = adjustedTotalAssets - l.lastTotalAssets;

    // calculate the performance fee denominated in the collateral asset
    feeInCollateral = l.performanceFee64x64.mulu(netIncome);

    // send collected fee to recipient wallet
    ERC20.safeTransfer(l.feeRecipient, feeInCollateral);
}
```
But when the admin sets `performanceFee64x64` [here](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L160), there is no requirement of `performanceFee64x64 > 0` and `feeInCollateral` might be 0 in this case.

Even if `performanceFee64x64 > 0`, we can assume it's possible `feeInCollateral == 0` for low fee percent and small net income.

As we can see [here](https://github.com/d-xo/weird-erc20#revert-on-zero-value-transfers), some tokens don't allow to transfer 0 amount.

So with such weird ERC20 token, [this transfer](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L525) will revert when `feeInCollateral == 0`.

As a result, it would be impossible to create a new auction [here](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L234).

## Impact
It might be impossible to create a new auction for some cases.

## Code Snippet
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L525

## Tool used
Manual Review

## Recommendation
We should check if `feeInCollateral > 0` before tranfer [here](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L525).

```solidity
if (feeInCollateral > 0) {
    ERC20.safeTransfer(l.feeRecipient, feeInCollateral);
}
```
