# [?] fix(kona/mpt): guard against panic when prefix longer than path in Extension node (#19728)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2026-06-16
Source: https://github.com/ethereum-optimism/optimism/commit/40d8cf29c2c27c25bbd7e86e91cc40e7412a9310
Type: security-commit

## Details
fix(kona/mpt): guard against panic when prefix longer than path in Extension node (#19728)

Adds a length check before slicing in `TrieNode::open` to prevent a
panic when `prefix.len()` exceeds `path.len()` for Extension nodes.

Adds a unit test that calls `TrieNode::open` on an Extension node with
a path shorter than the prefix, verifying it returns `Ok(None)` rather
than panicking. Also enables the `thread_rng` feature for `rand` in
dev-dependencies so the existing proptest compiles.

Co-authored-by: Einar Rasmussen <einar@oplabs.com>
Co-authored-by: Claude Sonnet 4.6 <noreply@anthropic.com>
