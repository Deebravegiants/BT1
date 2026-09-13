# [M] getfCashGivenCashAmount reverts if fCashDelta hits 1

## Summary
Severity: Medium
Reporter: 0xGoodess
Source: https://github.com/sherlock-audit/2023-03-notional/blob/main/contracts-v2/contracts/internal/markets/InterestRateCurve.sol#L585
Type: audit-issue

## Details
# getfCashGivenCashAmount reverts if fCashDelta hits 1

## Summary
✅ getfCashGivenCashAmount reverts if fCashDelta hits 1

## Vulnerability Detail
getfCashGivenCashAmount might revert if fCashDelta hits 1

## Impact
breaks `getfCashAmountGivenCashAmount` which is a view function on the Calculation Viewers. Some user may rely on this to decide the slippage amount they would like to accept when swapping fCash <=> Cash.

## Code Snippet
https://github.com/sherlock-audit/2023-03-notional/blob/main/contracts-v2/contracts/internal/markets/InterestRateCurve.sol#L585

## Tool used

Manual Review

## Recommendation
```solidity
if (fCashDelta <= 1) return fCash_1;
```
