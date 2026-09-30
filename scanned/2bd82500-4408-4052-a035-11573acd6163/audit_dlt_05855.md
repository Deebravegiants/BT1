# [?] fix: blocks reexecutor panic recovery and shutdown error suppression

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2026-03-19
Source: https://github.com/OffchainLabs/nitro/commit/86d7ad1f95aab16be2207921dcc0b22eaf605691
Type: security-commit

## Details
fix: blocks reexecutor panic recovery and shutdown error suppression

- Add handleContextOrFatal to suppress context errors during shutdown
- Wrap AdvanceStateByBlock with recover() to convert panics from
  concurrent trie access races into errors, preventing database
  corruption from abnormal process termination
- Add unit tests for handleContextOrFatal behavior

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
@@ -217,6 +218,26 @@ func logState(header *types.Header, hasState bool) {
 	}
 }
 
+// handleContextOrFatal suppresses errors during shutdown (when ctx is done)
+// and sends non-context errors to fatalErrChan.
+func (s *BlocksReExecutor) handleContextOrFatal(ctx context.Context, err error, fatalMsg string) {
+	if ctx.Err() != nil {
+		log.Trace("blocksReExecutor shutting down", "ctxErr", ctx.Err(), "err", err)
+		return
+	}
+	if errors.Is(err, context.Canceled) {
+		log.Trace("blocksReExecutor context cancelled", "err", err)
+	} else if errors.Is(err, context.DeadlineExceeded) {
+		log.Warn("blocksReExecutor timed out", "err", err)
+	} else {
+		select {
+		case s.fatalErrChan <- fmt.Errorf("%s: %w", fatalMsg, err):
+		default:
+			log.Error("fatalErrChan full, dropping error", "msg", fatalMsg, "err", err)
+		}
+	}
+}
+
 // LaunchBlocksReExecution launches the thread to apply blocks of range [currentBlock-s.config.MinBlocksPerThread, currentBlock] to the last available valid state
 func (s *BlocksReExecutor) LaunchBlocksReExecution(ctx context.Context, startBlock, currentBlock, minBlocksPerThread uint64) uint64 {
 	start := arbmath.SaturatingUSub(currentBlock, minBlocksPerThread)
@@ -225,19 +246,19 @@ func (s *BlocksReExecutor) LaunchBlocksReExecution(ctx context.Context, startBlo
 	}
 	startHeader := s.blockchain.GetHeaderByNumber(start)
 	if startHeader == nil {
-		s.fatalErrChan <- fmt.Errorf("blocksReExecutor failed to get start header at %d", start)
+		s.handleContextOrFatal(ctx, fmt.Errorf("blocksReExecutor failed to get start header at %d", start), "missing start header")
 		return startBlock
 	}
 	startState, startHeader, release, err := arbitrum.FindLastAvailableState(ctx, s.blockchain, s.stateFor, startHeader, logState, -1)
 	if err != nil {
-		s.fatalErrChan <- fmt.Errorf("blocksReExecutor failed to get last available state while searching for state at %d, err: %w", start, err)
+		s.handleContextOrFatal(ctx, err, fmt.Sprintf("blocksReExecutor failed to get last available state while searching for state at %d", start))
 		return startBlock
 	}
 	start = startHeader.Number.Uint64()
 	s.LaunchThread(func(ctx context.Context) {
 		log.Info("Starting reexecution of blocks against historic state", "stateAt", start, "startBlock", start+1, "endBlock", currentBlock)
 		if err := s.advanceStateUpToBlock(ctx, startState, s.blockchain.GetHeaderByNumber(currentBlock), startHeader, release); err != nil {
-			s.fatalErrChan <- fmt.Errorf("blocksReExecutor errored advancing state from block %d to block %d, err: %w", start, currentBlock, err)
+			s.handleContextOrFatal(ctx, err, fmt.Sprintf("blocksReExecutor errored advancing state from block %d to block %d", start, currentBlock))
 		} else {
 			log.Info("Successfully reexecuted blocks against historic state", "stateAt", start, "startBlock", start+1, "endBlock", currentBlock)
 		}
@@ -354,7 +375,23 @@ func (s *BlocksReExecutor) advanceStateUpToBlock(ctx context.Context, state *sta
 	}
 	for ctx.Err() == nil {
 		var receipts types.Receipts
-		state, block, receipts, err = arbitrum.AdvanceStateByBlock(ctx, s.blockchain, state, blockToRecreate, prevHash, nil, vmConfig)
+		// Wrap AdvanceStateByBlock in a closure with recover to convert panics
+		// into errors, preventing abnormal process termination that could
+		// corrupt the database. The panic occurs when a concurrent goroutine
+		// dereferences a trie root (allowing its nodes to be evicted from the
+		// cache) while this goroutine is still traversing those nodes, which
+		// can manifest as: "ArbOS uninitialized", trie node decode failures,
+		// invalid node types, etc.
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
@@ -0,0 +1,95 @@
+package blocksreexecutor
+
+import (
+	"context"
+	"errors"
+	"fmt"
+	"testing"
+)
+
+// newTestReExecutor creates a minimal BlocksReExecutor for unit testing
+// handleContextOrFatal. Only fatalErrChan is needed; other fields are zero.
+func newTestReExecutor(fatalCh chan error) *BlocksReExecutor {
+	s := new(BlocksReExecutor)
+	s.fatalErrChan = fatalCh
+	return s
+}
+
+func TestHandleContextOrFatalSuppressesContextErrors(t *testing.T) {
+	fatalCh := make(chan error, 1)
+	s := newTestReExecutor(fatalCh)
+
+	// context.Canceled should be suppressed
+	s.handleContextOrFatal(context.Background(), context.Canceled, "test")
+	select {
+	case err := <-fatalCh:
+		t.Fatalf("context.Canceled should not be fatal, got: %v", err)
+	default:
+	}
+
+	// Wrapped context.Canceled should also be suppressed
+	s.handleContextOrFatal(context.Background(), fmt.Errorf("op failed: %w", context.Canceled), "test")
+	select {
+	case err := <-fatalCh:
+		t.Fatalf("wrapped context.Canceled should not be fatal, got: %v", err)
+	default:
+	}
+
+	// context.DeadlineExceeded should be suppressed
+	s.handleContextOrFatal(context.Background(), context.DeadlineExceeded, "test")
+	select {
+	case err := <-fatalCh:
+		t.Fatalf("context.DeadlineExceeded should not be fatal, got: %v", err)
+	default:
+	}
+
+	// A real error should be sent to fatalErrChan
+	realErr := errors.New("disk corruption")
+	s.handleContextOrFatal(context.Background(), realErr, "reexecution failed")
+	select {
+	case err := <-fatalCh:
+		if !errors.Is(err, realErr) {
+			t.Fatalf("expected realErr wrapped, got: %v", err)
+		}
+	default:
+		t.Fatal("expected real error to be sent to fatalErrChan")
+	}
+}
+
+func TestHandleContextOrFatalSuppressesDuringShutdown(t *testing.T) {
+	fatalCh := make(chan error, 1)
+	s := newTestReExecutor(fatalCh)
+
+	// When context is cancelled (shutdown), even non-context errors should be suppressed
+	ctx, cancel := context.WithCancel(context.Background())
+	cancel()
+
+	s.handleContextOrFatal(ctx, errors.New("some error during shutdown"), "test")
+	select {
+	case err := <-fatalCh:
+		t.Fatalf("errors during shutdown should be suppressed, got: %v", err)
+	default:
+	}
+}
+
+func TestHandleContextOrFatalDropsWhenChannelFull(t *testing.T) {
+	// Use a buffer of 1, fill it, then verify the second error is dropped (not panicking)
+	fatalCh := make(chan error, 1)
+	s := newTestReExecutor(fatalCh)
+
+	// First error fills the channel
+	s.handleContextOrFatal(context.Background(), errors.New("first error"), "test")
+	// Second error should be dropped (logged, not panic)
+	s.handleContextOrFatal(context.Background(), errors.New("second error"), "test")
+
+	// Only the first error should be in the channel
+	err := <-fatalCh
+	if err.Error() != "test: first error" {
+		t.Fatalf("expected first error, got: %v", err)
+	}
+	select {
+	case err := <-fatalCh:
+		t.Fatalf("second error should have been dropped, got: %v", err)
+	default:
+	}
+}
```

### changelog/jco-blocks-reexecutor-shutdown.md
```diff
@@ -0,0 +1,3 @@
+### Fixed
+- Harden blocks reexecutor with panic recovery for concurrent trie access races
+- Suppress spurious shutdown errors from context cancellation in blocks reexecutor
```
