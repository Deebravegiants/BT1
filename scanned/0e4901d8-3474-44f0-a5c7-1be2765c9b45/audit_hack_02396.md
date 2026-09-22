# [M] Outdated Interest Rates

## Summary
Severity: Medium
Source: https://github.com/compound-finance/compound-protocol/blob/f385d71983ae5c5799faae9b2dfea43e5cf75262/contracts/CToken.sol#L410
Type: audit-issue

## Details
In the `CToken` contract, [borrowRatePerBlock](https://github.com/compound-finance/compound-protocol/blob/f385d71983ae5c5799faae9b2dfea43e5cf75262/contracts/CToken.sol#L410) and [supplyRatePerBlock](https://github.com/compound-finance/compound-protocol/blob/f385d71983ae5c5799faae9b2dfea43e5cf75262/contracts/CToken.sol#L420) are supposed to return the current rates but they may be outdated. This is because those rates depend on variables that are updated when `accrueInterest` is called. Consider calling [accrueInterest](https://github.com/compound-finance/compound-protocol/blob/f385d71983ae5c5799faae9b2dfea43e5cf75262/contracts/CToken.sol#L597) at the beginning of these functions.
