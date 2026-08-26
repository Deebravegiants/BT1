# [?] db, execmoduletester: fix data race in EnableDomain vs openFolder (#20068)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-03-22
Source: https://github.com/erigontech/erigon/commit/2f0f3a47180a94704e98fb404cd22d7677ddca56
Type: security-commit

## Details
db, execmoduletester: fix data race in EnableDomain vs openFolder (#20068)

## Summary

- Fix flaky `race-tests / tests-linux (core-rpc)` CI failure caused by a
data race between `Aggregator.EnableDomain()` and
`Aggregator.openFolder()`
- `TestHeadStorage`, `TestBlockReceiptStorage`, and sibling tests called
`EnableDomain(kv.RCacheDomain)` **after** `execmoduletester.New(t)`
returned — racing with a background pipeline goroutine spawned by
`InsertChain` → `UpdateForkChoice` → `SnapshotsStage` →
`agg.OpenFolder()` which reads `d.Disable`
- Add `WithEnableDomain` option to `execmoduletester` so the domain is
enabled right after DB creation, before `InsertChain` spawns any
background goroutines

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
