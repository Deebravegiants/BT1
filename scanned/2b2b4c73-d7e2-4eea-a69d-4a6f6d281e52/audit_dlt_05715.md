# [?] qa: Add shielded balance accounting tests for GHSA-g4x5-crjh-29ff

## Summary
Severity: Unknown
Chain: Zcash
Component: zcash/zcash
Published: 2026-06-01
Source: https://github.com/zcash/zcash/commit/ee0a3b3320ee41c0b1a7faf065c86cd340cbe031
Type: security-commit

## Details
qa: Add shielded balance accounting tests for GHSA-g4x5-crjh-29ff

shielded_balance_accounting_coinbase.py is a regression test: a coinbase with a
positive Sapling value balance aborts the node on the vulnerable binary and is
cleanly rejected (bad-cb-positive-sapling-valuebalance, node stays up) on the
fixed binary.

shielded_balance_accounting_noncoinbase.py is a characterization/guard: the same
attack in a non-coinbase transaction is not exploitable (the positive value
balance is compensated via GetShieldedValueIn / the fee), so it never aborts on
either binary; it guards against a regression that breaks that compensation.

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
