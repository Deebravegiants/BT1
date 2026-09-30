# [?] Merge pull request #4431 from jeongkyun-oh/fix/panic-recovery

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2026-02-26
Source: https://github.com/OffchainLabs/nitro/commit/6ac8c3312043a35da713c12926d549bafad7556e
Type: security-commit

## Details
Merge pull request #4431 from jeongkyun-oh/fix/panic-recovery

Use defer to unlock createBlocksMutex in sequencerWrapper

## Patch
### changelog/jeongkyun-oh-nit-4431.md
```diff
@@ -0,0 +1,2 @@
+### Fixed
+ - Use defer to release createBlocksMutex in sequencerWrapper to prevent deadlock on panic
```

### execution/gethexec/executionengine.go
```diff
@@ -550,9 +550,11 @@ func (s *ExecutionEngine) resequenceReorgedMessages(messages []*arbostypes.Messa
 func (s *ExecutionEngine) sequencerWrapper(sequencerFunc func() (*types.Block, error)) (*types.Block, error) {
 	attempts := 0
 	for {
-		s.createBlocksMutex.Lock()
-		block, err := sequencerFunc()
-		s.createBlocksMutex.Unlock()
+		block, err := func() (*types.Block, error) {
+			s.createBlocksMutex.Lock()
+			defer s.createBlocksMutex.Unlock()
+			return sequencerFunc()
+		}()
 		if !errors.Is(err, execution.ErrSequencerInsertLockTaken) {
 			return block, err
 		}
```

### execution/gethexec/executionengine_test.go
```diff
@@ -0,0 +1,60 @@
+// Copyright 2026, Offchain Labs, Inc.
+// For license information, see https://github.com/OffchainLabs/nitro/blob/master/LICENSE.md
+
+package gethexec
+
+import (
+	"errors"
+	"testing"
+
+	"github.com/ethereum/go-ethereum/core/types"
+)
+
+// TestSequencerWrapperMutexReleasedOnPanic verifies that createBlocksMutex is
+// properly released even when sequencerFunc panics. Without defer, a panic
+// would bypass Unlock() and leave the mutex locked, causing a deadlock on the
+// next call (e.g. after createBlock's recover() catches the panic).
+func TestSequencerWrapperMutexReleasedOnPanic(t *testing.T) {
+	engine := &ExecutionEngine{
+		cachedL1PriceData: NewL1PriceData(),
+	}
+
+	// Mirrors what createBlock does: call into sequencerWrapper and recover.
+	func() {
+		defer func() {
+			if r := recover(); r == nil {
+				t.Error("expected a panic but got none")
+			}
+		}()
+		_, _ = engine.sequencerWrapper(func() (*types.Block, error) {
+			panic("simulated sequencer panic")
+		})
+	}()
+
+	// The mutex must be unlocked after the panic is recovered upstream.
+	if !engine.createBlocksMutex.TryLock() {
+		t.Fatal("createBlocksMutex is still locked after panic recovery; would deadlock on next call")
+	}
+	engine.createBlocksMutex.Unlock()
+}
+
+// TestSequencerWrapperMutexReleasedOnSuccess verifies that normal (non-panic)
+// returns also leave the mutex unlocked.
+func TestSequencerWrapperMutexReleasedOnSuccess(t *testing.T) {
+	engine := &ExecutionEngine{
+		cachedL1PriceData: NewL1PriceData(),
+	}
+
+	sentinel := errors.New("stop retrying")
+	_, err := engine.sequencerWrapper(func() (*types.Block, error) {
+		return nil, sentinel
+	})
+	if !errors.Is(err, sentinel) {
+		t.Fatalf("unexpected error: %v", err)
+	}
+
+	if !engine.createBlocksMutex.TryLock() {
+		t.Fatal("createBlocksMutex is still locked after normal return")
+	}
+	engine.createBlocksMutex.Unlock()
+}
```
