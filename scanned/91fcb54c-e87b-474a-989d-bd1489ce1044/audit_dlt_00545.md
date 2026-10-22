# [?] rpc: fix panic in debug_traceBlockByHash with prestateTracer due to overflow (#22623)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-07-21
Source: https://github.com/erigontech/erigon/commit/70895fe56ff63b022bf8ed9adbaa9baafc0b1ef6
Type: security-commit

## Details
rpc: fix panic in debug_traceBlockByHash with prestateTracer due to overflow (#22623)

fixes #22607

## Summary

- Add an rpcdaemon exec-module regression using the real signed
transaction and independently verified pre/post state from the affected
block. The test reproduces the original `runtime error: makeslice: len
out of range` panic before the fix.
- Reject `int64` overflow before calculating the end of a padded memory
copy.
- Let `prestateTracer` skip CREATE2 account derivation when the opcode's
memory cannot be copied safely. The unexecutable CREATE2 no longer
aborts the trace, and the returned prestate matches Reth and Nethermind.

## Root cause

The CREATE2 offset and size were positive `int64` values, but their sum
exceeded `math.MaxInt64` and wrapped negative. `GetMemoryCopyPadded`
therefore mistook the range for data already present in empty EVM
memory, then passed the still-positive, enormous size to `make([]byte,
size)`, which panicked.

## Testing

- `go test ./execution/tracing/tracers/... ./rpc/jsonrpc -count=1`
- `make lint` (two consecutive clean runs)
- `make erigon integration`
