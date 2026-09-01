# [M] Inadequate slippage control

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-03-notional
Published: 2023-05-15
Source: https://github.com/sherlock-audit/2023-03-notional-judging/issues/177
Type: sherlock-finding

## Details
xiaoming90

high

# Inadequate slippage control

## Summary

The current slippage control mechanism checks a user's acceptable interest rate limit against the post-trade rate, which could result in trades proceeding at rates exceeding the user's defined limit.

## Vulnerability Detail

https://github.com/sherlock-audit/2023-03-notional/blob/main/contracts-v2/contracts/internal/markets/InterestRateCurve.sol#L421

```solidity
File: InterestRateCurve.sol
421:     function _getNetCashAmountsUnderlying(
422:         InterestRateParameters memory irParams,
423:         MarketParameters memory market,
424:         CashGroupParameters memory cashGroup,
425:         int256 totalCashUnderlying,
426:         int256 fCashToAccount,
427:         uint256 timeToMaturity
428:     ) private pure returns (int256 postFeeCashToAccount, int256 netUnderlyingToMarket, int256 cashToReserve) {
429:         uint256 utilization = getfCashUtilization(fCashToAccount, market.totalfCash, totalCashUnderlying);
430:         // Do not allow utilization to go above 100 on trading
431:         if (utilization > uint256(Constants.RATE_PRECISION)) return (0, 0, 0);
432:         uint256 preFeeInterestRate = getInterestRate(irParams, utilization);
433: 
434:         int256 preFeeCashToAccount = fCashToAccount.divInRatePrecision(
435:             getfCashExchangeRate(preFeeInterestRate, timeToMaturity)
436:         ).neg();
437: 
438:         uint256 postFeeInterestRate = getPostFeeInterestRate(irParams, preFeeInterestRate, fCashToAccount < 0);
439:         postFeeCashToAccount = fCashToAccount.divInRatePrecision(
440:             getfCashExchangeRate(postFeeInterestRate, timeToMaturity)
441:         ).neg();
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2023-03-notional-judging/issues/177_
