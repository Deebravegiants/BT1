# [?] fix(epoch-sync): reject malicious proofs instead of overflow panic (#15921)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-06-16
Source: https://github.com/near/nearcore/commit/1ab8ed40d320d155a04d7b82aa745e73e773cc91
Type: security-commit

## Details
fix(epoch-sync): reject malicious proofs instead of overflow panic (#15921)

A peer that a bootstrapping node selects as its epoch-sync source can
crash the node with an arithmetic overflow panic on attacker-controlled
`u64` fields in the proof. Two such sites, both reachable before the
offending value is validated:

- `partial_merkle_tree_for_first_block.size() + 1` in
`verify_current_epoch_data`: `size = u64::MAX` overflows before the
well-formedness check.
- `last_final_block_header.height() + 1` in `verify_block_endorsements`:
`height = u64::MAX` overflows before any signature check.

Both now use `checked_add` and return `InvalidEpochSyncProof` on
overflow. Adds regression tests for each.
