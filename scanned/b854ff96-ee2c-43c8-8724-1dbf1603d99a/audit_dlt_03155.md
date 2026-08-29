# [M] Market-specific pause is not checked for payRent

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-06-realitycards
Published: 2021-06-16
Source: https://github.com/code-423n4/2021-06-realitycards-findings/issues/143
Type: code-finding

## Details
# Handle

cmichel


# Vulnerability details


## Vulnerability Details

The treasury only checks its `globalPause` field but does not check its market-specific `marketPaused` field for `Treasury.payRent`.
The market contract can therefore still collect rent even when it's paused using `Market.updateTimeHeldLimit`, `Market.exit` and `Market.collectRentAllCards`. (`treasury.marketPaused` is only checked in `Market.newRental`)

## Impact

The market-specific pause does not work correctly.

## Recommended Mitigation Steps

Add checks for `marketPaused` in the Treasury for `payRent`.
