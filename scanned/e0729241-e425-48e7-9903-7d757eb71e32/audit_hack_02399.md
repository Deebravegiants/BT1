# [M] Misleading NatSpec Comments

## Summary
Severity: Medium
Source: https://github.com/compound-finance/compound-protocol/blob/f385d71983ae5c5799faae9b2dfea43e5cf75262/contracts/InterestRateModel.sol#L19
Type: audit-issue

## Details
Since the purpose of the Ethereum Natural Specification (NatSpec) is to describe the code to the user, misleading statements should be considered a violation of the public API that may confuse or mislead users.

The `getBorrowRate` [interface](https://github.com/compound-finance/compound-protocol/blob/f385d71983ae5c5799faae9b2dfea43e5cf75262/contracts/InterestRateModel.sol#L19) and [implementation](https://github.com/compound-finance/compound-protocol/blob/f385d71983ae5c5799faae9b2dfea43e5cf75262/contracts/WhitePaperInterestRateModel.sol#L113) `@return` comments state that the rate is scaled by 10e18\. In fact, it is only scaled by 1e18.

The `CToken` contract [borrowRateMaxMantissa comment](https://github.com/compound-finance/compound-protocol/blob/f385d71983ae5c5799faae9b2dfea43e5cf75262/contracts/CToken.sol#L38) states that the maximum borrow rate per block is 0.0005% but it is actually 0.0005 ( or 0.05% ).

The comment on [line 7 of Unitroller.sol](https://github.com/compound-finance/compound-protocol/blob/f385d71983ae5c5799faae9b2dfea43e5cf75262/contracts/Unitroller.sol#L7-L8) is an incomplete thought/sentence.

The comment on [line 41 of ComptrollerStorage.sol](https://github.com/compound-finance/compound-protocol/blob/f385d71983ae5c5799faae9b2dfea43e5cf75262/contracts/ComptrollerStorage.sol#L41) uses the word “discount” when it should use “bonus”, which may cause confusion for people trying to understand the code. For example, a 25% discount is equivalent to a 33% bonus. That is, “25% off” is the same as “33% more for free”.

The comment on [line 6 of Exponential.sol](https://github.com/compound-finance/compound-protocol/blob/f385d71983ae5c5799faae9b2dfea43e5cf75262/contracts/Exponential.sol#L6) says “fixed-decision” when it should say “fixed-precision”.

The comment on [line 83 of CToken.sol](https://github.com/compound-finance/compound-protocol/blob/f385d71983ae5c5799faae9b2dfea43e5cf75262/contracts/CToken.sol#L83) describes `borrowIndex` as the accumulator of earned interest when it should be the accumulator of the earned interest rate.

Consider updating the comments appropriately.
