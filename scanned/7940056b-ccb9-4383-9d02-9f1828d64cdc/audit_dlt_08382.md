# [?] Merge pull request #26430 from c-tonneslan/fix-pagination-overflow

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2026-05-26
Source: https://github.com/cosmos/cosmos-sdk/commit/a3723398e751ebc8c9c6473f6b49fce62f961e05
Type: security-commit

## Details
Merge pull request #26430 from c-tonneslan/fix-pagination-overflow

fix(types/query): saturate Paginate end when offset+limit overflows

## Patch
### types/query/filtered_pagination.go
```diff
@@ -2,6 +2,7 @@ package query
 
 import (
 	"fmt"
+	"math"
 
 	proto "github.com/cosmos/gogoproto/proto"
 
@@ -57,14 +58,22 @@ func FilteredPaginate(
 	}
 
 	end := pageRequest.Offset + pageRequest.Limit
+	if end < pageRequest.Offset {
+		// Saturate to MaxUint64 when offset+limit overflows. Without this,
+		// a caller passing an absurdly large limit would wrap end back to a
+		// small number and the loop would return zero results.
+		end = math.MaxUint64
+	}
 	accumulateFn := func(numHits uint64) bool { return numHits >= pageRequest.Offset && numHits < end }
 
 	for ; iterator.Valid(); iterator.Next() {
 		numHits, err = processResult(iterator, numHits, onResult, accumulateFn)
 		if err != nil {
 			return nil, err
 		}
-		if numHits == end+1 {
+		// numHits > end (rather than ==end+1) so the check stays correct
+		// when end has been saturated to MaxUint64 and end+1 would wrap.
+		if numHits > end {
 			if nextKey == nil {
 				nextKey = iterator.Key()
 			}
@@ -182,6 +191,12 @@ func GenericFilteredPaginate[T, F proto.Message](
 	}
 
 	end := pageRequest.Offset + pageRequest.Limit
+	if end < pageRequest.Offset {
+		// Saturate to MaxUint64 when offset+limit overflows. Without this,
+		// a caller passing an absurdly large limit would wrap end back to a
+		// small number and the loop would return zero results.
+		end = math.MaxUint64
+	}
 	accumulateFn := func(numHits uint64) bool { return numHits >= pageRequest.Offset && numHits < end }
 
 	for ; iterator.Valid(); iterator.Next() {
@@ -190,7 +205,9 @@ func GenericFilteredPaginate[T, F proto.Message](
 			return nil, nil, err
 		}
 
-		if numHits == end+1 {
+		// numHits > end (rather than ==end+1) so the check stays correct
+		// when end has been saturated to MaxUint64 and end+1 would wrap.
+		if numHits > end {
 			if nextKey == nil {
 				nextKey = iterator.Key()
 			}
```

### types/query/filtered_pagination_test.go
```diff
@@ -88,6 +88,16 @@ func (s *paginationTestSuite) TestFilteredPaginations() {
 	s.Require().NoError(err)
 	s.Require().NotNil(res)
 	s.Require().LessOrEqual(len(balances), 2)
+
+	s.T().Log("verify offset+limit overflow returns the page instead of nothing")
+	// A limit large enough that offset+limit wraps a uint64 used to make
+	// FilteredPaginate skip everything because end wrapped to a small
+	// number. It should walk the remaining rows after the offset.
+	pageReq = &query.PageRequest{Offset: 1, Limit: 0xFFFFFFFFFFFFFFFF}
+	balances, res, err = execFilterPaginate(store, pageReq, s.cdc)
+	s.Require().NoError(err)
+	s.Require().NotNil(res)
+	s.Require().Equal(3, len(balances))
 }
 
 func (s *paginationTestSuite) TestReverseFilteredPaginations() {
```

### types/query/pagination.go
```diff
@@ -2,6 +2,7 @@ package query
 
 import (
 	"fmt"
+	"math"
 
 	db "github.com/cosmos/cosmos-db"
 	"google.golang.org/grpc/codes"
@@ -85,6 +86,12 @@ func Paginate(
 	}
 
 	end := pageRequest.Offset + pageRequest.Limit
+	if end < pageRequest.Offset {
+		// Saturate to MaxUint64 when offset+limit overflows. Without this,
+		// a caller passing an absurdly large limit would wrap end back to a
+		// small number and the loop would return zero results.
+		end = math.MaxUint64
+	}
 
 	for ; iterator.Valid(); iterator.Next() {
 		count++
```

### types/query/pagination_test.go
```diff
@@ -209,6 +209,16 @@ func (s *paginationTestSuite) TestPagination() {
 	s.Require().NoError(err)
 	s.Require().LessOrEqual(res.Balances.Len(), 0)
 	s.Require().Nil(res.Pagination.NextKey)
+
+	s.T().Log("verify offset+limit overflow returns the page instead of nothing")
+	// A limit large enough that offset+limit wraps a uint64 used to make
+	// Paginate skip everything. It should walk the remaining rows after
+	// the offset like a normal large limit would.
+	pageReq = &query.PageRequest{Offset: 12, Limit: 0xFFFFFFFFFFFFFFFF, CountTotal: false}
+	request = types.NewQueryAllBalancesRequest(addr1, pageReq, false)
+	res, err = queryClient.AllBalances(gocontext.Background(), request)
+	s.Require().NoError(err)
+	s.Require().Equal(res.Balances.Len(), numBalances-12)
 }
 
 func (s *paginationTestSuite) TestReversePagination() {
```
