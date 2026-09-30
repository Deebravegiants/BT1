# [?] Merge remote-tracking branch 'origin/master' into peterargue/fix-follower-happy-path-pebble-panic

## Summary
Severity: Unknown
Chain: Flow
Component: onflow/flow-go
Published: 2026-02-27
Source: https://github.com/onflow/flow-go/commit/2a5028b5677100ed797d38b91ad3b7a4c68749a6
Type: security-commit

## Details
Merge remote-tracking branch 'origin/master' into peterargue/fix-follower-happy-path-pebble-panic

## Patch
### engine/verification/assigner/blockconsumer/consumer_test.go
```diff
@@ -77,18 +77,20 @@ func TestProduceConsume(t *testing.T) {
 		var processAll sync.WaitGroup
 		alwaysFinish := func(notifier module.ProcessingNotifier, block *flow.Block) {
 			lock.Lock()
-			defer lock.Unlock()
-
 			received = append(received, block)
+			lock.Unlock()
 
-			go func() {
-				notifier.Notify(block.ID())
-				processAll.Done()
-			}()
+			notifier.Notify(block.ID())
+			processAll.Done()
 		}
 
 		withConsumer(t, 100, 3, alwaysFinish, func(consumer *blockconsumer.BlockConsumer, blocks []*flow.Block, followerDistributor *pubsub.FollowerDistributor) {
 			unittest.RequireCloseBefore(t, consumer.Ready(), time.Second, "could not start consumer")
+			// defer shutdown to ensure it runs even if a `unittest.Require*` fails.
+			// this helps avoid a "pebble: closed" panic when the test times out.
+			defer func() {
+				unittest.RequireCloseBefore(t, consumer.Done(), time.Second, "could not terminate consumer")
+			}()
 			processAll.Add(len(blocks))
 
 			for i := 0; i < len(blocks); i++ {
@@ -100,7 +102,6 @@ func TestProduceConsume(t *testing.T) {
 
 			// waits until all blocks finish processing
 			unittest.RequireReturnsBefore(t, processAll.Wait, time.Second, "could not process all blocks on time")
-			unittest.RequireCloseBefore(t, consumer.Done(), time.Second, "could not terminate consumer")
 
 			// expects the mock engine receive all 100 blocks.
 			require.ElementsMatch(t, flow.GetIDs(blocks), flow.GetIDs(received))
```
