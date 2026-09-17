# [M]  No default `liquidationThresholdPercent`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-04-marginswap
Published: 2021-04-07
Source: https://github.com/code-423n4/2021-04-marginswap-findings/issues/28
Type: code-finding

## Details
# Email address

mail@cmichel.io


# Handle

@cmichelio


# Eth address

0x6823636c2462cfdcD8d33fE53fBCD0EdbE2752ad


# Vulnerability details

The `IsolatedMarginTrading` contract does not define a default `liquidationThresholdPercent` which means it is set to 0.

The `belowMaintenanceThreshold` function uses this value and anyone could be liquidated due to `100 * holdings >= liquidationThresholdPercent * loan = 0` being always true.



# Impact

Anyone can be liquidated immediately.
If the faulty `belowMaintenanceThreshold` function is fixed (see other issue), then nobody could be liquidated which is bad as well.



# Recommended mitigation steps

Set a default liquidation threshold like in `CrossMarginTrading` contracts.
