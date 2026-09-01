# [M] Incorrect "maxAvailable" calc in "maxWithdraw" for Senior Vault

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-rage-trade
Published: 2022-11-25
Source: https://github.com/sherlock-audit/2022-10-rage-trade-judging/issues/84
Type: sherlock-finding

## Details
0x52

RageTrade (found by protocol team after contest)

medium

# In "maxWithdraw" for Senior Vault, the calculation for "maxAvailable" was incorrect.

## Summary

In "maxWithdraw" for Senior Vault, the calculation for "maxAvailable" was incorrect.

## Vulnerability Detail

## Impact

Could result in unexpected behavior

## Code Snippet

https://github.com/sherlock-audit/2022-10-rage-trade/blob/main/dn-gmx-vaults/contracts/vaults/DnGmxSeniorVault.sol#L406

## Tool used

Manual Review

## Recommendation

Fixed by RageTrade in [PR #50](https://github.com/RageTrade/delta-neutral-gmx-vaults/pull/50)
