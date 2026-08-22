# [M] interestRatePerBlock in FixedInterestRateModel.constructor can exceed BORROW_RATE_MAX_MANTISSA

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-union-finance
Published: 2022-11-04
Source: https://github.com/sherlock-audit/2022-10-union-finance-judging/issues/158
Type: sherlock-finding

## Details
GimelSec

medium

# interestRatePerBlock in FixedInterestRateModel.constructor can exceed BORROW_RATE_MAX_MANTISSA

## Summary

`interestRatePerBlock` should not exceed `BORROW_RATE_MAX_MANTISSA`. `FixedInterestRateModel.setInterestRate` has the correct check. But `FixedInterestRateModel.constructor` doesn’t.

## Vulnerability Detail

According to `FixedInterestRateModel.setInterestRate`. `interestRatePerBlock` should not exceed `BORROW_RATE_MAX_MANTISSA`.

```solidity
    function setInterestRate(uint256 _interestRatePerBlock) external override onlyOwner {
        if (_interestRatePerBlock > BORROW_RATE_MAX_MANTISSA) revert BorrowRateExceeded();
        interestRatePerBlock = _interestRatePerBlock;

        emit LogNewInterestParams(_interestRatePerBlock);
    }
```

However, the constructor doesn’t have the same check.

```solidity
    constructor(uint256 interestRatePerBlock_) {
        interestRatePerBlock = interestRatePerBlock_;

        emit LogNewInterestParams(interestRatePerBlock_);
    }
```

It seems to be a low-severity issue. But according to this [report](https://code4rena.com/reports/2021-10-union/#m-04-change-in-interest-rate-can-disable-repay-of-loan), a malicious admin could use this issue to temporarily disable repay of loan in `UToken`.

When doing repay in `UToken`, `UToken.borrowRatePerBlock` would be called. if `borrowRateMantissa > BORROW_RATE_MAX_MANTISSA`, the repay always revert.

```solidity
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-union-finance-judging/issues/158_
