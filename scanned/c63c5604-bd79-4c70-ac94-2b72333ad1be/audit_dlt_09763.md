# [?] fix: prevent pebble:closed panic in TestFollowerHappyPath shutdown

## Summary
Severity: Unknown
Chain: Flow
Component: onflow/flow-go
Published: 2026-02-27
Source: https://github.com/onflow/flow-go/commit/e9ea929e6d9ad92f8d0fdf723240e793e385ef6e
Type: security-commit

## Details
fix: prevent pebble:closed panic in TestFollowerHappyPath shutdown

Co-Authored-By: Claude Sonnet 4.6 (1M context) <noreply@anthropic.com>

## Patch
### engine/common/follower/integration_test.go
```diff
@@ -214,11 +214,22 @@ func TestFollowerHappyPath(t *testing.T) {
 		defer func() {
 			// stop producers and wait for them to exit
 			submittingBlocks.Store(false)
+			// Cancel context before waiting for producers, so the engine starts shutting down
+			// even if the producer-wait times out.
+			cancel()
 			unittest.RequireReturnsBefore(t, wg.Wait, time.Second, "expect workers to stop producing")
 
-			// stop engines and wait for graceful shutdown
-			cancel()
-			unittest.RequireCloseBefore(t, moduleutil.AllDone(engine, followerLoop), 10*time.Second, "engine failed to stop")
+			// Wait for engine shutdown. processCertifiedBlocks does not check context
+			// cancellation within its loop, so a large connected-block batch can take
+			// longer than a short fixed timeout. Use t.Errorf (non-fatal) so the defer
+			// always runs to completion: a fatal assertion here calls runtime.Goexit(),
+			// which would leave engine goroutines running while pebble is closed, causing
+			// a "pebble: closed" panic that obscures the real test failure.
+			select {
+			case <-moduleutil.AllDone(engine, followerLoop):
+			case <-time.After(30 * time.Second):
+				t.Errorf("engine failed to stop")
+			}
 			// Note: in case any error occur, the `mockCtx` will fail the test, due to the unexpected call of `Throw` on the mock.
 		}()
 
```
