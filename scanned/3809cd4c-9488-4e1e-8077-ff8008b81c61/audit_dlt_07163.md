# [?] wtclient: ensure correct disk mode for overflow queue

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
Published: 2024-01-12
Source: https://github.com/lightningnetwork/lnd/commit/3d201dde505ea8109cce3d6a4475f61b349c9df4
Type: security-commit

## Details
wtclient: ensure correct disk mode for overflow queue

Before this commit, in the watchtower client's DiskOverflowQueue, there
could be a situation _if no consumer was reading from the queue_ that
could lead to an in-memory build up of backup tasks instead of the
expected disk overflow. This commit fixes this by ensuring that if a
task is read from disk, then the mode is set to disk mode to ensure that
any new items are persisted to disk in this scenario.
The unit tests added in the previous commit is updated here in order to
show that the fix does in-fact fix the test.

## Patch
### docs/release-notes/release-notes-0.18.0.md
```diff
@@ -49,7 +49,7 @@
   same exclusive group](https://github.com/lightningnetwork/lnd/pull/7800).
   When using neutrino as a backend unconfirmed transactions have to be
   removed from the wallet when a conflicting tx is confirmed. For other backends
-  these unconfirmed transactions are already removed. In addition a new 
+  these unconfirmed transactions are already removed. In addition, a new 
   walletrpc endpoint `RemoveTransaction` is introduced which let one easily
   remove unconfirmed transaction manually.
   
@@ -61,6 +61,9 @@
   this buffer which can be used to increase the commitment fee and it also
   protects against the case where htlcs are added asynchronously resulting in
   stuck channels.
+ 
+* [Fixed](https://github.com/lightningnetwork/lnd/pull/8377) a watchtower client
+  test flake that prevented new tasks from overflowing to disk. 
 
 * [Properly handle un-acked updates for exhausted watchtower 
   sessions](https://github.com/lightningnetwork/lnd/pull/8233)
```

### watchtower/wtclient/queue.go
```diff
@@ -529,6 +529,13 @@ func (q *DiskOverflowQueue[T]) feedMemQueue() {
 				}
 			}
 
+			// If we did manage to fetch a task from disk, we make
+			// sure to set the toDisk mode to true since we may
+			// block indefinitely while trying to push the tasks to
+			// the memQueue in which case we want the drainInputList
+			// goroutine to write any new tasks to disk.
+			q.toDisk.Store(true)
+
 			for i, task := range tasks {
 				select {
 				case q.memQueue <- task:
```

### watchtower/wtclient/queue_test.go
```diff
@@ -75,9 +75,9 @@ func TestDiskOverflowQueue(t *testing.T) {
 	}
 }
 
-// demoFlake is a temporary test demonstrating race condition that currently
-// exists in the DiskOverflowQueue. It contrives a scenario that results in
-// the queue being in memory mode when it really should be in disk mode.
+// demoFlake is a temporary test demonstrating the fix of a race condition that
+// existed in the DiskOverflowQueue. It contrives a scenario that once resulted
+// in the queue being in memory mode when it really should be in disk mode.
 func demoFlake(t *testing.T, db wtdb.Queue[*wtdb.BackupID]) {
 	// Generate some backup IDs that we want to add to the queue.
 	tasks := genBackupIDs(10)
@@ -147,21 +147,25 @@ func demoFlake(t *testing.T, db wtdb.Queue[*wtdb.BackupID]) {
 	}, waitTime)
 	require.NoError(t, err)
 
-	// Now, we allow task 4 to be written to disk. NOTE that this is
-	// happening while the mode is memory mode! This is the bug! This will
-	// result in a newDiskItemsSignal being sent meaning that feedMemQueue
-	// will read from disk and block on pushing the new item to memQueue.
+	// Now, we allow task 4 to be written to disk. This will result in a
+	// newDiskItemsSignal being sent meaning that feedMemQueue will read
+	// from disk and block on pushing the new item to memQueue.
 	q.allowDiskWrite()
 
-	// Now, if we enqueue task 5, it will _not_ be written to disk since the
-	// queue is currently in memory mode. This is the bug that needs to be
-	// fixed.
+	// The above will result in feeMemQueue switching the mode to disk-mode.
+	err = wait.Predicate(func() bool {
+		return q.toDisk.Load()
+	}, waitTime)
+	require.NoError(t, err)
+
+	// Now, if we enqueue task 5, it _will_ be written to disk since the
+	// queue is currently in disk mode.
 	enqueue(t, q, tasks[5])
 	q.allowDiskWrite()
 
-	// Show that there are no items on disk at this point. When the bug is
-	// fixed, this should be changed to 1.
-	waitForNumDisk(t, db, 0)
+	// Show that there is an item on disk at this point. This demonstrates
+	// that the bug has been fixed.
+	waitForNumDisk(t, db, 1)
 
 	require.NoError(t, q.Stop())
 }
```
