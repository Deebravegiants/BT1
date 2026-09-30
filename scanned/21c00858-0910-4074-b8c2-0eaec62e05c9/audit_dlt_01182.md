# [?] Fix race condition in ShutterBlockHandler (#10296)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-01-30
Source: https://github.com/NethermindEth/nethermind/commit/8d695ffdade80c0271bb673abe89aa881142f2e5
Type: security-commit

## Details
Fix race condition in ShutterBlockHandler (#10296)

* fix(shutter): add synchronization to CancelWaitForBlock to prevent race condition

* Add lock to Dispose

Co-authored-by: Lukasz Rozmej <lukasz.rozmej@gmail.com>

* Fix Dispose lock

* Fix test for async TCS completion

---------

Co-authored-by: Lukasz Rozmej <lukasz.rozmej@gmail.com>

## Patch
### src/Nethermind/Nethermind.Shutter.Test/ShutterBlockHandlerTests.cs
```diff
@@ -32,7 +32,7 @@ public void Can_wait_for_valid_block()
     }
 
     [Test]
-    public void Wait_times_out_at_cutoff()
+    public async Task Wait_times_out_at_cutoff()
     {
         Random rnd = new(ShutterTestsCommon.Seed);
         Timestamper timestamper = ShutterTestsCommon.InitTimestamper(ShutterTestsCommon.InitialSlotTimestamp, 0);
@@ -48,7 +48,8 @@ public void Wait_times_out_at_cutoff()
 
         Assert.That(waitTask.IsCompleted, Is.False);
         timeoutSource.Cancel();
-        Assert.That(waitTask.IsCompletedSuccessfully);
+        Block? result = await waitTask;
+        Assert.That(result, Is.Null);
     }
 
     [Test]
```

### src/Nethermind/Nethermind.Shutter/ShutterBlockHandler.cs
```diff
@@ -89,7 +89,7 @@ public ShutterBlockHandler(
 
             if (_logger.IsDebug) _logger.Debug($"Waiting for block in {slot} to get Shutter transactions.");
 
-            tcs = new();
+            tcs = new(TaskCreationOptions.RunContinuationsAsynchronously);
 
             long offset = _time.GetCurrentOffsetMs(slot);
             long waitTime = (long)_blockWaitCutoff.TotalMilliseconds - offset;
@@ -125,31 +125,39 @@ public ShutterBlockHandler(
     public void Dispose()
     {
         _blockTree.NewHeadBlock -= OnNewHeadBlock;
-        _blockWaitTasks.ForEach(static x => x.Value.ForEach(static waitTask =>
+        lock (_syncObject)
         {
-            waitTask.Value.CancellationRegistration.Dispose();
-            waitTask.Value.TimeoutCancellationRegistration.Dispose();
-        }));
+            _blockWaitTasks.ForEach(static x => x.Value.ForEach(static waitTask =>
+            {
+                waitTask.Value.CancellationRegistration.Dispose();
+                waitTask.Value.TimeoutCancellationRegistration.Dispose();
+            }));
+        }
     }
 
     private void CancelWaitForBlock(ulong slot, ulong taskId, bool timeout)
     {
-        if (_blockWaitTasks.TryGetValue(slot, out Dictionary<ulong, BlockWaitTask>? slotWaitTasks))
+        lock (_syncObject)
         {
-            if (slotWaitTasks.TryGetValue(taskId, out BlockWaitTask waitTask))
+            if (_blockWaitTasks.TryGetValue(slot, out Dictionary<ulong, BlockWaitTask>? slotWaitTasks))
             {
-                if (timeout)
-                {
-                    waitTask.Tcs.TrySetResult(null);
-                }
-                else
+                if (slotWaitTasks.TryGetValue(taskId, out BlockWaitTask waitTask))
                 {
-                    waitTask.Tcs.SetException(new OperationCanceledException());
+                    if (timeout)
+                    {
+                        waitTask.Tcs.TrySetResult(null);
+                    }
+                    else
+                    {
+                        waitTask.Tcs.SetException(new OperationCanceledException());
+                    }
+
+                    waitTask.CancellationRegistration.Dispose();
+                    waitTask.TimeoutCancellationRegistration.Dispose();
                 }
-                waitTask.CancellationRegistration.Dispose();
-                waitTask.TimeoutCancellationRegistration.Dispose();
+
+                slotWaitTasks.Remove(taskId);
             }
-            slotWaitTasks.Remove(taskId);
         }
     }
 
```
