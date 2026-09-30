# [?] Merge pull request #8474 from onflow/peterargue/fix-follower-happy-path-pebble-panic

## Summary
Severity: Unknown
Chain: Flow
Component: onflow/flow-go
Published: 2026-04-10
Source: https://github.com/onflow/flow-go/commit/a41baf9c165df447ab8f578472744163a8b23a24
Type: security-commit

## Details
Merge pull request #8474 from onflow/peterargue/fix-follower-happy-path-pebble-panic

[CI] refactor TestFollowerHappyPath to use synctest

## Patch
### engine/common/follower/integration_test.go
```diff
@@ -4,7 +4,7 @@ import (
 	"context"
 	"sync"
 	"testing"
-	"time"
+	"testing/synctest"
 
 	"github.com/cockroachdb/pebble/v2"
 	"github.com/stretchr/testify/mock"
@@ -14,6 +14,7 @@ import (
 	"github.com/onflow/flow-go/consensus"
 	"github.com/onflow/flow-go/consensus/hotstuff"
 	"github.com/onflow/flow-go/consensus/hotstuff/mocks"
+	"github.com/onflow/flow-go/consensus/hotstuff/model"
 	"github.com/onflow/flow-go/consensus/hotstuff/notifications/pubsub"
 	"github.com/onflow/flow-go/model/flow"
 	"github.com/onflow/flow-go/module/compliance"
@@ -43,6 +44,13 @@ import (
 // Each worker submits batchesPerWorker*blocksPerBatch blocks
 // In total we will submit workers*batchesPerWorker*blocksPerBatch
 func TestFollowerHappyPath(t *testing.T) {
+	// All construction happens inside the synctest bubble so that channels
+	// created by the engine components are associated with the bubble.
+	// This allows synctest.Wait() to detect when all goroutines have settled.
+	synctest.Test(t, runTestFollowerHappyPath)
+}
+
+func runTestFollowerHappyPath(t *testing.T) {
 	allIdentities := unittest.CompleteIdentitySet()
 	rootSnapshot := unittest.RootSnapshotFixture(allIdentities)
 	lockManager := storage.NewTestingLockManager()
@@ -148,7 +156,26 @@ func TestFollowerHappyPath(t *testing.T) {
 		// start hotstuff logic and follower engine
 		followerLoop.Start(mockCtx)
 		engine.Start(mockCtx)
-		unittest.RequireCloseBefore(t, moduleutil.AllReady(engine, followerLoop), time.Second, "engine failed to start")
+		allReady := moduleutil.AllReady(engine, followerLoop)
+		defer func() {
+			cancel()
+
+			allDone := moduleutil.AllDone(engine, followerLoop)
+			synctest.Wait()
+			select {
+			case <-allDone:
+			default:
+				t.Fatal("engine failed to stop")
+			}
+		}()
+
+		// Wait until all startup goroutines have settled, then verify readiness.
+		synctest.Wait()
+		select {
+		case <-allReady:
+		default:
+			t.Fatal("engine failed to start")
+		}
 
 		// prepare chain of blocks, we will use a continuous chain assuming it was generated on happy path.
 		workers := 5
@@ -188,6 +215,22 @@ func TestFollowerHappyPath(t *testing.T) {
 		// where ◄(B) denotes a QC for block B
 		targetBlockHeight := pendingBlocks[len(pendingBlocks)-3].Block.Height
 
+		// Register a finalization callback so the test can block on a channel instead of polling
+		// with require.Eventually. require.Eventually uses time.Sleep internally; in a synctest
+		// bubble fake time only advances when all goroutines are durably blocked, which never
+		// happens while the worker goroutines are running their continuous submission loop.
+		// A channel receive IS durably blocking, so the main goroutine can wait here while workers
+		// keep running and the engine keeps processing blocks.
+		finalized := make(chan struct{}, 1)
+		consensusConsumer.AddOnBlockFinalizedConsumer(func(b *model.Block) {
+			if b.View >= targetBlockHeight {
+				select {
+				case finalized <- struct{}{}:
+				default:
+				}
+			}
+		})
+
 		// emulate syncing logic, where we push same blocks over and over.
 		originID := unittest.IdentifierFixture()
 		submittingBlocks := atomic.NewBool(true)
@@ -207,33 +250,15 @@ func TestFollowerHappyPath(t *testing.T) {
 			}(pendingBlocks[i*blocksPerWorker : (i+1)*blocksPerWorker])
 		}
 
-		// Ensure graceful shutdown even if the test fails early (e.g., Eventually times out).
-		// Otherwise, the test may panic with "pebble: closed" when threads are attempting to still write to the database, while
-		// the test is unwinding and closing the database. If such panics happen, we don't know what assertation failed and
-		// just see the panic. Hence, we call `cancel()` and attempt to wait for the engine to stop in all cases.
-		defer func() {
-			// stop producers and wait for them to exit
-			submittingBlocks.Store(false)
-			unittest.RequireReturnsBefore(t, wg.Wait, time.Second, "expect workers to stop producing")
+		// Block until the target block is finalized. The callback above fires from within the
+		// HotStuff finalization goroutine (inside the bubble) and sends on this channel, which
+		// unblocks the main goroutine.
+		<-finalized
 
-			// stop engines and wait for graceful shutdown
-			cancel()
-			unittest.RequireCloseBefore(t, moduleutil.AllDone(engine, followerLoop), 10*time.Second, "engine failed to stop")
-			// Note: in case any error occur, the `mockCtx` will fail the test, due to the unexpected call of `Throw` on the mock.
-		}()
-
-		// wait for target block to become finalized, this might take a while.
-		require.Eventually(t, func() bool {
-			final, err := followerState.Final().Head()
-			require.NoError(t, err)
-			success := final.Height == targetBlockHeight
-			if !success {
-				t.Logf("finalized height %d, waiting for %d", final.Height, targetBlockHeight)
-			} else {
-				t.Logf("successfully finalized target height %d\n", targetBlockHeight)
-			}
-			return success
-		}, 90*time.Second, time.Second, "expect to process all blocks before timeout")
+		// stop producers and wait for them to exit, then wait for engine shutdown.
+		submittingBlocks.Store(false)
 
+		// Note: in case any error occur, the `mockCtx` will fail the test, due to the unexpected call of `Throw` on the mock.
+		// shutdown is in defer
 	})
 }
```
