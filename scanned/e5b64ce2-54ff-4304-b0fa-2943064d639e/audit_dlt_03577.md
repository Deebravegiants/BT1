# [M] M-06 Unmitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-angle-mitigation
Published: 2023-07-21
Source: https://github.com/code-423n4/2023-07-angle-mitigation-findings/issues/29
Type: code-finding

## Details
# Lines of code

https://github.com/AngleProtocol/angle-transmuter/blob/3e43e29d2b2f0b75876396e7c65e48c00c5fd1b2/contracts/savings/SavingsVest.sol#L212


# Vulnerability details

## Original Issue
https://github.com/code-423n4/2023-06-angle-findings/issues/13

## Details
This issue shows users may lose a portion of yield when `protocolSafetyFee` and `vestingPeriod` are changed.

As mitigation, it recommends accruing interests before those parameters are changed. 

## Mitigation
PR: https://github.com/AngleProtocol/angle-transmuter/commit/94c4e51ae3400a63532e85f04f4081152adc97db

It calls `accrue()` method when `protocolSafetyFee` and `vestingPeriod` are changed in `setParams()`.

When `vestingPeriod` is changed, `vestingProfit` and `lastUpdate` should always be updated for correct vesting amount calculation. But in the current implementation of `accrue()`, `vestingProfit` and `lastUpdate` are updated only when the collateral ratio is changed more than 0.1 percent. So if the collateral ratio is nearly the same, `vestingProfit` and `lastUpdate` are not updated in the `accrue()` method, and this will affect the vesting amount.

## Recommended Mitigation
`vestingProfit` and `lastUpdate` should always be updated when `vestingPeriod` is changed.

## Conclusion
This issue wasn't mitigated properly.


## Assessed type

Other
