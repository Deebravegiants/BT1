# [M] AuctionInternal: Loop in _processOrders may cause system to get stuck

## Summary
Severity: Medium
Reporter: cccz
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L366-L383
Type: audit-issue

## Details
# AuctionInternal: Loop in _processOrders may cause system to get stuck

## Summary
AuctionInternal: Loop in _processOrders may cause system to get stuck
## Vulnerability Detail
In the_processOrders function of the AuctionInternal contract, all the elements in the orderbook are iterated, and if there are too many elements in the orderbook, the _processOrders function may revert due to exceeding the block size gas limit.
## Impact
This may cause system to get stuck
## Code Snippet
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L366-L383
## Tool used

Manual Review

## Recommendation

Consider setting a looping upper limit when processing elements in an orderbook
