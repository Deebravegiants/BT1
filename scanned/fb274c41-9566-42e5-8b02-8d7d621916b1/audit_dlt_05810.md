# [?] Fix the deadlock during statements gossiping (#9868)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/polkadot-sdk
Published: 2025-09-30
Source: https://github.com/paritytech/polkadot-sdk/commit/ed4eebb461069f65fda4a88d44ee811dd8c010e3
Type: security-commit

## Details
Fix the deadlock during statements gossiping (#9868)

# Description

During statement store benchmarking we experienced deadlock-like
behavior which we found happened during statement propagation. Every
second statements were propagating, locking the index which possibly
caused the deadlock. After the fix, the observed behavior no longer
occurs.

Even though there is a possibility to unsync the DB and the index for
read operations and release locks earlier, which should be harmless, it
leads to regressions. I suspect because of concurrent access to many
calls of db.get(). Checked with the benchmarks in
https://github.com/paritytech/polkadot-sdk/pull/9884

## Integration

This PR should not affect downstream projects.

---------

Co-authored-by: cmd[bot] <41898282+github-actions[bot]@users.noreply.github.com>
