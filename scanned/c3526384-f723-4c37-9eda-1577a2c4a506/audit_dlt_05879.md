# [?] fix(prover): index-out-of-range panic in merkle proof verification (#3453)

## Summary
Severity: Unknown
Chain: Linea
Component: Consensys/linea-monorepo
Published: 2026-06-26
Source: https://github.com/LFDT-Lineth/lineth-monorepo/commit/ea9dc73d6de8e6da4f5e3a72fc2a0ece97b9b2ea
Type: security-commit

## Details
fix(prover): index-out-of-range panic in merkle proof verification (#3453)

* fix(prover): make CoWindowRange cover all windows, not just the last

CoWindowRange set foundAny only after an early continue, so it stayed
false: each padded window overwrote start/stop instead of being merged,
leaving the min/max union as dead code. Combining two distinct windows
returned only the last window's range.

Set foundAny in the first branch so the range spans every window.

* fix(prover): fix index-out-of-range panic in Merkle proof verification

TernaryCtx.Run iterated i <= stop over the half-open range returned by
CoCompactRange, reading one element past the end when the active range
reached the last row of the column. This panicked with "index out of
range [N] with length N" during Merkle proof verification on near-full
state-manager batches.
