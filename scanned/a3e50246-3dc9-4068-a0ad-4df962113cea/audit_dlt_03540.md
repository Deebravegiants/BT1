# [H] Awarding takes reserve fee several times

## Summary
Severity: High
Chain: Smart contract
Component: 2021-06-pooltogether
Published: 2021-06-23
Source: https://github.com/code-423n4/2021-06-pooltogether-findings/issues/85
Type: code-finding

## Details
# Handle

cmichel


# Vulnerability details

The `PrizePool.captureAwardBalance` function takes fees repeatedly on the same interest. One would expect `unaccountedPrizeBalance` to be `0` in any repeated calls, but it's not.

Assume the following example scenario with a 10% reserve fee:
- user calls `captureAwardBalance`: `totalInterest = 1000, _currentAwardBalance = 500 => unaccountedPrizeBalance = 1000 - 500 = 500.` With a 10% reserve fee on it, `unaccountedPrizeBalance = 450 => _currentAwardBalance = 500 + 450`.
- user calls `captureAwardBalance` immediately again and it'll take a fee on `totalInterest = 1000, _currentAwardBalance = 500 => unaccountedPrizeBalance = 1000 - 950 = 50`. Adding another `5` to the reserve.
- can keep going taking a fee on a smaller amount each time

## Impact

Instead of taking a reserve fee `f`  (`0 <= f < 1.0 = 100%`), a higher fee of `f / (1 - f)` can be taken by repeated calls to `captureAwardBalance`.
The pool creator (or reserve registry owner) can even use this with a high reserve fee (~99%) to rug the entire pool investments by inflating the `reserveTotalSupply` to almost any arbitrary value and later redeeming everything using `withdrawReserve`.

## Recommended Mitigation Steps

When determining the amount to take a fee on (`unaccountedPrizeBalance`), one needs to take into account not only the after-fee amount (`_currentAwardBalance`) but the pre-fee amount.
This probably requires tracking another variable.
