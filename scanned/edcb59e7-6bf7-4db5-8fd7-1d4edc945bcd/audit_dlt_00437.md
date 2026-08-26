# [?] Fix out-of-bounds chunk index error in erasure coding (#12521)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/polkadot-sdk
Published: 2026-07-15
Source: https://github.com/paritytech/polkadot-sdk/commit/35000d248860886d1b2fab8c79940e3356d02a36
Type: security-commit

## Details
Fix out-of-bounds chunk index error in erasure coding (#12521)

# Description

`reconstruct` in `polkadot-erasure-coding` allocated `received_shards`
with
length `n_validators` and then indexed it directly with the
caller-provided
`chunk_idx`. Any chunk index `>= n_validators` panicked with an
index-out-of-bounds instead of returning the already-defined
`Error::ChunkIndexOutOfBounds` variant.

This PR adds the missing bounds check so invalid indices are reported as
an
error rather than panicking.

Closes #12465

## Integration

`reconstruct` (and `reconstruct_v1`) now
return `Err(Error::ChunkIndexOutOfBounds { chunk_index, n_validators })`
for an
out-of-bounds chunk index where they previously panicked. The function
already
returns `Result<_, Error>` and the variant is already public, so there
is no API
or signature change — callers that propagate the `Result` need no
modification.

## Review Notes

The fix is a single guard in the chunk-consumption loop, placed
alongside the
existing `UnevenLength` check and before the indexing write:

```rust
if chunk_idx >= n_validators {
```

_Trimmed to 38 lines — full report: https://github.com/paritytech/polkadot-sdk/commit/35000d248860886d1b2fab8c79940e3356d02a36_
