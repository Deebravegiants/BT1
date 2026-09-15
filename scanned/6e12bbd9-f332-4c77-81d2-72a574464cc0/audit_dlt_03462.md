# [M] `exitTempusAMMAndRedeem` redeems to the wrong account

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-10-tempus
Published: 2021-10-20
Source: https://github.com/code-423n4/2021-10-tempus-findings/issues/22
Type: code-finding

## Details
# Handle

cmichel


# Vulnerability details

In `TempusController._exitTempusAMMAndRedeem` (the first one), the inner `_exitTempusAMMGivenAmountsOut` call redeems LP tokens and sends the yield&principal shares to the `msg.sender` already.
It then tries to redeem the received shares for backing tokens or yield-bearing tokens in `_redeemToBacking`/`_redeemToYieldBearing`.

However, as the shares have been sent to the `msg.sender` already instead of the controller itself, the redemption to backing/yield-bearing tokens will fail.

## Impact
The `exitTempusAMMAndRedeem` function does not work correctly and will always revert.

## Recommended Mitigation Steps
The `_exitTempusAMMGivenAmountsOut` call should use `this` as the recipient, not `msg.sender`.
