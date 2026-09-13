# [M] `processDeposits()` reverts for second epoch if Vault uses `USDT` as collateral

## Summary
Severity: Medium
Reporter: joestakey
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L204
Type: audit-issue

## Details
# `processDeposits()` reverts for second epoch if Vault uses `USDT` as collateral

## Summary
`processDeposits()` reverts for second epoch if Vault uses `USDT` as collateral due to the way `USDT` handles `approve()`.

## Vulnerability Detail
When using the approval mechanism in `USDT`, the approval must be set to 0 before it is updated.
In `Queue.processDeposits`, `ERC20.approve` is called with `amount = deposits`, meaning it is not set to 0.
This means the function will only work for the 1st epoch and break afterwards.

See the following example:

1 - epoch 1, Friday 8AM: the `Keeper` calls `Vault.InitializeEpoch()`, which in turns calls `Queue.processDeposits` to transfer all of the collateral held in `Queue` to `Vault`.
In `Queue.processDeposits`, the function approves the `Vault` to transfer the `USDT` deposits:
```solidity
204:        ERC20.approve(address(Vault), deposits);
```

2 - epoch 2, Friday 8AM: the `Keeper` calls `Vault.InitializeEpoch()`, which in turns calls `Queue.processDeposits`.
But this time in `Queue.processDeposits`, the `approve` function reverts, because the current approval is a non-zero value.

## Impact
`Vault` receives collateral only during the first epoch, meaning this essentially breaks the functionality of the protocol, because the vault will not have the funds to underwrite the options sold during auctions.

## Code Snippet
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L204

## Tool used
Manual Review

## Recommendation
Set the allowance to 0 before setting it to the new value.

```diff
+           ERC20.approve(address(Vault), 0);
204:        ERC20.approve(address(Vault), deposits);
```
