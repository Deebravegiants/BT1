# [?] [execution] Fix non-deterministic hot state promotions

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-06-11
Source: https://github.com/aptos-labs/aptos-core/commit/69fe58b6494cf22608a5055cb67bd87de1ea937b
Type: security-commit

## Details
[execution] Fix non-deterministic hot state promotions

`BlockHotStateOpAccumulator` capped promotions at `MAX_PROMOTIONS_PER_BLOCK`
while accumulating reads, dropping any key first seen after the cap was hit.
The per-transaction read set is a `HashSet`, so its iteration order — and
hence *which* keys survived the cap — differed across processes. Two
validators executing the same block could therefore promote different keys to
the hot state in the block epilogue and diverge.

Instead, accumulate every eligible key and apply the cap only when the
promotions are materialized, keeping the smallest keys via the ordered
`BTreeSet`. The retained subset is now a deterministic function of the
block's reads, regardless of the order they were observed.

While here, rename the drop counter to `promotions_dropped_over_cap` and have
it record how many keys were dropped rather than only that the cap was hit, so
the metric reflects how far over the cap a block ran.
