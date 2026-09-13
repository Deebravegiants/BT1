# [M] TimeToMaturity better use auction time

## Summary
Severity: Medium
Reporter: __141345__
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/pricer/PricerInternal.sol#L62-L68
Type: audit-issue

## Details
# TimeToMaturity better use auction time

## Summary

In `getDeltaStrikePrice64x64()`, TimeToMaturity is using currently `block.timestamp`. However, the actual option begins after the auction is finalized, there is some time difference between the calculation time. Hence the price derived will be inaccurate. Based on the inaccurate TimeToMaturity, some users could get misleading price and lose fund.


## Vulnerability Detail

The actual option underwritten is after the auction. But when calculating the price, the spot `block.timestamp` is used. The time difference will result in a higher price since the time value will be higher.

## Impact

Some users could get misleading price and lose fund.


## Code Snippet

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/pricer/PricerInternal.sol#L62-L68


## Tool used

Manual Review


## Recommendation

Use the timestamp of the auction instead of `block.timestamp` in `_getTimeToMaturity64x64(uint64 expiry)`.
