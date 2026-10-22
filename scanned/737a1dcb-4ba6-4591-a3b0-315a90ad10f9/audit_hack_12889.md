# [H] Bad debt is not updated when liquidating

## Summary
Severity: High
Reporter: stopthecap
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L346-L375
Type: audit-issue

## Details
# Bad debt is not updated when liquidating

## Summary
Bad debt is not updated when liquidating

## Vulnerability Detail
In unstoppable when a user closes a position and it ends in a loss the `bad_debt` mapping in creased by said amount. 
When a keeper calls `liquidate` and liquidates a position and it also ends in a loss, the `bad_debt` mapping is not updated, not reflecting the actual state of the debt in the protocol.

## Impact
Missing to update bad_debt when liquidating will cause further calculations to be wrong due to not reflecting the actual state of the protocol

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L346-L375
## Tool used

Manual Review

## Recommendation
Increase `self.bad_debt[position.debt_token] += bad_debt`  when a liquidation returns less than the initial debt amount borrowed
