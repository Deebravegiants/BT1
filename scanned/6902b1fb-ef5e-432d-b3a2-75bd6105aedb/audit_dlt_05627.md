# [?] cl/forkchoice: fix data race on GetHead fast-path return (#21988)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-06-24
Source: https://github.com/erigontech/erigon/commit/6b98ebc6a96c9d1a6440a2a863717a119614674b
Type: security-commit

## Details
cl/forkchoice: fix data race on GetHead fast-path return (#21988)

## Summary
- Fix data race between `GetHead` (read) and `onTickPerSlot` (write) on
`ForkChoiceStore.headHash`/`headSlot`
- The fast-path cache hit in `GetHead` was reading struct fields
**after** releasing `RLock`, racing with `onTickPerSlot` clearing
`headHash` under the write lock
- Copy `headHash` and `headSlot` into locals while `RLock` is still
held, return the locals after unlock

Fixes #21936

## Test plan
- [x] `go test -race ./cl/phase1/forkchoice/...` — pass
- [x] `go build -race ./cl/...` — pass
- [x] `make lint` — 0 issues
