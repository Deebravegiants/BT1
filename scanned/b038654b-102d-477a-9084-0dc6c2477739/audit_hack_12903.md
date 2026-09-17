# [M] Persistent position_uid Lead to Position Creation Limitation after Liquidation

## Summary
Severity: Medium
Reporter: pengun
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L669-L677
Type: audit-issue

## Details
# Persistent position_uid Lead to Position Creation Limitation after Liquidation

## Summary
In `MarginDex.vy` the liquidation function didn't remove position_uid from the `trades_by_account` array. This results in these uid persisting even after the positions have been liquidated.

## Vulnerability Detail
Upon opening a trade, the position_uid is appended to the `trades_by_account` array for management purposes. When the position is closed, the corresponding uid is removed from the array. 

However, the liquidation function, unlike the full close function, doesn't remove the uid from the `trades_by_account` array. Therefore, if a position is liquidated, its uid continues to remain in the array.

Given that the `trades_by_account` array can hold a maximum of 1024 positions, this issue would prevent users from creating any new positions once 1024 positions have been liquidated.

## Impact
The impact of this issue is that it could limit a user's ability to create new positions after a certain number of positions have been liquidated. This may hamper the platform's usability and functionality for active traders, thereby potentially affecting their trading strategies and overall trading experience.

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L669-L677

## Tool used

Manual Review

## Recommendation
It is recommended to incorporate logic within the liquidate function to remove the corresponding uid from the `trades_by_account`array once a position has been liquidated.
