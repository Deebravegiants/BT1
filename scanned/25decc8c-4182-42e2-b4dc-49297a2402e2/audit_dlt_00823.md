# [?] rosetta: fix historical vesting liquid/locked balance underflow

## Summary
Severity: Unknown
Chain: Mina
Component: MinaProtocol/mina
Published: 2026-07-20
Source: https://github.com/MinaProtocol/mina/commit/a26652a650ab6b6f20e1a0370fb874c8ac0dbcbe
Type: security-commit

## Details
rosetta: fix historical vesting liquid/locked balance underflow

Compute the liquid balance directly as total - min_balance(end_slot) instead
of total + incremental_balance_between_slots. The old base was the *total*
balance rather than the liquid base (total - min_balance(start_slot)), so for
accounts with an active vesting schedule the reported liquid_balance exceeded
the total and drove the downstream unsigned `locked = total - liquid` into a
2^64 wraparound.

This is a pure behavior fix: liquid_balance_at_slot drops the now-unused
~start_slot parameter (the corrected formula only depends on end_slot), and
the regression tests from the previous commit are updated only to match that
dropped parameter -- their assertions and expected values are unchanged, and
all now turn green.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
