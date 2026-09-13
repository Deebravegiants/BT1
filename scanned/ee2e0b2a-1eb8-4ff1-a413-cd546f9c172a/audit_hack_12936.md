# [H] `reduce_position` from `Vault.vy` can underflow 100% of the time in some cases which will make reducing positions impossible

## Summary
Severity: High
Reporter: Vagner
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L314
Type: audit-issue

## Details
# `reduce_position` from `Vault.vy` can underflow 100% of the time in some cases which will make reducing positions impossible

## Summary
The function `reduce_position` is used to reduce a position of an user, in case he doesn't have enough assets to close his position but this function has a subtraction that can revert 100% for the cases where the margin and the debt tokens both have 18 decimals.
## Vulnerability Detail
The function `reduce_position` calculates `margin_debt_ratio` like this https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L314
`PRECISION` being 1e18, `position.margin_amount` and `debt_amount` being denominated in the assets decimals. In the cases where both the `position.margin_amount` and `debt_amount` are 1e18 numbers the `margin_debt_ratio` will be greater than 1e18 every time. After that `reduce_margin_by_amount` is calculated like this https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L321-L323 where `amount_out_received ` is a number denominated in the assets decimals, which in the case of 18 decimals assets is a 1e18 number, so by multiplying 2 numbers greater than 1e18 and dividing by 1e18, `reduce_margin_by_amount` will always be greater than `amount_out_received `. The problem occurs in the next line where it is done a subtraction that looks like this https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L324 
,subtraction which will revert 100% of the time since, for the cases of 2 assets with 18 decimals, since `reduce_margin_by_amount` will always be greater than `amount_out_received `
## Impact
The impact is a high one since multiple tokens have 18 decimals and this would make reducing a position basically impossible.
## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L324
## Tool used

Manual Review

## Recommendation
Change the logic of the calculations so the subtraction would not underflow.
