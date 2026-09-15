# [M] Should reset allowance to 0 before approve an non-zero value

## Summary
Severity: Medium
Reporter: kutugu
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L204
Type: audit-issue

## Details
# Should reset allowance to 0 before approve an non-zero value

## Summary

Should reset allowance to 0 before approve non-zero value, or cannot interact with some tokens such as USDT.

## Vulnerability Detail

USDT not support approve non-zero value if allowance is not 0.

## Impact

The protocol is not compatible with USDT stablecoins, and users cannot use USDT in the protocol.

## Code Snippet

- https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L204
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L164
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L174
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L395

## Tool used

Manual Review

## Recommendation

approve 0 before approve an non-zero value
