# [?] cryptonote_basic: fix amount overflow detection on 32-bit systems

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2023-05-08
Source: https://github.com/monero-project/monero/commit/7206ef8ab85c921310ba45c1dd8b1621622aa696
Type: security-commit

## Details
cryptonote_basic: fix amount overflow detection on 32-bit systems

On systems where `ULONG_MAX` != `ULLONG_MAX` (e.g. most 32-bit systems), the `round_money_up` function will not correctly detect overflows.
