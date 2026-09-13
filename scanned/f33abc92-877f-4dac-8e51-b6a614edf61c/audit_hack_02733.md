# [M] M-02 The Keeper can Process Deposits while the Vault is Paused

## Summary
Severity: Medium
Reporter: GalloDaSballo
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L202-L203
Type: audit-issue

## Details
# M-02 The Keeper can Process Deposits while the Vault is Paused

## Summary

In contrast to other functions (deposit / withdraw) `processDeposits` can be executed while the Queue is paused.

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L202-L203

```solidity
    function processDeposits() external onlyVault {

```

It may be desireable to instead allow direct withdrawals or an emergency withdraw

## Vulnerability Detail

## Impact

If the system was paused, chances are the Vault may have an issue, instead of forcing a deposit into the vault to then allow a withdrawal, it may be best to find a way to allow withdrawals directly from the Queue.

## Code Snippet

## Tool used

Manual Review

## Recommendation

Consider a safer escape-hatch to handle issues with the Vault
