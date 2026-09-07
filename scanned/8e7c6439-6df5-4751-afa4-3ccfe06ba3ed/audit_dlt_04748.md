# [M] `setDelta64x64()` and `setDeltaOffset64x64()` need sanity check

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-knox
Published: 2022-10-18
Source: https://github.com/sherlock-audit/2022-09-knox-judging/issues/90
Type: sherlock-finding

## Details
__141345__

medium

# `setDelta64x64()` and `setDeltaOffset64x64()` need sanity check

## Summary

When `_setAuctionPrices()`, if `l.delta64x64` is less than `l.deltaOffset64x64`, the function will revert, and epoch initialization will fail. Users fund in the vault will not work and effectively lose yield.


## Vulnerability Detail

If a new `l.delta64x64` is less than `l.deltaOffset64x64`, the `_setAuctionPrices()` function in epoch initialization will revert, new auction will not be performed.

## Impact

Epoch could fail to be initialized, new auction can not take place. User fund will stop working and users lose the yield.



## Code Snippet

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L64-L72

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L77-L93

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L572-L577

## Tool used

Manual Review


## Recommendation

In `setDelta64x64()` and `setDeltaOffset64x64()`, check that the new delta value is bigger than the offset delta.


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-09-knox-judging/issues/90_
