# [M] ERC777 token order can attack keeper to exhaust gas in spot-dex

## Summary
Severity: Medium
Reporter: kutugu
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L201
Type: audit-issue

## Details
# ERC777 token order can attack keeper to exhaust gas in spot-dex

## Summary

spot-dex supports ERC777 token, the order's contract hook is called back when the order is executed, which leads to two uses:
- Malicious users can control the execution time of the order
- Malicious users can attack keeper to exhaust gas

## Vulnerability Detail

Mainly through the second type of repeated attack, keeper can be run out of funds.

## Impact

Malicious users can control the execution time of the order or attack keeper to exhaust gas. 
ERC777 has very few tokens and may have very little keeper support, with mid impact.

## Code Snippet

- https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L201
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L161

## Tool used

Manual Review

## Recommendation

This kind of attack is hard to prevent, better not support ERC777
