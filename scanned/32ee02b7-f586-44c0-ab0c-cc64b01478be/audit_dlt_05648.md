# [?] [SharovBot] fix Amsterdam signer support and BAL non-determinism (#19434)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-03-02
Source: https://github.com/erigontech/erigon/commit/9d1c662dcb3436dfc636cbb5e4aaae1593c86c87
Type: security-commit

## Details
[SharovBot] fix Amsterdam signer support and BAL non-determinism (#19434)

**[SharovBot]** Fix Amsterdam signer support and BAL non-determinism in
parallel execution

## Summary

- **Amsterdam signer**: Add Amsterdam fork handling in `MakeSigner` and
`LatestSigner` so that `setCode` and `blob` tx types are supported when
only `AmsterdamTime` is configured (without `PragueTime`).
- **BAL non-determinism (parallel execution)**: Fix multiple sources of
non-deterministic BAL (EIP-7928) hashes during parallel tx execution:
- Sort `ApplyVersionedWrites` output by (Address, Path, Key) for
deterministic application order
- Sync `WaitGroup` before block finalization to ensure all prior tx
state is applied to `pe.rs`
- Flush merged writes (execution + finalize) to the version map so later
tx finalizations see the full post-tx state
- Read coinbase balance from the version map (via
`versionedStateReader`) rather than a stale `pe.rs` snapshot
- Sync `CodeHash` in `getStateObject` when code is loaded from the
version map, preventing the "revert to original" optimization from
incorrectly deleting code writes
- **Atomic version map flush**: `FlushVersionedWrites` now holds a
single lock for all writes, preventing concurrent workers from observing
a partially-flushed state (e.g. seeing `AddressPath` but not the
corresponding `CodePath` from the same transaction)

## Test plan

- [x] `execution/tests` package compiles without errors
- [x] `TestExecutionSpecBlockchainDevnet/amsterdam` passes in a single
run
- [x] `TestExecutionSpecBlockchainDevnet/amsterdam` passes 30
consecutive times with `-count=1`
- [x] `TestExecutionSpecBlockchainDevnet/prague/eip7702` passes (no
regression)


_Trimmed to 38 lines — full report: https://github.com/erigontech/erigon/commit/9d1c662dcb3436dfc636cbb5e4aaae1593c86c87_
