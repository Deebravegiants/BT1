# [M] executeBatchDeposit() will revert under certain conditions

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-rage-trade
Published: 2022-11-28
Source: https://github.com/sherlock-audit/2022-10-rage-trade-judging/issues/86
Type: sherlock-finding

## Details
0x52

RageTrade (found by protocol team after contest)

medium

## Summary

DnGmxBatchingManager.executeBatchDeposit() will always revert if _convertAUsdcToAsset is called within DnGmxJuniorVault.deposit sub call because it will again call DnGmxBatchingManager.depositToken() and this will revert due to glp 15 mins cooldown

## Vulnerability Detail

## Impact

DnGmxBatchingManager.executeBatchDeposit() will revert under certain conditions 

## Code Snippet

## Tool used

## Recommendation

Fixed in [PR#43](https://github.com/RageTrade/delta-neutral-gmx-vaults/pull/43)
