# [M] Vault: `_update_debt` should be called in the entry of close_position, reduce_position and liquidate

## Summary
Severity: Medium
Reporter: n33k
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L251
Type: audit-issue

## Details
# Vault: `_update_debt` should be called in the entry of close_position, reduce_position and liquidate

## Summary

In functions like `close_position`, `reduce_position` and `liquidate`, `_update_debt` should be called first to accure debt interest for `_debt(_position_uid)` function to return the correct debt.

## Vulnerability Detail

`close_position`, `reduce_position` and `liquidate` all calls `_debt(_position_uid)` to get debt amount, but if `_update_debt` is not called beforehand, the interest is not added so the debt is incorrect.

## Impact

Debt amount will less than real.

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L251

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L313

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L354-L357

## Tool used

Manual Review

## Recommendation

Call `_update_debt` at the beginning of these functions.
