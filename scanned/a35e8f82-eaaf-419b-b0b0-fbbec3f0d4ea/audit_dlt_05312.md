# [?] Fix flaky TestFollowerHappyPath panic on pebble DB close

## Summary
Severity: Unknown
Chain: Flow
Component: onflow/flow-go
Published: 2026-02-25
Source: https://github.com/onflow/flow-go/commit/a5199f4cdf156db3864a30083f2c411ef027e024
Type: security-commit

## Details
Fix flaky TestFollowerHappyPath panic on pebble DB close

Increase teardown AllDone timeout from 1s to 10s to give the engine
enough time to drain queued work after cancellation.

Co-Authored-By: Claude Sonnet 4.6 (1M context) <noreply@anthropic.com>

## Patch
### engine/common/follower/integration_test.go
```diff
@@ -218,7 +218,7 @@ func TestFollowerHappyPath(t *testing.T) {
 
 			// stop engines and wait for graceful shutdown
 			cancel()
-			unittest.RequireCloseBefore(t, moduleutil.AllDone(engine, followerLoop), time.Second, "engine failed to stop")
+			unittest.RequireCloseBefore(t, moduleutil.AllDone(engine, followerLoop), 10*time.Second, "engine failed to stop")
 			// Note: in case any error occur, the `mockCtx` will fail the test, due to the unexpected call of `Throw` on the mock.
 		}()
 
```
