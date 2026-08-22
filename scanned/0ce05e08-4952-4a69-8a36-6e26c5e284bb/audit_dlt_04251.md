# [M] Marketplace's and Lender's batch functions performing delegatecalls are payable

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-illuminate
Published: 2022-11-10
Source: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/180
Type: sherlock-finding

## Details
hyh

medium

# Marketplace's and Lender's batch functions performing delegatecalls are payable

## Summary

`delegatecall` is used in the cycle in payable `batch` functions Marketplace and Lender have.

First of all, if any `msg.value` be attached to batch() call it will be lost.

On the other hand, if there be native funds usage in the future versions of these contracts and batch() will be migrated there, `msg.value` multiple reusage attack surface will open, i.e. it will be counted multiple times as `delegatecall` keeps it the same in all the instances within the loop.

## Vulnerability Detail

Although protocol do not use native funds, both Marketplace's and Lender's batch() are `payable`. This means any funds attached to the calls will be frozen on the contracts balance as there are no rescue function for the native funds either.

Also, there is a small chance of migrating batch() to the future versions of the Marketplace and Lender contracts that do use native funds. This will lead to massive double counting as `delegatecall` keeps `msg.value` the same within the loop.

## Impact

Native funds attached to the Marketplace's and Lender's batch() call will be lost.

If there be any future versions of the contracts that use `msg.value` a possibility of the massive native funds double counting be introduced.

Due to user mistake and low probability prerequisites correspondingly setting the severity to be medium.

## Code Snippet

Marketplace's batch():

https://github.com/sherlock-audit/2022-10-illuminate/blob/main/src/Marketplace.sol#L613-L628

```solidity
    /// @notice Allows batched call to self (this contract).
    /// @param c An array of inputs for each call.
    function batch(bytes[] calldata c)
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/180_
