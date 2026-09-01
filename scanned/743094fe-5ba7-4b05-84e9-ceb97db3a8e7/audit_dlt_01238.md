# [?] fix: disable FcuBackgroundCommit in test mock (race condition fix) (#19333)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-02-20
Source: https://github.com/erigontech/erigon/commit/89a91a23fd04df9f69b006185d3169db5e52b3ec
Type: security-commit

## Details
fix: disable FcuBackgroundCommit in test mock (race condition fix) (#19333)

# fix(tests): remove FcuBackgroundCommit/FcuBackgroundPrune overrides in
test mock

## Summary

Remove explicit overrides of `FcuBackgroundCommit` and
`FcuBackgroundPrune` in the
execution module tester so the production defaults from
`ethconfig.Defaults` are used.

## Root Cause

`execution/execmodule/execmoduletester/exec_module_tester.go` was
explicitly setting:

```go
cfg.FcuBackgroundCommit = true
cfg.FcuBackgroundPrune = true
```

However, `FcuBackgroundCommit = true` is explicitly **not
production-ready** — the
production default is `false` with a comment:

```go
// node/ethconfig/config.go
FcuBackgroundCommit: false, // to enable, we need to 1) have rawdb API go via execctx and 2) revive Coherent cache for rpcdaemon
```

Enabling it in tests caused background goroutines to race against test
goroutines
in `SharedDomains`, leading to flaky failures under `-race`:

• `[4/6 Execution] Wrong trie root of block N` — state hash diverges due
to concurrent commits
• `TestSendRawTransactionSyncTimeout` — port conflicts from RPC server

_Trimmed to 38 lines — full report: https://github.com/erigontech/erigon/commit/89a91a23fd04df9f69b006185d3169db5e52b3ec_
