# [?] cmd/utils: correct --db.read.concurrency usage on read-tx exhaustion (#22848)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-07-29
Source: https://github.com/erigontech/erigon/commit/4d1b99b7dac1124a529bfef976294c47e384d825
Type: security-commit

## Details
cmd/utils: correct --db.read.concurrency usage on read-tx exhaustion (#22848)

One-line change to the `--db.read.concurrency` help text. The flag
claimed a behaviour the code does not have.

## The problem

`cmd/utils/flags.go:407` said:

> extra readers wait for a slot **rather than error**

That is only true for callers that do not opt into fail-fast
acquisition. The RPC layer does:

* `rpc/websocket.go:83` tags every WebSocket connection context with
`kv.WithNonBlockingAcquire`, unconditionally.
* `node/rpcstack.go:87-90` tags HTTP requests whenever the admission
handler is active — which is the default: `--rpc.max.concurrency`
defaults to `0` (`cmd/utils/flags.go:410-414`), and
`cmd/rpcdaemon/cli/config.go:764-775` resolves `0` to
`db.read.concurrency`, always ≥ 10.
* `db/kv/mdbx/kv_mdbx.go:700-705` then takes the `TryAcquire` branch and
returns `kv.ErrReadTxLimitExceeded` immediately instead of blocking.
* `rpc/handler.go:631-639` remaps that to JSON-RPC `-32005`, and
`rpc/http.go:239-241` surfaces it as HTTP 503 with `Retry-After`.

So under read-tx exhaustion an operator gets an overload response, not a
stalled request — the opposite of what `--help` promised.

## The fix

Only the second clause changes; the rest of the string is untouched:

> extra readers wait for a slot **by default, though some RPC paths
(HTTP/WebSocket) fail fast with an overload response**

## Why "some RPC paths" rather than naming HTTP outright


_Trimmed to 38 lines — full report: https://github.com/erigontech/erigon/commit/4d1b99b7dac1124a529bfef976294c47e384d825_
