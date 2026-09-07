# [?] db/state: fix data race on Aggregator stepSize/stepsInFrozenFile (#20100)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-03-23
Source: https://github.com/erigontech/erigon/commit/2660b49705e5d69ed4d3510cf287696bb0b22173
Type: security-commit

## Details
db/state: fix data race on Aggregator stepSize/stepsInFrozenFile (#20100)

## Summary
- Convert `Aggregator.stepSize` and `Aggregator.stepsInFrozenFile` from
`uint64` to `atomic.Uint64`
- `ReloadErigonDBSettings()` writes these fields (from the staged sync
pipeline goroutine) while `MergeLoop` reads them concurrently via
`StepSize()`/`StepsInFrozenFile()`, causing a data race detected by the
race-tests CI shard
- All read sites use `.Load()`, all write sites use `.Store()`

## Test plan
- [x] `go build ./...` passes
- [x] `go test -short ./db/state/...` passes
- [x] `go test -run TestEngineApiBuiltBlockStateMatchesValidation
./execution/engineapi/` passes
- [ ] CI race-tests shard passes (was the failing check)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
