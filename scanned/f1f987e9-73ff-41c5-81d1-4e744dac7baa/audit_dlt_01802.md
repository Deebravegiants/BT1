# [?] Fix underflow issue for XRP:

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2016-02-25
Source: https://github.com/XRPLF/rippled/commit/d8ee487c196bf5972ad2b0f153df56008e0b02ac
Type: security-commit

## Details
Fix underflow issue for XRP:

In some cases multiplying or dividing STAmounts gave incorrect results.

This happens when:

1) The result should be rounded up
2) The STAmount represents a native value (XRP)
3) The rounded up value was less than one drop

In this case, the result was zero, instead of one drop. This could
cause funded offers to be removed as unfunded.
