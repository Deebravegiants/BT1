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

Deliberate hedge. These HTTP-served paths do **not** fail fast:

| Path | Where | Behaviour |
|---|---|---|
| Engine API (auth) HTTP | `config.go:1001-1005` — built `limit=0,
tagAsRPC=false`, with a comment saying so | blocks |
| GraphQL | `config.go:952-956` routes `/graphql` before the tagged
handler | blocks |
| Healthcheck | `config.go:958-961`, same | blocks |
| Unix/TCP socket transport | `config.go:742-762`, no tag | blocks |
| Public HTTP with `--rpc.max.concurrency=-1` | admission control
disabled | blocks |

A tighter phrasing such as *"JSON-RPC over HTTP/WebSocket fails fast"*
was considered and rejected: the Engine API **is** JSON-RPC over HTTP
and deliberately blocks, so that wording would be wrong in a new way.
`some RPC paths` is vague but true; the exhaustive list belongs in prose
docs, not a help string.

## Relationship to #22799

This closes a source↔docs divergence that exists on `main` today.
`docs/site/docs/fundamentals/modules/rpc-daemon.md:51` already describes
the fail-fast behaviour (merged in #22415) while the Go string still
claimed the opposite. Open PR #22799 refines that same docs sentence;
the string in this PR is **byte-identical (548 chars)** to what #22799
lands, so once both merge, `erigon --help` and the docs help block agree
verbatim.

The two PRs are independent and can merge in either order — no docs
generator reads the Go source (`generate-llms.py` derives the exports
from the markdown pages), so nothing needs regenerating here.

## Testing

* `go build ./cmd/utils/` and `go vet ./cmd/utils/` — clean.
* No test, golden file, fixture, or docs generator asserts on this
string or on `--help` output, so nothing else changes. Verified across
`cmd/utils/flags_test.go`, `node/cli/helpers_test.go`, and a tree-wide
search for the literal.
* `cmd/utils/flags.go:407` is the only definition and the only
occurrence in Go sources.

## Two pre-existing issues noticed, not addressed here

Both are out of scope for a help-string fix; happy to file issues or
follow-up PRs if wanted.

1. **Engine API over WebSocket fails fast, contradicting the intent
stated for Engine over HTTP.** `createEngineListener` deliberately
leaves the engine HTTP stack untagged so CL↔EL calls block
(`config.go:1001-1005`), but its WS handler goes through
`engineSrv.WebsocketHandler` → the unconditional tag at
`rpc/websocket.go:83`. A CL speaking engine-over-WS can receive `-32005`
under read-tx exhaustion. Related: the comment at `config.go:1001`
refers to "TxPriorityRPC", an identifier that no longer exists anywhere
in the tree — the mechanism is `kv.WithNonBlockingAcquire`.
2. **The unchanged tail understates the floor.** It says a value below
the parallel-exec worker count "is raised to it", but `RoTxsLimit`
floors at `execWorkers + 23` (5 permanent + 2 read-ahead + 16 reserve —
`cmd/rpcdaemon/cli/httpcfg/http_cfg.go:38-62`). #22799 repeats the same
simplification in the docs, so correcting it means touching both.

Co-authored-by: Bloxster <gianni.morselli@erigon.tech>

### cmd/utils/flags.go
```diff
@@ -404,7 +404,7 @@ var (
 	}
 	DBReadConcurrencyFlag = cli.IntFlag{
 		Name:  "db.read.concurrency",
-		Usage: "Ceiling on concurrent open DB read transactions (MDBX read-tx semaphore); extra readers wait for a slot rather than error. Default scales as min(max(10, GOMAXPROCS*64), 9000) — kept well above CPU count because reads are I/O-bound, and capped below Go's ~10K OS-thread limit. A value below the parallel-exec worker count is raised to it (each worker holds a long-lived read tx, so a lower ceiling would deadlock); to actually reduce read concurrency, lower --exec.workers instead",
+		Usage: "Ceiling on concurrent open DB read transactions (MDBX read-tx semaphore); extra readers wait for a slot by default, though some RPC paths (HTTP/WebSocket) fail fast with an overload response. Default scales as min(max(10, GOMAXPROCS*64), 9000) — kept well above CPU count because reads are I/O-bound, and capped below Go's ~10K OS-thread limit. A value below the parallel-exec worker count is raised to it (each worker holds a long-lived read tx, so a lower ceiling would deadlock); to actually reduce read concurrency, lower --exec.workers instead",
 		Value: httpcfg.DefaultDBReadConcurrency(),
 	}
 	RpcMaxConcurrentRequestsFlag = cli.IntFlag{
```
