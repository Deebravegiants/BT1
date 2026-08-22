# [?] fix(sei-cosmos): harden paginated RPC queries against DoS via limit, offset, and count_total caps (PLT-361) (#3494)

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2026-06-16
Source: https://github.com/sei-protocol/sei-chain/commit/53fc1face64f86995370fd7929095c71789a9445
Type: security-commit

## Details
fix(sei-cosmos): harden paginated RPC queries against DoS via limit, offset, and count_total caps (PLT-361) (#3494)

## Problem

Three separate vectors allow a single RPC call to trigger unbounded KV
store iteration:

1. **Limit too large** — `MaxLimit` was `math.MaxUint64`; callers could
request billions of items in one call.
2. **`count_total=true` unbounded scan** — after serving the requested
page, the paginator continued iterating the entire remaining store just
to populate `pagination.total`. Implicit `limit=0` also silently enabled
this behaviour.
3. **Offset too large** — no cap on `pagination.offset`; a caller with
`offset=1_000_000_000` forces the iterator to skip a billion entries
before serving a single result.
4. **`GetBlockWithTxs` allocation** — user-supplied `limit` was passed
directly into `make([]*txtypes.Tx, 0, limit)` before any validation.

## Changes

### `sei-cosmos/types/query/pagination.go`
- Lowers `MaxLimit` to `1_000`
- Adds `MaxOffset = 10_000` and `VerifyPaginationOffset()`; enforced in
`ParsePagination` and `paginate()`
- Adds `MaxScanLimit = 10_000` — fires when `count_total=true` and the
iterator travels more than `MaxScanLimit` entries *past the end of the
requested page* (`count > end + MaxScanLimit`), preventing full-store
counts while still allowing `count_total` on reasonably-sized stores
- Removes the implicit `countTotal = true` side-effect when `limit ==
0`; callers must opt in explicitly

### `sei-cosmos/types/query/filtered_pagination.go`
- Same `MaxOffset` and `MaxScanLimit` guards applied to
`FilteredPaginate` and `GenericFilteredPaginate`
- Fixes a bug in the original scan cap where `totalIter` (raw store
iterations) was compared against `end` (a filtered-hit count), causing
the limit to fire mid-page for selective filters — a query with a 1%

_Trimmed to 38 lines — full report: https://github.com/sei-protocol/sei-chain/commit/53fc1face64f86995370fd7929095c71789a9445_
