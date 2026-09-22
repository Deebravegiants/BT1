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
pass rate and `limit=100` could be rejected before accumulating its
first result
- Replaces the single mixed-space guard with a two-phase approach:
- **Phase 1** (`numHits < end`): caps raw iterations at `end +
MaxScanLimit` — prevents full-store walks when the filter produces too
few hits to fill the page (no-hits DoS path); cannot fire once the page
starts completing
- **Phase 2** (`numHits >= end`): tracks iterations after page
completion via `pageCompleteIter` and caps at `MaxScanLimit` — limits
post-page `count_total` scanning without any risk of mid-page
interference

### `sei-cosmos/x/auth/tx/service.go`
- Calls `pagination.VerifyPaginationLimit(limit)` before
`make([]*txtypes.Tx, 0, limit)` in `GetBlockWithTxs`

## Behaviour summary

| Request | Before | After |
|---|---|---|
| `limit > 1,000` | accepted, full scan | `InvalidArgument` |
| `limit = 0` | default 100 items + implicit `count_total=true` |
default 100 items, no implicit count |
| `count_total=true`, store has > `end + 10,000` entries | full store
scan | `InvalidArgument` |
| `count_total=true`, selective filter, `numHits < end` | rejected
mid-page assembly | completes page; errors only if filter is too sparse
to fill page within `end + MaxScanLimit` raw iterations |
| `offset > 10,000` | accepted, skips N entries | `InvalidArgument` |
| `GetBlockWithTxs` with `limit=1_000_000_000` | allocates ~1 GB slice |
`InvalidArgument` |

## Regression risk

Breaking change for clients sending `limit > 1,000`, `offset > 10,000`,
or relying on `limit=0` to return a total count. Clients should use
`limit ≤ 1,000`, follow `next_key` for subsequent pages, and set
`count_total=true` explicitly only when the store is known to be small.

`ExportGenesis` and the `TotalSupply` invariant were migrated to
`collectAllTotalSupply`, which internally paginates at `MaxLimit` per
page to collect all denominations without being blocked by the new
limit.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---------

Co-authored-by: Masih H. Derkani <m@derkani.org>

### sei-cosmos/types/query/filtered_pagination.go
```diff
@@ -5,16 +5,17 @@ import (
 
 	"github.com/sei-protocol/sei-chain/sei-cosmos/codec"
 	"github.com/sei-protocol/sei-chain/sei-cosmos/store/types"
+	"google.golang.org/grpc/codes"
+	"google.golang.org/grpc/status"
 )
 
 // FilteredPaginate does pagination of all the results in the PrefixStore based on the
-// provided PageRequest. onResult should be used to do actual unmarshaling and filter the results.
-// If key is provided, the pagination uses the optimized querying.
-// If offset is used, the pagination uses lazy filtering i.e., searches through all the records.
-// The accumulate parameter represents if the response is valid based on the offset given.
-// It will be false for the results (filtered) < offset  and true for `offset > accumulate <= end`.
-// When accumulate is set to true the current result should be appended to the result set returned
-// to the client.
+// provided PageRequest. onResult does the unmarshaling and filtering.
+// Key-based pagination is optimized; offset-based pagination lazily walks all records.
+//
+// Iteration is capped at MaxScanLimit entries to prevent unbounded store walks. Use key-based
+// pagination for reliable traversal of sparse datasets, as the nextKey could be nil when the
+// page is full and the scan limit is reached.
 func FilteredPaginate(
 	prefixStore types.KVStore,
 	pageRequest *PageRequest,
@@ -36,27 +37,38 @@ func FilteredPaginate(
 		return nil, fmt.Errorf("invalid request, either offset or key is expected, got both")
 	}
 
+	if err := VerifyPaginationOffset(offset); err != nil {
+		return nil, err
+	}
+
 	if limit == 0 {
 		limit = DefaultLimit
+	}
 
-		// count total results when the limit is zero/not supplied
-		countTotal = true
+	if err := VerifyPaginationLimit(limit); err != nil {
+		return nil, err
 	}
 
 	if len(key) != 0 {
 		iterator := getIterator(prefixStore, key, reverse)
 		defer func() { _ = iterator.Close() }()
 
 		var (
-			numHits uint64
-			nextKey []byte
+			numHits   uint64
+			nextKey   []byte
+			totalIter uint64
 		)
 
 		for ; iterator.Valid(); iterator.Next() {
+			totalIter++
 			if numHits == limit {
 				nextKey = iterator.Key()
 				break
 			}
+			if totalIter > MaxScanLimit {
+				return nil, status.Errorf(codes.InvalidArgument,
+					"scanned more than %d entries without filling the page; use a more specific key prefix or reduce limit", MaxScanLimit)
+			}
 
 			if iterator.Error() != nil {
 				return nil, iterator.Error()
@@ -83,11 +95,30 @@ func FilteredPaginate(
 	end := offset + limit
 
 	var (
-		numHits uint64
-		nextKey []byte
+		numHits          uint64
+		nextKey          []byte
+		totalIter        uint64
+		pageCompleteIter uint64
 	)
 
 	for ; iterator.Valid(); iterator.Next() {
+		totalIter++
+		// Phase 1: page not yet complete — cap raw iterations to prevent full-store
+		// walks when the filter produces too few hits to fill the page.
+		if numHits < end && totalIter > offset+MaxScanLimit {
+			return nil, status.Errorf(codes.InvalidArgument,
+				"scanned more than %d entries without filling the page; use key-based pagination instead", MaxScanLimit)
+		}
+		// Phase 2: page complete — cap how far past the page we scan for nextKey/count_total.
+		if pageCompleteIter > MaxScanLimit {
+			if !countTotal {
+				// Page is already assembled; no next hit found within scan window → no next page.
+				break
+			}
+			return nil, status.Errorf(codes.InvalidArgument,
+				"scanned more than %d entries past the end of the page; use key-based pagination instead", MaxScanLimit)
+		}
+
 		if iterator.Error() != nil {
 			return nil, iterator.Error()
 		}
@@ -102,6 +133,10 @@ func FilteredPaginate(
 			numHits++
 		}
 
+		if numHits >= end {
+			pageCompleteIter++
+		}
+
 		if numHits == end+1 {
 			nextKey = iterator.Key()
 
@@ -127,6 +162,8 @@ func FilteredPaginate(
 // If offset is used, the pagination uses lazy filtering i.e., searches through all the records.
 // The resulting slice (of type F) can be of a different type than the one being iterated through
 // (type T), so it's possible to do any necessary transformation inside the onResult function.
+//
+// Scan limits: same semantics as FilteredPaginate — see its documentation for details.
 func GenericFilteredPaginate[T codec.ProtoMarshaler, F codec.ProtoMarshaler](
 	cdc codec.BinaryCodec,
 	prefixStore types.KVStore,
@@ -150,27 +187,38 @@ func GenericFilteredPaginate[T codec.ProtoMarshaler, F codec.ProtoMarshaler](
 		return results, nil, fmt.Errorf("invalid request, either offset or key is expected, got both")
 	}
 
+	if err := VerifyPaginationOffset(offset); err != nil {
+		return results, nil, err
+	}
+
 	if limit == 0 {
 		limit = DefaultLimit
+	}
 
-		// count total results when the limit is zero/not supplied
-		countTotal = true
+	if err := VerifyPaginationLimit(limit); err != nil {
+		return results, nil, err
 	}
 
 	if len(key) != 0 {
 		iterator := getIterator(prefixStore, key, reverse)
 		defer func() { _ = iterator.Close() }()
 
 		var (
-			numHits uint64
-			nextKey []byte
+			numHits   uint64
+			nextKey   []byte
+			totalIter uint64
 		)
 
 		for ; iterator.Valid(); iterator.Next() {
+			totalIter++
 			if numHits == limit {
 				nextKey = iterator.Key()
 				break
 			}
+			if totalIter > MaxScanLimit {
+				return nil, nil, status.Errorf(codes.InvalidArgument,
+					"scanned more than %d entries without filling the page; use a more specific key prefix or reduce limit", MaxScanLimit)
+			}
 
 			if iterator.Error() != nil {
 				return nil, nil, iterator.Error()
@@ -205,11 +253,30 @@ func GenericFilteredPaginate[T codec.ProtoMarshaler, F codec.ProtoMarshaler](
 	end := offset + limit
 
 	var (
-		numHits uint64
-		nextKey []byte
+		numHits          uint64
+		nextKey          []byte
+		totalIter        uint64
+		pageCompleteIter uint64
 	)
 
 	for ; iterator.Valid(); iterator.Next() {
+		totalIter++
+		// Phase 1: page not yet complete — cap raw iterations to prevent full-store
+		// walks when the filter produces too few hits to fill the page.
+		if numHits < end && totalIter > offset+MaxScanLimit {
+			return nil, nil, status.Errorf(codes.InvalidArgument,
+				"scanned more than %d entries without filling the page; use key-based pagination instead", MaxScanLimit)
+		}
+		// Phase 2: page complete — cap how far past the page we scan for nextKey/count_total.
+		if pageCompleteIter > MaxScanLimit {
+			if !countTotal {
+				// Page is already assembled; no next hit found within scan window → no next page.
+				break
+			}
+			return nil, nil, status.Errorf(codes.InvalidArgument,
+				"scanned more than %d entries past the end of the page; use key-based pagination instead", MaxScanLimit)
+		}
+
 		if iterator.Error() != nil {
 			return nil, nil, iterator.Error()
 		}
@@ -234,6 +301,10 @@ func GenericFilteredPaginate[T codec.ProtoMarshaler, F codec.ProtoMarshaler](
 			numHits++
 		}
 
+		if numHits >= end {
+			pageCompleteIter++
+		}
+
 		if numHits == end+1 {
 			if nextKey == nil {
 				nextKey = iterator.Key()
```

### sei-cosmos/types/query/filtered_pagination_test.go
```diff
@@ -47,7 +47,7 @@ func (s *paginationTestSuite) TestFilteredPaginations() {
 	s.Require().NoError(err)
 	s.Require().NotNil(res)
 	s.Require().Equal(4, len(balances))
-	s.Require().Equal(uint64(4), res.Total)
+	s.Require().Equal(uint64(0), res.Total)
 	s.Require().Nil(res.NextKey)
 
 	s.T().Log("verify nextKey is returned if there are more results")
@@ -79,7 +79,7 @@ func (s *paginationTestSuite) TestFilteredPaginations() {
 	s.Require().NoError(err)
 	s.Require().NotNil(res)
 	s.Require().Equal(4, len(balances))
-	s.Require().Equal(uint64(4), res.Total)
+	s.Require().Equal(uint64(0), res.Total)
 
 	s.T().Log("verify with offset")
 	pageReq = &query.PageRequest{Offset: 2, Limit: 2}
@@ -122,7 +122,7 @@ func (s *paginationTestSuite) TestReverseFilteredPaginations() {
 	s.Require().NoError(err)
 	s.Require().NotNil(res)
 	s.Require().Equal(10, len(balns))
-	s.Require().Equal(uint64(10), res.Total)
+	s.Require().Equal(uint64(0), res.Total)
 	s.Require().Nil(res.NextKey)
 
 	s.T().Log("verify default limit")
@@ -131,7 +131,7 @@ func (s *paginationTestSuite) TestReverseFilteredPaginations() {
 	s.Require().NoError(err)
 	s.Require().NotNil(res)
 	s.Require().Equal(10, len(balns))
-	s.Require().Equal(uint64(10), res.Total)
+	s.Require().Equal(uint64(0), res.Total)
 
 	s.T().Log("verify nextKey is returned if there are more results")
 	pageReq = &query.PageRequest{Limit: 2, CountTotal: true, Reverse: true}
@@ -170,6 +170,110 @@ func (s *paginationTestSuite) TestReverseFilteredPaginations() {
 
 }
 
+func (s *paginationTestSuite) TestFilteredPaginateMaxLimitExceeded() {
+	app, ctx, _ := setupTest(s.T())
+	store := ctx.KVStore(app.GetKey(types.StoreKey))
+
+	_, err := query.FilteredPaginate(store, &query.PageRequest{Limit: query.MaxLimit + 1}, func(_ []byte, _ []byte, _ bool) (bool, error) {
+		return false, nil
+	})
+	s.Require().Error(err)
+	s.Require().Contains(err.Error(), "exceeds maximum allowed limit")
+}
+
+func (s *paginationTestSuite) TestFilteredPaginateOffsetExceedsMax() {
+	app, ctx, _ := setupTest(s.T())
+	kvStore := ctx.KVStore(app.GetKey(types.StoreKey))
+
+	_, err := query.FilteredPaginate(kvStore, &query.PageRequest{Offset: query.MaxOffset + 1}, func(_ []byte, _ []byte, _ bool) (bool, error) {
+		return false, nil
+	})
+	s.Require().Error(err)
+	s.Require().Contains(err.Error(), "exceeds maximum allowed offset")
+
+	_, err = query.FilteredPaginate(kvStore, &query.PageRequest{Offset: query.MaxOffset}, func(_ []byte, _ []byte, _ bool) (bool, error) {
+		return false, nil
+	})
+	s.Require().NoError(err)
+}
+
+func (s *paginationTestSuite) TestFilteredPaginateCountTotalScanLimitExceeded() {
+	app, ctx, _ := setupTest(s.T())
+	kvStore := prefix.NewStore(ctx.KVStore(app.GetKey(types.StoreKey)), []byte("filteredscanlimit/"))
+
+	numItems := int(query.MaxScanLimit) + 2
+	for i := 0; i < numItems; i++ {
+		kvStore.Set([]byte(fmt.Sprintf("%08d", i)), []byte("v"))
+	}
+
+	_, err := query.FilteredPaginate(kvStore, &query.PageRequest{Limit: 1, CountTotal: true}, func(_ []byte, _ []byte, _ bool) (bool, error) {
+		return true, nil
+	})
+	s.Require().Error(err)
+	s.Require().Contains(err.Error(), "scanned more than")
+}
+
+func (s *paginationTestSuite) TestFilteredPaginateCountTotalScanLimitExceededNoHits() {
+	app, ctx, _ := setupTest(s.T())
+	kvStore := prefix.NewStore(ctx.KVStore(app.GetKey(types.StoreKey)), []byte("filteredscanlimitnohits/"))
+
+	// Phase 1 fires when totalIter > offset + MaxScanLimit = 10001
+	pageReq := &query.PageRequest{Offset: 1, CountTotal: true}
+	numItems := int(query.MaxScanLimit) + 2
+	for i := 0; i < numItems; i++ {
+		kvStore.Set([]byte(fmt.Sprintf("%08d", i)), []byte("v"))
+	}
+
+	// filter returns no hits — numHits never reaches end, Phase 1 guard must fire
+	_, err := query.FilteredPaginate(kvStore, pageReq, func(_ []byte, _ []byte, _ bool) (bool, error) {
+		return false, nil
+	})
+	s.Require().Error(err)
+	s.Require().Contains(err.Error(), "scanned more than")
+}
+
+func (s *paginationTestSuite) TestFilteredPaginateSparseFilterFillsPageWithinScanLimit() {
+	app, ctx, _ := setupTest(s.T())
+	kvStore := prefix.NewStore(ctx.KVStore(app.GetKey(types.StoreKey)), []byte("filteredsparse/"))
+
+	numItems := int(query.MaxScanLimit)
+	for i := 0; i < numItems; i++ {
+		value := "miss"
+		if i%1000 == 0 {
+			value = "hit"
+		}
+		kvStore.Set([]byte(fmt.Sprintf("%08d", i)), []byte(value))
+	}
+
+	var hits [][]byte
+	onResult := func(key []byte, value []byte, accumulate bool) (bool, error) {
+		if string(value) != "hit" {
+			return false, nil
+		}
+		if accumulate {
+			hits = append(hits, key)
+		}
+		return true, nil
+	}
+
+	res, err := query.FilteredPaginate(kvStore, &query.PageRequest{Limit: 5}, onResult)
+	s.Require().NoError(err)
+	s.Require().NotNil(res)
+	s.Require().Equal(5, len(hits))
+	s.Require().Equal("00000000", string(hits[0]))
+	s.Require().Equal("00004000", string(hits[4]))
+	s.Require().Equal("00005000", string(res.NextKey))
+
+	s.T().Log("count_total scans the rest of the store, still within the Phase 2 cap")
+	hits = nil
+	res, err = query.FilteredPaginate(kvStore, &query.PageRequest{Limit: 5, CountTotal: true}, onResult)
+	s.Require().NoError(err)
+	s.Require().NotNil(res)
+	s.Require().Equal(5, len(hits))
+	s.Require().Equal(uint64(10), res.Total)
+	s.Require().NotNil(res.NextKey)
+}
+
 func execFilterPaginate(store sdk.KVStore, pageReq *query.PageRequest, appCodec codec.Codec) (balances sdk.Coins, res *query.PageResponse, err error) {
 	balancesStore := prefix.NewStore(store, types.BalancesPrefix)
 	accountStore := prefix.NewStore(balancesStore, address.MustLengthPrefix(addr1))
```

### sei-cosmos/types/query/pagination.go
```diff
@@ -2,7 +2,6 @@ package query
 
 import (
 	"fmt"
-	"math"
 
 	"github.com/sei-protocol/sei-chain/sei-cosmos/store/types"
 	db "github.com/tendermint/tm-db"
@@ -14,9 +13,15 @@ import (
 // if the `limit` is not supplied, paginate will use `DefaultLimit`
 const DefaultLimit = 100
 
-// MaxLimit is the maximum limit the paginate function can handle
-// which equals the maximum value that can be stored in uint64
-const MaxLimit = math.MaxUint64
+// MaxLimit is the maximum limit per page the paginate function can handle
+const MaxLimit = uint64(1_000)
+
+// MaxScanLimit is the maximum number of store entries the paginate function
+// will iterate past the page end when count_total is requested.
+const MaxScanLimit = uint64(10_000)
+
+// MaxOffset is the maximum offset allowed in a PageRequest.
+const MaxOffset = uint64(10_000)
 
 // ParsePagination validate PageRequest and returns page number & limit.
 func ParsePagination(pageReq *PageRequest) (page, limit int, err error) {
@@ -30,47 +35,68 @@ func ParsePagination(pageReq *PageRequest) (page, limit int, err error) {
 	if offset < 0 {
 		return 1, 0, status.Error(codes.InvalidArgument, "offset must greater than 0")
 	}
+	// #nosec G115 -- offset is non-negative after validation above; fits in uint64
+	if offsetErr := VerifyPaginationOffset(uint64(offset)); offsetErr != nil {
+		return 1, 0, offsetErr
+	}
 
 	if limit < 0 {
 		return 1, 0, status.Error(codes.InvalidArgument, "limit must greater than 0")
 	} else if limit == 0 {
 		limit = DefaultLimit
 	}
 
+	// #nosec G115 -- limit is positive after validation above; fits in uint64
+	if limitErr := VerifyPaginationLimit(uint64(limit)); limitErr != nil {
+		return 1, 0, limitErr
+	}
+
 	page = offset/limit + 1
 
 	return page, limit, nil
 }
 
+func VerifyPaginationLimit(limit uint64) error {
+	if limit > MaxLimit {
+		return status.Errorf(codes.InvalidArgument, "limit %d exceeds maximum allowed limit %d", limit, MaxLimit)
+	}
+	return nil
+}
+
+func VerifyPaginationOffset(offset uint64) error {
+	if offset > MaxOffset {
+		return status.Errorf(codes.InvalidArgument, "offset %d exceeds maximum allowed offset %d", offset, MaxOffset)
+	}
+	return nil
+}
+
 // Paginate does pagination of all the results in the PrefixStore based on the
 // provided PageRequest. onResult should be used to do actual unmarshaling.
 func Paginate(
 	prefixStore types.KVStore,
 	pageRequest *PageRequest,
 	onResult func(key []byte, value []byte) error,
 ) (*PageResponse, error) {
-
-	// if the PageRequest is nil, use default PageRequest
 	if pageRequest == nil {
 		pageRequest = &PageRequest{}
 	}
-
 	offset := pageRequest.Offset
 	key := pageRequest.Key
 	limit := pageRequest.Limit
-	countTotal := pageRequest.CountTotal
-	reverse := pageRequest.Reverse
-
+	if limit == 0 {
+		limit = DefaultLimit
+	}
 	if offset > 0 && key != nil {
 		return nil, fmt.Errorf("invalid request, either offset or key is expected, got both")
 	}
-
-	if limit == 0 {
-		limit = DefaultLimit
-
-		// count total results when the limit is zero/not supplied
-		countTotal = true
+	if err := VerifyPaginationLimit(limit); err != nil {
+		return nil, err
 	}
+	if err := VerifyPaginationOffset(offset); err != nil {
+		return nil, err
+	}
+	countTotal := pageRequest.CountTotal
+	reverse := pageRequest.Reverse
 
 	if len(key) != 0 {
 		iterator := getIterator(prefixStore, key, reverse)
@@ -80,7 +106,6 @@ func Paginate(
 		var nextKey []byte
 
 		for ; iterator.Valid(); iterator.Next() {
-
 			if count == limit {
 				nextKey = iterator.Key()
 				break
@@ -92,7 +117,6 @@ func Paginate(
 			if err != nil {
 				return nil, err
 			}
-
 			count++
 		}
 
@@ -112,6 +136,11 @@ func Paginate(
 	for ; iterator.Valid(); iterator.Next() {
 		count++
 
+		if count > end+MaxScanLimit {
+			return nil, status.Errorf(codes.InvalidArgument,
+				"scanned more than %d entries past the end of the page; use key-based pagination instead", MaxScanLimit)
+		}
+
 		if count <= offset {
 			continue
 		}
```

### sei-cosmos/types/query/pagination_test.go
```diff
@@ -15,6 +15,7 @@ import (
 	"github.com/sei-protocol/sei-chain/sei-cosmos/codec"
 	"github.com/sei-protocol/sei-chain/sei-cosmos/crypto/keys/secp256k1"
 	"github.com/sei-protocol/sei-chain/sei-cosmos/store"
+	"github.com/sei-protocol/sei-chain/sei-cosmos/store/prefix"
 	sdk "github.com/sei-protocol/sei-chain/sei-cosmos/types"
 	"github.com/sei-protocol/sei-chain/sei-cosmos/types/query"
 	"github.com/sei-protocol/sei-chain/sei-cosmos/x/bank/types"
@@ -56,6 +57,37 @@ func (s *paginationTestSuite) TestParsePagination() {
 	s.Require().NoError(err)
 	s.Require().Equal(page, 1)
 	s.Require().Equal(limit, 10)
+
+	s.T().Log("verify limit equal to MaxLimit is accepted")
+	pageReq = &query.PageRequest{Limit: query.MaxLimit}
+	_, _, err = query.ParsePagination(pageReq)
+	s.Require().NoError(err)
+
+	s.T().Log("verify limit exceeding MaxLimit is rejected")
+	pageReq = &query.PageRequest{Limit: query.MaxLimit + 1}
+	_, _, err = query.ParsePagination(pageReq)
+	s.Require().Error(err)
+	s.Require().Contains(err.Error(), "exceeds maximum allowed limit")
+
+	s.T().Log("verify offset equal to MaxOffset is accepted")
+	pageReq = &query.PageRequest{Offset: query.MaxOffset, Limit: 1}
+	_, _, err = query.ParsePagination(pageReq)
+	s.Require().NoError(err)
+
+	s.T().Log("verify offset exceeding MaxOffset is rejected")
+	pageReq = &query.PageRequest{Offset: query.MaxOffset + 1, Limit: 1}
+	_, _, err = query.ParsePagination(pageReq)
+	s.Require().Error(err)
+	s.Require().Contains(err.Error(), "exceeds maximum allowed offset")
+}
+
+func (s *paginationTestSuite) TestPaginateMaxLimitExceeded() {
+	app, ctx, _ := setupTest(s.T())
+	store := ctx.KVStore(app.GetKey(types.StoreKey))
+
+	_, err := query.Paginate(store, &query.PageRequest{Limit: query.MaxLimit + 1}, func(_, _ []byte) error { return nil })
+	s.Require().Error(err)
+	s.Require().Contains(err.Error(), "exceeds maximum allowed limit")
 }
 
 func (s *paginationTestSuite) TestPagination() {
@@ -77,12 +109,12 @@ func (s *paginationTestSuite) TestPagination() {
 	app.AccountKeeper.SetAccount(ctx, acc1)
 	s.Require().NoError(apptesting.FundAccount(app.BankKeeper, ctx, addr1, balances))
 
-	s.T().Log("verify empty page request results a max of defaultLimit records and counts total records")
+	s.T().Log("verify empty page request results a max of defaultLimit records without total count")
 	pageReq := &query.PageRequest{}
 	request := types.NewQueryAllBalancesRequest(addr1, pageReq)
 	res, err := queryClient.AllBalances(gocontext.Background(), request)
 	s.Require().NoError(err)
-	s.Require().Equal(res.Pagination.Total, uint64(numBalances))
+	s.Require().Equal(res.Pagination.Total, uint64(0))
 	s.Require().NotNil(res.Pagination.NextKey)
 	s.Require().LessOrEqual(res.Balances.Len(), defaultLimit)
 
@@ -291,6 +323,35 @@ func (s *paginationTestSuite) TestReversePagination() {
 	s.Require().Nil(res.Pagination.NextKey)
 }
 
+func (s *paginationTestSuite) TestPaginateOffsetExceedsMax() {
+	app, ctx, _ := setupTest(s.T())
+	kvStore := ctx.KVStore(app.GetKey(types.StoreKey))
+
+	_, err := query.Paginate(kvStore, &query.PageRequest{Offset: query.MaxOffset + 1}, func(_, _ []byte) error { return nil })
+	s.Require().Error(err)
+	s.Require().Contains(err.Error(), "exceeds maximum allowed offset")
+
+	_, err = query.Paginate(kvStore, &query.PageRequest{Offset: query.MaxOffset}, func(_, _ []byte) error { return nil })
+	s.Require().NoError(err)
+}
+
+func (s *paginationTestSuite) TestPaginateCountTotalScanLimitExceeded() {
+	app, ctx, _ := setupTest(s.T())
+	// Use a dedicated prefix to isolate test data from other store entries.
+	kvStore := prefix.NewStore(ctx.KVStore(app.GetKey(types.StoreKey)), []byte("scanlimit/"))
+
+	// With offset=1, scan cap fires when count > offset+MaxScanLimit = 10,001.
+	// Insert 10,002 items to guarantee the cap is exceeded.
+	numItems := int(query.MaxScanLimit) + 2
+	for i := 0; i < numItems; i++ {
+		kvStore.Set([]byte(fmt.Sprintf("%08d", i)), []byte("v"))
+	}
+
+	_, err := query.Paginate(kvStore, &query.PageRequest{Limit: 1, CountTotal: true}, func(_, _ []byte) error { return nil })
+	s.Require().Error(err)
+	s.Require().Contains(err.Error(), fmt.Sprintf("scanned more than %d entries", query.MaxScanLimit))
+}
+
 func setupTest(t *testing.T) (*app.App, sdk.Context, codec.Codec) {
 	a := app.Setup(t, false, false, false)
 	ctx := a.BaseApp.NewContext(false, tmproto.Header{Height: 1})
```

### sei-cosmos/x/auth/tx/service.go
```diff
@@ -192,8 +192,11 @@ func (s txServer) GetBlockWithTxs(ctx context.Context, req *txtypes.GetBlockWith
 	if req.Pagination != nil {
 		offset = req.Pagination.Offset
 		limit = req.Pagination.Limit
-	} else {
-		offset = 0
+		if err = pagination.VerifyPaginationLimit(limit); err != nil {
+			return nil, sdkerrors.ErrInvalidRequest.Wrapf("invalid pagination limit: %d. Max allowed limit is %d", limit, pagination.MaxLimit)
+		}
+	}
+	if limit == 0 {
 		limit = pagination.DefaultLimit
 	}
 
```

### sei-cosmos/x/bank/keeper/genesis.go
```diff
@@ -4,7 +4,6 @@ import (
 	"fmt"
 
 	sdk "github.com/sei-protocol/sei-chain/sei-cosmos/types"
-	"github.com/sei-protocol/sei-chain/sei-cosmos/types/query"
 	"github.com/sei-protocol/sei-chain/sei-cosmos/x/bank/types"
 )
 
@@ -60,9 +59,9 @@ func (k BaseKeeper) InitGenesis(ctx sdk.Context, genState *types.GenesisState) {
 
 // ExportGenesis returns the bank module's genesis state.
 func (k BaseKeeper) ExportGenesis(ctx sdk.Context) *types.GenesisState {
-	totalSupply, _, err := k.GetPaginatedTotalSupply(ctx, &query.PageRequest{Limit: query.MaxLimit})
+	totalSupply, err := CollectAllTotalSupply(ctx, k)
 	if err != nil {
-		panic(fmt.Errorf("unable to fetch total supply %v", err))
+		panic(fmt.Errorf("unable to fetch total supply: %w", err))
 	}
 	weiBalances := []types.WeiBalance{}
 	k.IterateAllWeiBalances(ctx, func(aa sdk.AccAddress, i sdk.Int) bool {
```

### sei-cosmos/x/bank/keeper/invariants.go
```diff
@@ -4,7 +4,6 @@ import (
 	"fmt"
 
 	sdk "github.com/sei-protocol/sei-chain/sei-cosmos/types"
-	"github.com/sei-protocol/sei-chain/sei-cosmos/types/query"
 	"github.com/sei-protocol/sei-chain/sei-cosmos/x/bank/types"
 )
 
@@ -13,8 +12,7 @@ func TotalSupply(k Keeper) sdk.Invariant {
 	return func(ctx sdk.Context) (string, bool) {
 		expectedTotal := sdk.Coins{}
 		weiTotal := sdk.NewInt(0)
-		supply, _, err := k.GetPaginatedTotalSupply(ctx, &query.PageRequest{Limit: query.MaxLimit})
-
+		supply, err := CollectAllTotalSupply(ctx, k)
 		if err != nil {
 			return sdk.FormatInvariant(types.ModuleName, "query supply",
 				fmt.Sprintf("error querying total supply %v", err)), false
```

### sei-cosmos/x/bank/keeper/keeper.go
```diff
@@ -106,6 +106,28 @@ func (k BaseKeeper) GetPaginatedTotalSupply(ctx sdk.Context, pagination *query.P
 	return supply, pageRes, nil
 }
 
+// CollectAllTotalSupply returns the full supply by paging with MaxLimit.
+func CollectAllTotalSupply(ctx sdk.Context, k Keeper) (sdk.Coins, error) {
+	totalSupply := sdk.NewCoins()
+	pageReq := &query.PageRequest{Limit: query.MaxLimit}
+
+	for {
+		page, pageRes, err := k.GetPaginatedTotalSupply(ctx, pageReq)
+		if err != nil {
+			return nil, err
+		}
+		totalSupply = totalSupply.Add(page...)
+
+		if pageRes == nil || len(pageRes.NextKey) == 0 {
+			return totalSupply, nil
+		}
+		pageReq = &query.PageRequest{
+			Key:   pageRes.NextKey,
+			Limit: query.MaxLimit,
+		}
+	}
+}
+
 // NewBaseKeeper returns a new BaseKeeper object with a given codec, dedicated
 // store key, an AccountKeeper implementation, and a parameter Subspace used to
 // store and fetch module parameters. The BaseKeeper also accepts a
```

### sei-cosmos/x/bank/keeper/keeper_test.go
```diff
@@ -157,6 +157,12 @@ func (suite *IntegrationTestSuite) TestSendCoinsAndWei() {
 	require.Equal(sdk.NewInt(53), keeper.GetBalance(ctx, addr3, sdk.DefaultBondDenom).Amount)
 }
 
+func (suite *IntegrationTestSuite) TestGetPaginatedTotalSupplyMaxLimitExceeded() {
+	_, _, err := suite.app.BankKeeper.GetPaginatedTotalSupply(suite.ctx, &query.PageRequest{Limit: query.MaxLimit + 1})
+	suite.Require().Error(err)
+	suite.Require().Contains(err.Error(), "exceeds maximum allowed limit")
+}
+
 func (suite *IntegrationTestSuite) TestSupply() {
 	ctx := suite.ctx
 
@@ -187,6 +193,33 @@ func (suite *IntegrationTestSuite) TestSupply() {
 	require.Equal(total.String(), "")
 }
 
+func (suite *IntegrationTestSuite) TestCollectAllTotalSupplyMultiPage() {
+	ctx := suite.ctx
+	require := suite.Require()
+
+	_, bk := suite.initKeepersWithmAccPerms(make(map[string]bool))
+
+	// 2.5x MaxLimit denoms so CollectAllTotalSupply must merge three pages (two
+	// full, one partial). Distinct amounts per denom so a dropped or duplicated
+	// page boundary changes the result, not just the count.
+	numDenoms := int(query.MaxLimit*2 + query.MaxLimit/2)
+	coins := make(sdk.Coins, numDenoms)
+	for i := 0; i < numDenoms; i++ {
+		coins[i] = sdk.NewInt64Coin(fmt.Sprintf("denom%05d", i), int64(i+1))
+	}
+	totalSupply := coins.Sort()
+	require.NoError(bk.MintCoins(ctx, authtypes.Minter, totalSupply))
+
+	supply, err := keeper.CollectAllTotalSupply(ctx, bk)
+	require.NoError(err)
+	require.Equal(len(totalSupply), len(supply))
+	require.True(totalSupply.IsEqual(supply))
+
+	// the in-consensus TotalSupply invariant consumes the same merged supply
+	msg, broken := keeper.TotalSupply(bk)(ctx)
+	require.False(broken, msg)
+}
+
 func (suite *IntegrationTestSuite) TestIterateSupply() {
 	ctx := suite.ctx
 
```

### sei-cosmos/x/slashing/client/rest/grpc_query_test.go
```diff
@@ -57,7 +57,7 @@ func (s *IntegrationTestSuite) TestGRPCQueries() {
 	}{
 		{
 			"get signing infos (height specific)",
-			fmt.Sprintf("%s/cosmos/slashing/v1beta1/signing_infos", baseURL),
+			fmt.Sprintf("%s/cosmos/slashing/v1beta1/signing_infos?pagination.count_total=true", baseURL),
 			map[string]string{
 				grpctypes.GRPCBlockHeightHeader: "1",
 			},
```

### sei-cosmos/x/staking/keeper/grpc_query_test.go
```diff
@@ -28,7 +28,7 @@ func (suite *KeeperTestSuite) TestGRPCQueryValidators() {
 		{
 			"empty request",
 			func() {
-				req = &types.QueryValidatorsRequest{}
+				req = &types.QueryValidatorsRequest{Pagination: &query.PageRequest{CountTotal: true}}
 			},
 			true,
 
@@ -38,7 +38,7 @@ func (suite *KeeperTestSuite) TestGRPCQueryValidators() {
 		{
 			"empty status returns all the validators",
 			func() {
-				req = &types.QueryValidatorsRequest{Status: ""}
+				req = &types.QueryValidatorsRequest{Status: "", Pagination: &query.PageRequest{CountTotal: true}}
 			},
 			true,
 			len(vals),
```
