# [?] [SharovBot] Fix data race between buildFiles and recalcVisibleFiles (#19590)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-03-04
Source: https://github.com/erigontech/erigon/commit/2db714813b45b85ec07c22d8460ca9f670b36b4c
Type: security-commit

## Details
[SharovBot] Fix data race between buildFiles and recalcVisibleFiles (#19590)

**[SharovBot]** Fix DATA RACE in `db/state/aggregator.go`

## Summary
- `buildFiles()` calls `BeginFilesRo()` on `Domain` and `InvertedIndex`
without holding `visibleFilesLock`, racing with `recalcVisibleFiles()`
which writes `_visible`/`_visibleFiles` fields under the same lock
- Wraps the `BeginFilesRo()` calls in `buildFiles()` with
`a.visibleFilesLock.RLock()`/`RUnlock()` to synchronize with the writer,
matching the pattern already used in `Aggregator.BeginFilesRo()`

## Test plan
- [x] `go build ./...` passes
- [x] `go test -race ./execution/verify/... -run
TestHistoryVerification_WithUserTransactions` passes 3 consecutive times
with no DATA RACE
- [x] `go test -race ./db/state/...` passes with no DATA RACE

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---------

Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>
