# [?] cl/beacon: fix nil pointer panics in GetEthV1ValidatorAttestationData (#19783)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-03-10
Source: https://github.com/erigontech/erigon/commit/0f3624a17b53f5d0dbefae13943b6a3d1b7e0edf
Type: security-commit

## Details
cl/beacon: fix nil pointer panics in GetEthV1ValidatorAttestationData (#19783)

## Summary

- **`SyncedDataManager.CommitteeCount`** (`synced_data.go`): added
`accessLock.RLock()` + nil check on `headState`, consistent with every
other accessor in the same file. Fixes a panic when a validator client
polls `/eth/v1/validator/attestation_data` before Caplin has synced to
head. Also closes a check-then-act race in `pool.go` and
`committee_subscription.go` where `Syncing()` is checked before
`CommitteeCount` is called.
- **Debug-log defer** (`block_production.go`): guard against nil
`committeeIndex` in the deferred log closure, which is nil on two
early-return paths — pre-Electra requests missing the `committee_index`
query param, and Electra cache-hit returns (the `committeeIndex = &zero`
assignment is bypassed by the cache-hit early return at line 158).

## Reproduction

Start Erigon with a fresh `caplin/` directory (or right after node
restart) while a Lighthouse VC is actively polling. The VC calls `GET
/eth/v1/validator/attestation_data` before Caplin reaches head → panic
in HTTP handler goroutine with `runtime error: invalid memory address or
nil pointer dereference` at `CachingBeaconState.CommitteeCount(0x0,
...)`.

## Test plan

- [x] `go test ./cl/beacon/synced_data/... ./cl/beacon/handler/...
-short` passes
- [x] `make lint` clean
- [x] Observed panic no longer reproducible after fix

Generated with Claude.
