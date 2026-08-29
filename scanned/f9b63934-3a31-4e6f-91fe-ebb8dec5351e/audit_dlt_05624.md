# [?] rpc, node: fix nil-pointer panic in gzip batch flush race (#22338)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-07-09
Source: https://github.com/erigontech/erigon/commit/63cc7de5f83fbce21036eb4b0e7ecc922717c413
Type: security-commit

## Details
rpc, node: fix nil-pointer panic in gzip batch flush race (#22338)

## Summary

A JSON-RPC batch containing 2+ streamable methods ran each call on its
own goroutine, and each one invoked the shared gzip-streaming flush hook
installed on the request context. `gzipResponseWriter.Flush` is not safe
for concurrent use, so calling it from multiple goroutines raced on the
underlying `gzip.Writer` and could dereference a nil flate compressor,
crashing the node.

Batch sub-calls write into private per-item buffers rather than the HTTP
response writer, so the hook was never useful there in the first place.
Mask it out of the context used by batch sub-call goroutines instead of
hardening `gzipResponseWriter` itself, since it remains owned by a
single goroutine everywhere else.

Also hardens the hook mechanism itself: `WithGzipStreamingHook` now
panics if ever called with a nil hook, and `runMethod` guards the flush
call with `ok && flush != nil`, so the mechanism doesn't rely on the
hook always being stored as an untyped nil to stay safe.

Fixes #22334

## Tests

- Added `node/rpcstack_gzip_batch_race_test.go`
(`TestGzipHandlerBatchConcurrentStreamableFlush`): sends a real JSON-RPC
batch of 8 calls to a streamable method through the actual gzip
middleware and `rpc.Server`, with `Accept-Encoding: gzip`, and each
call's payload sized above `minGzipBodySize` so the fixed path still
gzips. Asserts `HTTP 200`, `Content-Encoding: gzip`, and that the
decoded batch contains all `n` responses with the expected ids/results —
not just reliance on `-race` to catch a regression. Before the fix,
running it with `-race` reliably reproduced both the data race and, on
some runs, the exact nil-pointer panic reported in the issue. After the
fix it passes cleanly and repeatably under `-race` (verified over 15
consecutive runs).

_Trimmed to 38 lines — full report: https://github.com/erigontech/erigon/commit/63cc7de5f83fbce21036eb4b0e7ecc922717c413_
