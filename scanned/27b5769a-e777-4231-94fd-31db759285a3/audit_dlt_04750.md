# [H] Unbounded length loop could cause DoS in `withdraw()`

## Summary
Severity: High
Chain: Smart contract
Component: 2022-09-knox
Published: 2022-10-18
Source: https://github.com/sherlock-audit/2022-09-knox-judging/issues/85
Type: sherlock-finding

## Details
__141345__

medium

# Unbounded length loop could cause DoS in `withdraw()`

## Summary

In `_previewWithdraw()`, there is no limit on the length of array `orderbook`. When the `orderbook` grow too big, and the blockchain network is congested, it is possible that `withdraw()` function will fail due to DoS. And user funds could get locked temporarily or forever.


## Vulnerability Detail


As this array `orderbook` can grow quite large, the transaction’s gas cost could exceed the block gas limit and make it impossible to call this function at all. 


## Impact

`withdraw()` function could fail due to DoS. And user funds could get locked temporarily or forever.


## Code Snippet

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L298


## Tool used

Manual Review


## Recommendation

Consider introducing a reasonable upper limit based on block gas limits, or split the loop and continue if it is too long.


Duplicate of #102
