# [H] Unbounded length loop could cause DoS in `_processOrders()`

## Summary
Severity: High
Chain: Smart contract
Component: 2022-09-knox
Published: 2022-10-18
Source: https://github.com/sherlock-audit/2022-09-knox-judging/issues/82
Type: sherlock-finding

## Details
__141345__

medium

# Unbounded length loop could cause DoS in `_processOrders()`

## Summary

In `_processOrders()`, there is no limit on the length of array `orderbook`. When the `orderbook` grow too big, and the blockchain network is congested, it is possible that `_processOrders()` function will fail due to DoS. And user funds could get locked temporarily or forever.


## Vulnerability Detail


As this array `orderbook` can grow quite large, the transaction’s gas cost could exceed the block gas limit and make it impossible to call this function at all. 


## Impact

- `_processOrders()` function could fail due to DoS:
    - `finalizeAuction()` will not function
    - `cancelLimitOrder()` will not function ,users can not cancel limit order
- User funds could get locked temporarily or forever.


## Code Snippet

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L381


## Tool used

Manual Review


Duplicate of #102
