# [H] Triggering `is_accepting_new_orders` every time a position has any amount of bad debt will backfire the protocol

## Summary
Severity: High
Reporter: stopthecap
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L233-L266
Type: audit-issue

## Details
# Triggering `is_accepting_new_orders` every time a position has any amount of bad debt will backfire the protocol

## Summary
Triggering `is_accepting_new_orders` every time a position has any amount of bad debt will backfire the protocol

## Vulnerability Detail
Currently unstoppable is setting `is_accepting_new_orders` to false every time when closing a position there is any amount of small debt, limiting a lot the progress of the protocol.

The issue has a high severity because anyone can close their position at any time. If the returned amount, because the market fluctuated while the order was open and there was high slippage,  felt below the `position_debt_amount` , almost the whole protocol will be paused. This will happen extreamily often, at some point, it might be unusable because very 1 min there is a position that falls below `position_debt_amount`

## Impact
Protocol might get to the point where it is unusable because it is always paused.

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L233-L266

## Tool used

Manual Review

## Recommendation
Add a minimum amount for users to borrow so this does not happen that often. And also add a min amount of bad debt to put the protocol in "alert mode".
