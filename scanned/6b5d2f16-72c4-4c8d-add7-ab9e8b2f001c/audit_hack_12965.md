# [M] MarginDex has no expiration time protection

## Summary
Severity: Medium
Reporter: kutugu
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L294
Type: audit-issue

## Details
# MarginDex has no expiration time protection

## Summary

MarginDex invokes the vault operation as a router, hasn't add  expiration time protection.

## Vulnerability Detail

Even with slippage protection, if the tx stays in mempool for a long time and the oracle price changes significantly, the user's potential income will be lower, equivalent to a loss of funds.

## Impact

A user's tx may be executed after a long period of time, resulting in a loss of funds.

## Code Snippet

- https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L294
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L378
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L417

## Tool used

Manual Review

## Recommendation

Add expiration time protection
