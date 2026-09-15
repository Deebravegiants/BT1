# [M] HGTRemote may be blacklisted causing bridge to become nonfunctional

## Summary
Severity: Medium
Reporter: 0x52
Source: https://github.com/sherlock-audit/2023-04-hubble-exchange/blob/main/hubble-protocol/contracts/HGTRemote.sol#L14
Type: audit-issue

## Details
# HGTRemote may be blacklisted causing bridge to become nonfunctional

## Summary

USDC is different than most other ERC20 tokens because it contains a blacklist function that can be set to prevents any transfers to or from certain addresses. If HGTRemote were to become blacklisted, the entire bridge and by extension the hubble mainnet would suffer massive loss.

## Vulnerability Detail

See summary

## Impact

The HGT bridge will become completely nonfunctional if blacklisted

## Code Snippet

https://github.com/sherlock-audit/2023-04-hubble-exchange/blob/main/hubble-protocol/contracts/HGTRemote.sol#L14

## Tool used

Manual Review

## Recommendation

Consider using a different gas token
