# [?] [SharovBot] execution/execmodule: fix DATA RACE on miningCancel channel teardown (#22842)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-07-29
Source: https://github.com/erigontech/erigon/commit/d532725c6bf25345c9470abf156542df9b182920
Type: security-commit

## Details
[SharovBot] execution/execmodule: fix DATA RACE on miningCancel channel teardown (#22842)

**[SharovBot]**

## Summary

Fix a DATA RACE detected in
`TestGetAssembledBlockHonorsCanceledContextWhenTxPoolIsBehindParent`.

## Root Cause

The `miningCancel` channel in `execmoduletester.New` was:
1. **Sent to** (non-blocking) by `builder.finishBlock` at
`finish.go:124` — to cancel an in-flight sealing task
2. **Closed** by a teardown goroutine when `mock.Ctx` is cancelled

A concurrent `close(ch)` + `ch <- v` on the same channel is a DATA RACE
(detected by Go's race detector as a `closechan` write racing with a
`chansend` read).

## Fix

Change `miningCancel` from an unbuffered channel that gets closed to a
**buffered channel (capacity 1)** that receives a non-blocking send on
shutdown. This eliminates the close-while-send race without changing
observable semantics:

- `finishBlock` already uses a non-blocking `select` when sending to
`sealCancel`
- No active sealer (`Merge`, `FakeEthash`) actually receives from the
`stop` channel passed to `engine.Seal()`
- The buffered capacity ensures the shutdown signal is not dropped if no
goroutine is listening at the moment of the send

## Testing

```
go test -race -count=3 -run TestGetAssembledBlockHonorsCanceledContextWhenTxPoolIsBehindParent ./execution/execmodule/...
```

_Trimmed to 38 lines — full report: https://github.com/erigontech/erigon/commit/d532725c6bf25345c9470abf156542df9b182920_
