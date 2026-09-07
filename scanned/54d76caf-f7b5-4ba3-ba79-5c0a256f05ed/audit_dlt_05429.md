# [?] Fix unsound require assumptions in Liveness spec (#781)

## Summary
Severity: Unknown
Chain: Morpho
Component: morpho-org/morpho-blue
Published: 2026-07-23
Source: https://github.com/morpho-org/morpho-blue/commit/2a2921ab0ff90d59e6e9ea31437d00c0a7b844e5
Type: security-commit

## Details
Fix unsound require assumptions in Liveness spec (#781)

In summarySafeTransferFrom, the ghost balance under/overflow was silenced
with require_uint256, which is unsound in liveness rules (@withrevert +
assert !lastReverted): it assumes away the very no-revert precondition the
rules aim to prove.

Switch both branches to assert_uint256, turning the hidden assumption into
a proof obligation, and add the explicit, justified assumptions each rule
now needs (singleton solvency for out-transfers, bounded supply for
in-transfers).

Fixes #781

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_013Kx6WMx5o6emArfUMRXERr
