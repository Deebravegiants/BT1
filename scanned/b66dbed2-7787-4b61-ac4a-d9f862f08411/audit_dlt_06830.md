# [M] No bar fees for IndexPools?

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-09-sushitrident
Published: 2021-09-29
Source: https://github.com/code-423n4/2021-09-sushitrident-findings/issues/181
Type: code-finding

## Details
# Handle

0xsanson


# Vulnerability details

## Impact
IndexPool doesn't collect fees for `barFeeTo`. Since this Pool contains also a method `updateBarFee()`, probably this is an unintended behavior.
Also without a fee, liquidity providers would probably ditch ConstantProductPool in favor of IndexPool (using the same two tokens with equal weights), since they get all the rewards. This would constitute an issue for the ecosystem.

## Recommended Mitigation Steps
Add a way to send barFees to barFeeTo, same as the other pools.
