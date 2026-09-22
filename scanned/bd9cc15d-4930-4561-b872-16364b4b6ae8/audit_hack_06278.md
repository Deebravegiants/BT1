# [M] Rounding of shares causes loss of deposits

## Summary
Severity: Medium
Reporter: jkoppel
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/testing/MockAlchemist.vy#L72
Type: audit-issue

## Details
# Rounding of shares causes loss of deposits

## Summary

If MockAlchemist is any guide, then 1 share being worth 1e18 tokens is a typical number.

This means depositors will lose a lot of value to rounding error.

## Vulnerability Detail

In register_deposit, user is given an integer number of shares. If 1 share means 1e18 tokens, then someone  who deposits 1.99 WETH may only get shares worth 1 WETH.

## Impact

Depositors can lose a lot of money to rounding. Someone  who deposits 1.99 WETH may only get shares worth 1 WETH.

## Code Snippet

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/testing/MockAlchemist.vy#L72

1 * 10 ** 18 tokens per share proposed as a typical number.

## Tool used

Manual Review

## Recommendation

.....allow fractional shares? Hope I'm wrong? Change Alchemix to use more granular shares?
