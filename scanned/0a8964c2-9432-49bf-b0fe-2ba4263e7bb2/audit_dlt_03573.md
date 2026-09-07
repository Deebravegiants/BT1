# [M] Furnace would melt less than intended

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-08-reserve-mitigation
Published: 2023-08-22
Source: https://github.com/code-423n4/2023-08-reserve-mitigation-findings/issues/37
Type: code-finding

## Details
# Lines of code

https://github.com/reserve-protocol/protocol/blob/99d9db72e04db29f8e80e50a78b16a0b475d79f3/contracts/p1/Furnace.sol#L92-L105


# Vulnerability details

We traded one problem with another here
The original issue was that in case `melt()` fails then the distribution would use the new rate for previous periods as well.
The issue now is that in case of a failure (e.g. paused or frozen) we simply don’t melt for the previous period. Meaning RToken holders would get deprived of the melting they’re supposed to get.

This is esp. noticeable when the ratio has been decreased and the balance didn’t grow much, in that case we do more harm than good by updating `lastPayout` and `lastPayoutBal`.

A better mitigation might be to update the `lastPayout` in a way that would reflect the melting that should be distributed.



## Assessed type

Other
