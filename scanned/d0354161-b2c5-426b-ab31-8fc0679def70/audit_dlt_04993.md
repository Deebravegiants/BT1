# [M] Denial of Service on Batching Manager

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-rage-trade
Published: 2022-11-25
Source: https://github.com/sherlock-audit/2022-10-rage-trade-judging/issues/85
Type: sherlock-finding

## Details
0x52

RageTrade (found by protocol team after contest)

medium

# Denial of Service on Batching Manager

## Summary

In case there is significant amount (like $1M) of USDC deposited into Batching Manager then after conversion of usdc into sGLP would work fine (executeBatchStake) but from sGLP to shares (executeBatchDeposit) would fail due to slippage tolerance checks. This would lead to batching manager being stuck in this state since batch deposit cannot go through and users would not be able to withdraw the sGLP. 

## Vulnerability Detail

## Impact

Users would not be able to withdraw the sGLP from the Batching Manager. 

## Code Snippet

https://github.com/sherlock-audit/2022-10-rage-trade/blob/main/dn-gmx-vaults/contracts/vaults/DnGmxBatchingManager.sol#247

## Tool used

Manual Review

## Recommendation

Fixed by RageTrade in [PR #51](https://github.com/RageTrade/delta-neutral-gmx-vaults/pull/51)
