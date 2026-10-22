# [H] Positions are not being liquidated when they should

## Summary
Severity: High
Reporter: stopthecap
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L346-L374
Type: audit-issue

## Details
# Positions are not being liquidated when they should

## Summary
Positions are not being liquidated when they should

## Vulnerability Detail
Positions are being liquidated in the `liquidate` function:
https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L346-L374

as you can see, the position can only be liquidated if it is not liquidable:
https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L487

The problem is that the total `total_debt_shares[_debt_token]` is not updated when checking whether the positon is liquidable neither when calling `liquidate`  You can see on the following links the progression of the function calls to calculate whether a position is liquidable or not:
 
https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L444

https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1142

https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1099

https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1111

https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1117C16-L1117C16

As seen, `total_debt_shares[_debt_token]` is not updated to the current `total_debt_shares[_debt_token]` by calling `_update_debt` and therefore a stale `total_debt_shares[_debt_token]` is used to calculate whether a position is liquidable. Not accounting for positions that are in fact liquidable because the debt is not yet updated.

## Impact
Not updating the debt before liquidating a position will cause that positions that are in fact below the liquidation threshold, not be liquidated until debt is updated

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L346-L374

https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1117C16-L1117C16
## Tool used

Manual Review

## Recommendation
Call `_update_debt` at the beginning of the `liquidate` function
