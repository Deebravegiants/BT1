# [?] overflow protection

## Summary
Severity: Unknown
Chain: Flow
Component: onflow/flow-go
Published: 2026-04-14
Source: https://github.com/onflow/flow-go/commit/7cd22497fc6c18bf353a8cdd245b3f9faac9ae2a
Type: security-commit

## Details
overflow protection

## Patch
### engine/access/rpc/backend/events/events.go
```diff
@@ -94,10 +94,15 @@ func (e *Events) GetEventsForHeightRange(
 		return nil, status.Error(codes.InvalidArgument, "start height must not be larger than end height")
 	}
 
-	rangeSize := endHeight - startHeight + 1 // range is inclusive on both ends
-	if rangeSize > uint64(e.maxHeightRange) {
+	// Overflow-safe range validation: compute (endHeight - startHeight) first, then check if
+	// adding 1 (for inclusive range) would exceed maxHeightRange. This avoids the overflow that
+	// occurs when endHeight = math.MaxUint64 and startHeight = 0, where (endHeight - startHeight + 1)
+	// wraps to 0.
+	rangeSpan := endHeight - startHeight // safe: we already checked endHeight >= startHeight
+	if rangeSpan >= uint64(e.maxHeightRange) {
+		// rangeSpan + 1 > maxHeightRange, but we compute it this way to avoid overflow
 		return nil, status.Errorf(codes.InvalidArgument,
-			"requested block range (%d) exceeded maximum (%d)", rangeSize, e.maxHeightRange)
+			"requested block range (%d) exceeded maximum (%d)", rangeSpan+1, e.maxHeightRange)
 	}
 
 	// get the latest sealed block header
```

### engine/access/rpc/backend/events/events_test.go
```diff
@@ -4,6 +4,7 @@ import (
 	"bytes"
 	"context"
 	"fmt"
+	"math"
 	"sort"
 	"testing"
 
@@ -319,6 +320,38 @@ func (s *EventsSuite) TestGetEventsForHeightRange_HandlesErrors() {
 		s.Assert().Nil(response)
 	})
 
+	// Regression tests for unsigned integer overflow vulnerability (KRITT-1)
+	// When endHeight = math.MaxUint64 and startHeight = 0, the computation
+	// (endHeight - startHeight + 1) would overflow to 0, bypassing the range check.
+	s.Run("returns error for max uint64 end height - overflow prevention", func() {
+		backend := s.defaultBackend(query_mode.IndexQueryModeExecutionNodesOnly, s.eventsIndex)
+
+		response, err := backend.GetEventsForHeightRange(ctx, targetEvent, 0, math.MaxUint64, encoding)
+		s.Assert().Equal(codes.InvalidArgument, status.Code(err))
+		s.Assert().Contains(err.Error(), "exceeded maximum")
+		s.Assert().Nil(response)
+	})
+
+	s.Run("returns error for max uint64 end height with non-zero start - overflow prevention", func() {
+		backend := s.defaultBackend(query_mode.IndexQueryModeExecutionNodesOnly, s.eventsIndex)
+
+		response, err := backend.GetEventsForHeightRange(ctx, targetEvent, 100, math.MaxUint64, encoding)
+		s.Assert().Equal(codes.InvalidArgument, status.Code(err))
+		s.Assert().Contains(err.Error(), "exceeded maximum")
+		s.Assert().Nil(response)
+	})
+
+	s.Run("returns error for range exactly at max boundary", func() {
+		backend := s.defaultBackend(query_mode.IndexQueryModeExecutionNodesOnly, s.eventsIndex)
+		// Range of exactly maxHeightRange should be allowed (inclusive range = maxHeightRange blocks)
+		// But range of maxHeightRange + 1 blocks (endHeight = startHeight + maxHeightRange) should fail
+
+		// endHeight = startHeight + maxHeightRange gives maxHeightRange + 1 blocks, should fail
+		response, err := backend.GetEventsForHeightRange(ctx, targetEvent, startHeight, startHeight+DefaultMaxHeightRange, encoding)
+		s.Assert().Equal(codes.InvalidArgument, status.Code(err))
+		s.Assert().Nil(response)
+	})
+
 	s.Run("throws irrecoverable if sealed header not available", func() {
 		s.state.On("Sealed").Return(s.snapshot)
 		s.snapshot.On("Head").Return(nil, storage.ErrNotFound).Once()
```
