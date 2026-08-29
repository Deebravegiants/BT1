# [M] buyFYToken and buyBase do not reimburse leftovers

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-05-yield
Published: 2021-06-02
Source: https://github.com/code-423n4/2021-05-yield-findings/issues/39
Type: code-finding

## Details
# Handle

pauliax


# Vulnerability details

## Impact
functions buyFYToken and buyBase do not reimburse leftovers. It checks that the transferred amount is between min and max boundaries, however, it does not send back any excess amount back to the sender nor it accounts it in the _update function (e.g. it uses _baseCached + baseIn, not baseBalance) so basically these tokens will be left for bots to feed their hunger.

## Recommended Mitigation Steps
Either reimburse the sender, e.g. send back baseBalance - _baseCached - baseIn, or account that in the _update function.
