# [H] Reentrancy guard is missing for deposit, mint in junior and senior vaults

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-rage-trade
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-10-rage-trade-judging/issues/82
Type: sherlock-finding

## Details
ak1

high

# Reentrancy guard is missing for deposit, mint in junior and senior vaults

## Summary

In junior and senior vaults, shares are minted and distributed to users.

## Vulnerability Detail

For senior vault,

https://github.com/sherlock-audit/2022-10-rage-trade/blob/main/dn-gmx-vaults/contracts/vaults/DnGmxSeniorVault.sol#L211-L238

For junior vault,
https://github.com/sherlock-audit/2022-10-rage-trade/blob/main/dn-gmx-vaults/contracts/vaults/DnGmxJuniorVault.sol#L388-L412

The function call can be staked or wrapped inside anther function and re-entered.

## Impact

Both mint and deposit function can be reentered and cause considerable disruption.

## Code Snippet

Refer the vulnerability section.

## Tool used

Manual Review

## Recommendation
Add reentrancy guard which is standard practice.
