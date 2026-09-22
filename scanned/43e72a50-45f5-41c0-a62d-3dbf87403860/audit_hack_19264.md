# [H] `TelcoinDistributor :: proposeTransaction ` Council Member can steal all funds

## Summary
Severity: High
Reporter: Cheery Ash Goose
Source: https://github.com/sherlock-audit/2024-01-telcoin/blob/main/telcoin-audit/contracts/protocol/core/TelcoinDistributor.sol#L87
Type: audit-issue

## Details
# `TelcoinDistributor :: proposeTransaction ` Council Member can steal all funds

## Summary
member can propose a transaction and approve it
## Vulnerability Detail

## Impact
loss of all funds
## Code Snippet
https://github.com/sherlock-audit/2024-01-telcoin/blob/main/telcoin-audit/contracts/protocol/core/TelcoinDistributor.sol#L87

https://github.com/sherlock-audit/2024-01-telcoin/blob/main/telcoin-audit/contracts/protocol/core/TelcoinDistributor.sol#L143
## Tool used

Manual Review

## Recommendation
another person must approve the proposal
