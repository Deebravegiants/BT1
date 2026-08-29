# [M] Incompatability with deflationary / fee-on-transfer tokens

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-05-88mph
Published: 2021-05-19
Source: https://github.com/code-423n4/2021-05-88mph-findings/issues/16
Type: code-finding

## Details
# Handle

cmichel


# Vulnerability details


## Vulnerability Details

The `DInterest.deposit` function takes a `depositAmount` parameter but this parameter is not the actual transferred amount for fee-on-transfer / deflationary (or other rebasing) tokens.

## Impact

The actual deposited amount might be lower than the specified `depositAmount` of the function parameter.
This would lead to wrong interest rate calculations on the principal.

## Recommended Mitigation Steps

Transfer the tokens first and compare pre-/after token balances to compute the actual deposited amount.
