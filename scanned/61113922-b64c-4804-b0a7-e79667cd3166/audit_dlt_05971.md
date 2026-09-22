# [?] security: review follow-ups for GHSA-2026-010 and -011

## Summary
Severity: Unknown
Chain: Bittensor
Component: opentensor/subtensor
Published: 2026-06-16
Source: https://github.com/RaoFoundation/subtensor/commit/18e0ecb009914d24b1e41f6e199e5fe9abeca5c4
Type: security-commit

## Details
security: review follow-ups for GHSA-2026-010 and -011

GHSA-2026-010: merge RootClaimed by saturating_add (sum), not max(). Both
legitimate watermarks must combine on a real merge (e.g. coldkey swap onto an
existing position); the stale-residual case is already prevented by the root-swap
cleanliness gate. Retarget the regression test to assert A+B.

GHSA-2026-011: the all-subnets hotkey-swap cooldown must cover subnets where the
old hotkey is a parent (ChildKeys) or child (ParentKeys), not just member subnets,
since parent_child_swap_hotkey migrates those unconditionally. Broaden
affected_netuids accordingly + add a parent-only-subnet regression test.

Addresses review comments on #14 and #15.
