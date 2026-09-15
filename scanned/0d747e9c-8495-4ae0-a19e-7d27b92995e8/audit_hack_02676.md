# [M] `epochsByBuyer[]` can lose records

## Summary
Severity: Medium
Reporter: __141345__
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L545-L553
Type: audit-issue

## Details
# `epochsByBuyer[]` can lose records

## Summary

When `cancelLimitOrder()`, the `epoch` will be removed from `epochsByBuyer[]`, but the user could have other orders on the orderbook, the record will be inaccurate and mislead the users.


## Vulnerability Detail

If a user put 2 limit orders with different prices, 2 separate id will be assigned, but only 1 epoch will be added to the `epochsByBuyer[]` array. 
If the user cancel 1 of the orders, the `epoch` will be removed from `epochsByBuyer[]`, it will be impossible to track the other orders put by the user. And the `getEpochsByBuyer()` function will return inaccurate result.



## Impact

If some users rely on the results of `getEpochsByBuyer()` for new orders, the returned inaccurate results could be misleading, and cause potential loss to the users due to wrong information.


## Code Snippet

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L545-L553

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/Auction.sol#L220



## Tool used

Manual Review


## Recommendation

Only remove the `epochsByBuyer` records when all the orders of the user is cancelled.
