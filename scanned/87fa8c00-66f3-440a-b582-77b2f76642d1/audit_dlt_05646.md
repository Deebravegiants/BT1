# [?] [SharovBot] Fix data race on bheapCache in db/rawdb (#19606)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-03-04
Source: https://github.com/erigontech/erigon/commit/9a00f9a7456004643c3d2bf98513fefc29a9d8fe
Type: security-commit

## Details
[SharovBot] Fix data race on bheapCache in db/rawdb (#19606)

**[SharovBot]**

## Summary
- Fix DATA RACE between `TestBlockStorage` and `TestBadBlocks` in
`db/rawdb`
- Add `sync.RWMutex` to protect concurrent access to the package-level
`bheapCache` variable
- The variable was being read in `TruncateCanonicalHash` and written in
`ResetBadBlockCache` without synchronization

## Test plan
- [x] `go test -race ./db/rawdb/... -run
"TestBlockStorage|TestBadBlocks" -count=3` passes with no DATA RACE
- [x] `go build ./...` passes
- [x] No test files modified

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>
