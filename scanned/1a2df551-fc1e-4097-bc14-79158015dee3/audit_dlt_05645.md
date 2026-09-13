# [?] [SharovBot] Fix data race in ExecModuleTester.SendMessageToRandomPeers (#19713)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-03-07
Source: https://github.com/erigontech/erigon/commit/6a1f2077f636005d510bc13fe84b5a4f408a4766
Type: security-commit

## Details
[SharovBot] Fix data race in ExecModuleTester.SendMessageToRandomPeers (#19713)

## Summary
- Add `sentMessagesMu` mutex to `ExecModuleTester` to protect concurrent
access to the `sentMessages` slice
- Guard all append operations in `SendMessageByMinBlock`,
`SendMessageById`, `SendMessageToRandomPeers`, and `SendMessageToAll`
with the mutex
- Guard read access in `SentMessage` with the mutex
- Fixes data race detected in `TestAssembleBlockWithFreshlyAddedTxns`
where `BroadcastPooledTxns` and `AnnouncePooledTxns` concurrently call
`SendMessageToRandomPeers`

## Test plan
- [x] `go test -race ./execution/execmodule/... -count=3 -run
TestAssembleBlockWithFreshlyAddedTxns` passes with no DATA RACE warnings
- [x] `go build ./...` passes
- [x] No `*_test.go` files modified

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>
