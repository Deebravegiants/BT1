# [?] fix: BackgroundTaskScheduler disposal deadlock causing CI timeouts (#10927)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-03-23
Source: https://github.com/NethermindEth/nethermind/commit/82ab1a7e5d75a37f60b60f5523a567485b365ab2
Type: security-commit

## Details
fix: BackgroundTaskScheduler disposal deadlock causing CI timeouts (#10927)

* fix: resolve BackgroundTaskScheduler disposal deadlock causing CI timeouts

The scheduler worker threads exited on cancellation before StartChannel()
continuations could complete, causing Task.WhenAll to wait forever.

- Remove CancellationToken from BelowNormalPriorityTaskScheduler workers
  so they stay alive until CompleteAdding() is called via Dispose()
- Wrap StartChannel() outer loop with OperationCanceledException catch
  so WaitToReadAsync cancellation completes the task cleanly
- Workers now exit naturally after executor tasks finish, not before

* fix: address PR feedback - TryWrite guard, OCE filter, test timeout

- Only increment _queueCount if TryWrite succeeds; if re-queue fails
  (channel completed during dispose), fall through to run with cancelled
  token instead of skewing the counter
- Filter inner OCE catch with `when (cts.IsCancellationRequested)` to
  avoid swallowing unexpected cancellations from activity handlers
- Increase test timeout from 2s to 5s with assertion message for CI

* fix: Assert.DoesNotThrowAsync returns void, not Task - remove await

## Patch
### src/Nethermind/Nethermind.Consensus.Test/Scheduler/BackgroundTaskSchedulerTests.cs
```diff
@@ -44,6 +44,16 @@ public async Task Test_task_will_execute()
         await tcs.Task;
     }
 
+    [Test]
+    public async Task DisposeAsync_should_complete_when_scheduler_is_idle()
+    {
+        BackgroundTaskScheduler scheduler = new BackgroundTaskScheduler(_branchProcessor, _chainHeadInfo, 1, 65536, LimboLogs.Instance);
+
+        Assert.DoesNotThrowAsync(
+            async () => await scheduler.DisposeAsync().AsTask().WaitAsync(TimeSpan.FromSeconds(5)),
+            "DisposeAsync did not complete within timeout - possible deadlock in background task scheduler");
+    }
+
     [Test]
     public async Task Test_task_will_execute_concurrently_when_configured_so()
     {
```

### src/Nethermind/Nethermind.Consensus/Scheduler/BackgroundTaskScheduler.cs
```diff
@@ -69,8 +69,7 @@ public BackgroundTaskScheduler(IBranchProcessor branchProcessor, IChainHeadInfoP
         // TaskScheduler to run tasks at BelowNormal priority
         _scheduler = new BelowNormalPriorityTaskScheduler(
             concurrency,
-            logManager,
-            _mainCancellationTokenSource.Token);
+            logManager);
 
         TaskFactory factory = new(_scheduler);
         _tasksExecutors = [.. Enumerable.Range(0, concurrency).Select(_ => factory.StartNew(StartChannel).Unwrap())];
@@ -104,63 +103,73 @@ private void BranchProcessorOnBranchProcessed(object? sender, BlockProcessedEven
 
     private async Task StartChannel()
     {
-        while (await _taskQueue.Reader.WaitToReadAsync(_mainCancellationTokenSource.Token))
+        try
         {
-            // Create fresh CancellationTokenSource for current block processing
-            CancellationTokenSource cts = CancellationTokenSource.CreateLinkedTokenSource(
-                        _blockProcessorCancellationTokenSource.Token,
-                        _mainCancellationTokenSource.Token);
-            try
+            while (await _taskQueue.Reader.WaitToReadAsync(_mainCancellationTokenSource.Token))
             {
-                CancellationToken token = cts.Token;
-                while (_taskQueue.Reader.TryRead(out IActivity activity))
+                // Create fresh CancellationTokenSource for current block processing
+                CancellationTokenSource cts = CancellationTokenSource.CreateLinkedTokenSource(
+                            _blockProcessorCancellationTokenSource.Token,
+                            _mainCancellationTokenSource.Token);
+                try
                 {
-                    Interlocked.Decrement(ref _queueCount);
-                    UpdateQueueCount();
-
-                    if (token.IsCancellationRequested)
+                    CancellationToken token = cts.Token;
+                    while (_taskQueue.Reader.TryRead(out IActivity activity))
                     {
-                        // Block processing is active. If the task still has time left, put it back
-                        // and wait for block processing to finish before resuming.
-                        if (DateTimeOffset.UtcNow < activity.Deadline)
+                        Interlocked.Decrement(ref _queueCount);
+                        UpdateQueueCount();
+
+                        if (token.IsCancellationRequested)
                         {
-                            Interlocked.Increment(ref _queueCount);
-                            _taskQueue.Writer.TryWrite(activity);
-                            UpdateQueueCount();
-                            // Wait for block processing to complete before draining more tasks
-                            goto WaitForBlockProcessing;
+                            // Block processing is active. If the task still has time left, put it back
+                            // and wait for block processing to finish before resuming.
+                            if (DateTimeOffset.UtcNow < activity.Deadline)
+                            {
+                                if (_taskQueue.Writer.TryWrite(activity))
+                                {
+                                    Interlocked.Increment(ref _queueCount);
+                                    UpdateQueueCount();
+                                    // Wait for block processing to complete before draining more tasks
+                                    goto WaitForBlockProcessing;
+                                }
+                                // Re-queue failed (channel completed during dispose) - fall through
+                                // and run with cancelled token so handler can clean up
+                            }
+
+                            // Task already expired or re-queue failed — run with cancelled token
                         }
 
-                        // Task already expired — run it with cancelled token so the handler can clean up
+                        await activity.Do(token);
+                        Evm.Metrics.IncrementTotalBackgroundTasksExecuted();
                     }
-
-                    await activity.Do(token);
-                    Evm.Metrics.IncrementTotalBackgroundTasksExecuted();
                 }
-            }
-            catch (OperationCanceledException)
-            {
-            }
-            catch (Exception e)
-            {
-                if (_logger.IsError) _logger.Error($"Error processing background task {e}.");
-            }
-            finally
-            {
-                cts.Dispose();
-            }
+                catch (OperationCanceledException) when (cts.IsCancellationRequested)
+                {
+                }
+                catch (Exception e)
+                {
+                    if (_logger.IsError) _logger.Error($"Error processing background task {e}.");
+                }
+                finally
+                {
+                    cts.Dispose();
+                }
 
-            continue;
+                continue;
 
-        WaitForBlockProcessing:
-            cts.Dispose();
-            // Wait for block processing to finish, but wake up periodically to drain expired tasks
-            TaskCompletionSource? signal = _blockProcessingDoneSignal;
-            if (signal is not null && !signal.Task.IsCompleted)
-            {
-                await Task.WhenAny(signal.Task, Task.Delay(100, _mainCancellationTokenSource.Token));
+            WaitForBlockProcessing:
+                // cts already disposed by the finally block above (goto exits the try)
+                // Wait for block processing to finish, but wake up periodically to drain expired tasks
+                TaskCompletionSource? signal = _blockProcessingDoneSignal;
+                if (signal is not null && !signal.Task.IsCompleted)
+                {
+                    await Task.WhenAny(signal.Task, Task.Delay(100, _mainCancellationTokenSource.Token));
+                }
             }
         }
+        catch (OperationCanceledException) when (_mainCancellationTokenSource.IsCancellationRequested)
+        {
+        }
     }
 
     public bool TryScheduleTask<TReq>(TReq request, Func<TReq, CancellationToken, Task> fulfillFunc, TimeSpan? timeout = null, string? source = null)
@@ -209,6 +218,8 @@ public async ValueTask DisposeAsync()
 
         _taskQueue.Writer.Complete();
         await _mainCancellationTokenSource.CancelAsync();
+        // StartChannel continuations run on the custom scheduler, so its workers must stay alive
+        // until they observe cancellation and complete.
         await Task.WhenAll(_tasksExecutors);
         _mainCancellationTokenSource.Dispose();
         _scheduler.Dispose();
@@ -263,15 +274,13 @@ private sealed class BelowNormalPriorityTaskScheduler : TaskScheduler, IDisposab
         private readonly Thread[] workerThreads;
         private readonly int _maxDegreeOfParallelism;
         private readonly ILogger _logger;
-        private readonly CancellationToken _cancellationToken;
 
-        public BelowNormalPriorityTaskScheduler(int maxDegreeOfParallelism, ILogManager logManager, CancellationToken cancellationToken)
+        public BelowNormalPriorityTaskScheduler(int maxDegreeOfParallelism, ILogManager logManager)
         {
             ArgumentOutOfRangeException.ThrowIfLessThan(maxDegreeOfParallelism, 1);
 
             _logger = logManager.GetClassLogger();
             _maxDegreeOfParallelism = maxDegreeOfParallelism;
-            _cancellationToken = cancellationToken;
             workerThreads = [.. Enumerable.Range(0, maxDegreeOfParallelism)
                             .Select(i =>
                             {
@@ -290,7 +299,7 @@ private void ProcessBackgroundTasks(object _)
         {
             try
             {
-                foreach (Task task in _tasks.GetConsumingEnumerable(_cancellationToken))
+                foreach (Task task in _tasks.GetConsumingEnumerable())
                 {
                     try
                     {
@@ -305,9 +314,6 @@ private void ProcessBackgroundTasks(object _)
                     }
                 }
             }
-            catch (OperationCanceledException)
-            {
-            }
             catch (Exception e)
             {
                 if (_logger.IsError) _logger.Error($"Error in background task processing {e}.");
```
