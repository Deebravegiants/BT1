# [M] Default slippage value too high

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-04-maple
Published: 2021-04-21
Source: https://github.com/code-423n4/2021-04-maple-findings/issues/106
Type: code-finding

## Details
# Handle

janbro


# Vulnerability details

## Summary
Default slippage value too high.

## Risk Rating
Medium

## Vulnerability Details
MapleGlobals.sol
Line 87: maxSwapSlippage = 1000; // 10 %
The default slippage value of 10% is vulnerable to sandwich attackers which would shift larger costs onto stakers and LPs after a liquidation event. Flash loans can be utilized to manipulate the Uniswap price to an unfavorable rate for liquidation. This is effectively a liquidation penalty that gets distributed to front runners.

## Impact
Liquidation event could cause more loss to stakers and liquidity providers than expected.

## Proof of Concept
See https://cmichel.io/de-fi-sandwich-attacks/

## Tools Used
Manual code review

## Recommended Mitigation Steps
Set the default slippage to a lower value.
