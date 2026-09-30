# [?] Harden blocks reexecutor with panic recovery for trie-cache eviction races

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2026-03-22
Source: https://github.com/OffchainLabs/nitro/commit/757ba93e5641897b4b3fa3a02782678a1ae88914
Type: security-commit

## Details
Harden blocks reexecutor with panic recovery for trie-cache eviction races

- Wrap AdvanceStateByBlock in recover() to convert panics from
  concurrent trie-cache eviction races into errors, preventing
  abnormal process termination
- Add unit tests for reportFatalErr (basic, channel-full, multiple
  error types) and panic recovery in advanceStateUpToBlock

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

## Patch
### blocks_reexecutor/blocks_reexecutor.go
```diff
@@ -8,6 +8,7 @@ import (
 	"errors"
 	"fmt"
 	"math/rand"
+	"runtime/debug"
 	"sort"
 	"strings"
 	"sync"
@@ -397,7 +398,20 @@ func (s *BlocksReExecutor) advanceStateUpToBlock(ctx context.Context, state *sta
 	}
 	for ctx.Err() == nil {
 		var receipts types.Receipts
-		state, block, receipts, err = arbitrum.AdvanceStateByBlock(ctx, s.blockchain, state, blockToRecreate, prevHash, nil, vmConfig)
+		// Recover from panics in AdvanceStateByBlock caused by trie-cache
+		// eviction races: one goroutine dereferences a root (dropping its
+		// refcount to zero and allowing eviction) while another goroutine
+		// is still traversing shared nodes under a different root.
+		func() {
+			defer func() {
+				if r := recover(); r != nil {
+					log.Error("panic during block re-execution", "block", blockToRecreate, "recover", r, "stack", string(debug.Stack()))
+					state = nil
+					err = fmt.Errorf("panic during block re-execution at block %d: %v", blockToRecreate, r)
+				}
+			}()
+			state, block, receipts, err = arbitrum.AdvanceStateByBlock(ctx, s.blockchain, state, blockToRecreate, prevHash, nil, vmConfig)
+		}()
 		if err != nil {
 			return err
 		}
```

### blocks_reexecutor/blocks_reexecutor_test.go
```diff
@@ -4,92 +4,137 @@ import (
 	"context"
 	"errors"
 	"fmt"
+	"math/big"
+	"strings"
+	"sync/atomic"
 	"testing"
-)
 
-// newTestReExecutor creates a minimal BlocksReExecutor for unit testing
-// handleContextOrFatal. Only fatalErrChan is needed; other fields are zero.
-func newTestReExecutor(fatalCh chan error) *BlocksReExecutor {
-	s := new(BlocksReExecutor)
-	s.fatalErrChan = fatalCh
-	return s
-}
+	"github.com/ethereum/go-ethereum/core/types"
+)
 
-func TestHandleContextOrFatalSuppressesContextErrors(t *testing.T) {
+func TestReportFatalErrSetsFatalReported(t *testing.T) {
 	fatalCh := make(chan error, 1)
-	s := newTestReExecutor(fatalCh)
+	s := &BlocksReExecutor{
+		fatalErrChan:  fatalCh,
+		fatalReported: atomic.Bool{},
+	}
+
+	realErr := errors.New("disk corruption")
+	s.reportFatalErr(realErr)
 
-	// context.Canceled should be suppressed
-	s.handleContextOrFatal(context.Background(), context.Canceled, "test")
+	if !s.fatalReported.Load() {
+		t.Fatal("expected fatalReported to be set")
+	}
 	select {
 	case err := <-fatalCh:
-		t.Fatalf("context.Canceled should not be fatal, got: %v", err)
+		if !errors.Is(err, realErr) {
+			t.Fatalf("expected realErr, got: %v", err)
+		}
 	default:
+		t.Fatal("expected error in fatalErrChan")
 	}
+}
 
-	// Wrapped context.Canceled should also be suppressed
-	s.handleContextOrFatal(context.Background(), fmt.Errorf("op failed: %w", context.Canceled), "test")
-	select {
-	case err := <-fatalCh:
-		t.Fatalf("wrapped context.Canceled should not be fatal, got: %v", err)
-	default:
+func TestReportFatalErrDoesNotBlockOnFullChannel(t *testing.T) {
+	fatalCh := make(chan error, 1)
+	s := &BlocksReExecutor{
+		fatalErrChan:  fatalCh,
+		fatalReported: atomic.Bool{},
 	}
 
-	// context.DeadlineExceeded should be suppressed
-	s.handleContextOrFatal(context.Background(), context.DeadlineExceeded, "test")
+	// Fill the channel
+	s.reportFatalErr(errors.New("first"))
+	// Second call should not block (exercises the default branch)
+	s.reportFatalErr(errors.New("second"))
+
+	if !s.fatalReported.Load() {
+		t.Fatal("expected fatalReported to be set")
+	}
+	// Only the first error should be in the channel
+	err := <-fatalCh
+	if !strings.Contains(err.Error(), "first") {
+		t.Fatalf("expected first error preserved, got: %v", err)
+	}
 	select {
-	case err := <-fatalCh:
-		t.Fatalf("context.DeadlineExceeded should not be fatal, got: %v", err)
+	case extra := <-fatalCh:
+		t.Fatalf("expected channel to be empty after drain, got: %v", extra)
 	default:
 	}
+}
 
-	// A real error should be sent to fatalErrChan
-	realErr := errors.New("disk corruption")
-	s.handleContextOrFatal(context.Background(), realErr, "reexecution failed")
-	select {
-	case err := <-fatalCh:
-		if !errors.Is(err, realErr) {
-			t.Fatalf("expected realErr wrapped, got: %v", err)
+func TestReportFatalErrMultipleErrorTypes(t *testing.T) {
+	fatalCh := make(chan error, 4)
+	s := &BlocksReExecutor{
+		fatalErrChan:  fatalCh,
+		fatalReported: atomic.Bool{},
+	}
+
+	for _, err := range []error{
+		errors.New("disk corruption"),
+		fmt.Errorf("wrapped: %w", errors.New("inner")),
+		errors.New("another error"),
+	} {
+		s.reportFatalErr(err)
+		select {
+		case fatal := <-fatalCh:
+			if fatal == nil {
+				t.Fatalf("expected non-nil error for input: %v", err)
+			}
+		default:
+			t.Fatalf("expected error in channel for input: %v", err)
 		}
-	default:
-		t.Fatal("expected real error to be sent to fatalErrChan")
 	}
 }
 
-func TestHandleContextOrFatalSuppressesDuringShutdown(t *testing.T) {
-	fatalCh := make(chan error, 1)
-	s := newTestReExecutor(fatalCh)
+func TestAdvanceStateUpToBlockCancelledContext(t *testing.T) {
+	// When the context is already cancelled, advanceStateUpToBlock should
+	// return ctx.Err() immediately without entering the loop, and still
+	// call lastRelease via defer.
+	s := &BlocksReExecutor{
+		config:     &Config{},
+		blockchain: nil,
+	}
+	targetHeader := &types.Header{Number: big.NewInt(10)}
+	lastAvailableHeader := &types.Header{Number: big.NewInt(5)}
+	released := false
+	release := func() { released = true }
 
-	// When context is cancelled (shutdown), even non-context errors should be suppressed
 	ctx, cancel := context.WithCancel(context.Background())
 	cancel()
 
-	s.handleContextOrFatal(ctx, errors.New("some error during shutdown"), "test")
-	select {
-	case err := <-fatalCh:
-		t.Fatalf("errors during shutdown should be suppressed, got: %v", err)
-	default:
+	err := s.advanceStateUpToBlock(ctx, nil, targetHeader, lastAvailableHeader, release)
+	if !errors.Is(err, context.Canceled) {
+		t.Fatalf("expected context.Canceled, got: %v", err)
+	}
+	if !released {
+		t.Fatal("expected lastRelease to be called even with cancelled context")
 	}
 }
 
-func TestHandleContextOrFatalDropsWhenChannelFull(t *testing.T) {
-	// Use a buffer of 1, fill it, then verify the second error is dropped (not panicking)
-	fatalCh := make(chan error, 1)
-	s := newTestReExecutor(fatalCh)
-
-	// First error fills the channel
-	s.handleContextOrFatal(context.Background(), errors.New("first error"), "test")
-	// Second error should be dropped (logged, not panic)
-	s.handleContextOrFatal(context.Background(), errors.New("second error"), "test")
+func TestAdvanceStateUpToBlockRecoversPanic(t *testing.T) {
+	// A nil blockchain causes AdvanceStateByBlock to panic (nil pointer
+	// dereference). The panic recovery in advanceStateUpToBlock should
+	// catch it and return an error instead of crashing.
+	s := &BlocksReExecutor{
+		config:     &Config{},
+		blockchain: nil,
+	}
+	targetHeader := &types.Header{Number: big.NewInt(5)}
+	lastAvailableHeader := &types.Header{Number: big.NewInt(4)}
+	released := false
+	release := func() { released = true }
 
-	// Only the first error should be in the channel
-	err := <-fatalCh
-	if err.Error() != "test: first error" {
-		t.Fatalf("expected first error, got: %v", err)
+	err := s.advanceStateUpToBlock(context.Background(), nil, targetHeader, lastAvailableHeader, release)
+	if err == nil {
+		t.Fatal("expected error from panic recovery, got nil")
 	}
-	select {
-	case err := <-fatalCh:
-		t.Fatalf("second error should have been dropped, got: %v", err)
-	default:
+	if !strings.Contains(err.Error(), "panic during block re-execution") {
+		t.Fatalf("expected panic recovery error, got: %v", err)
+	}
+	if !strings.Contains(err.Error(), "at block 5") {
+		t.Fatalf("expected block number in error message, got: %v", err)
+	}
+	if !released {
+		t.Fatal("expected lastRelease to be called")
 	}
 }
```

### changelog/jco-blocks-reexecutor-shutdown.md
```diff
@@ -1,3 +1,2 @@
 ### Fixed
 - Harden blocks reexecutor with panic recovery for concurrent trie access races
-- Suppress spurious shutdown errors from context cancellation in blocks reexecutor
```
