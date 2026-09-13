# [?] Fix BackgroundTaskScheduler queue overflow during block processing (#10488)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-02-12
Source: https://github.com/NethermindEth/nethermind/commit/bd3af149a27893beacf588529d2e89eaa150761e
Type: security-commit

## Details
Fix BackgroundTaskScheduler queue overflow during block processing (#10488)

* Initial plan

* Fix BackgroundTaskScheduler queue overflow by removing signal wait from scheduler threads

During block processing, ManualResetEventSlim blocked all scheduler threads
in BelowNormalPriorityTaskScheduler, preventing StartChannel from draining
expired tasks. New tasks (P2P transaction messages) continued arriving,
filling the queue beyond capacity (1024) and triggering task drops.

Fix: Remove the ManualResetEventSlim signal entirely. The existing
cancellation token mechanism in StartChannel already handles block
processing correctly — expired tasks get drained with cancelled tokens
(fast return), while non-expired tasks are re-queued with a 1ms throttle
until their deadline passes or block processing ends.

Co-authored-by: kamilchodola <43241881+kamilchodola@users.noreply.github.com>

* Replace blocking ManualResetEventSlim with async TaskCompletionSource signal; add high-capacity stress test

The original ManualResetEventSlim blocked scheduler threads in
ProcessBackgroundTasks(), preventing StartChannel from draining expired
tasks during block processing. Replace with TaskCompletionSource-based
async signal awaited in StartChannel's Throttle path.

Add comprehensive stress test that fills a 1024-capacity queue across
multiple block processing cycles, verifying:
- Tasks are dropped when queue exceeds capacity
- Expired tasks drain with cancelled tokens during block processing
- Queue recovers and accepts new tasks after draining
- Mixed short/long-lived tasks behave correctly across cycles
- Queue remains fully operational after repeated block processing

Co-authored-by: kamilchodola <43241881+kamilchodola@users.noreply.github.com>

* Double BackgroundTaskMaxNumber default from 1024 to 2048

Co-authored-by: benaadams <1142958+benaadams@users.noreply.github.com>

* Add BenchmarkDotNet benchmark for BackgroundTaskScheduler throughput

Adds BackgroundTaskSchedulerBenchmarks with two scenarios:
- ScheduleAndDrainDuringBlockProcessing: simulates real-world scenario
  with periodic block-processing pauses (5 cycles, 50ms each)
- ScheduleAndDrainWithoutBlockProcessing: baseline without interruptions

Parameters: capacity (1024/2048), concurrency (2), block processing
duration (50ms), cycles (5).

Also fixes flaky over-capacity assertion in stress test that raced
with the async task draining.

Co-authored-by: kamilchodola <43241881+kamilchodola@users.noreply.github.com>

---------

Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>
Co-authored-by: kamilchodola <43241881+kamilchodola@users.noreply.github.com>
Co-authored-by: benaadams <1142958+benaadams@users.noreply.github.com>

### src/Nethermind/Nethermind.Api/IInitConfig.cs
```diff
@@ -93,7 +93,7 @@ public interface IInitConfig : IConfig
     [ConfigItem(Description = "[TECHNICAL] Specify concurrency limit for background task.", DefaultValue = "2", HiddenFromDocs = true)]
     int BackgroundTaskConcurrency { get; set; }
 
-    [ConfigItem(Description = "[TECHNICAL] Specify max number of background task.", DefaultValue = "1024", HiddenFromDocs = true)]
+    [ConfigItem(Description = "[TECHNICAL] Specify max number of background task.", DefaultValue = "2048", HiddenFromDocs = true)]
     int BackgroundTaskMaxNumber { get; set; }
 
     [ConfigItem(Description = "[TECHNICAL] True when in runner test. Disable some wait.", DefaultValue = "false", HiddenFromDocs = true)]
```

### src/Nethermind/Nethermind.Api/InitConfig.cs
```diff
@@ -38,7 +38,7 @@ public class InitConfig : IInitConfig
         public long? ExitOnBlockNumber { get; set; } = null;
         public bool ExitOnInvalidBlock { get; set; } = false;
         public int BackgroundTaskConcurrency { get; set; } = 2;
-        public int BackgroundTaskMaxNumber { get; set; } = 1024;
+        public int BackgroundTaskMaxNumber { get; set; } = 2048;
         public bool InRunnerTest { get; set; } = false;
         public string? DataDir { get; set; }
 
```

### src/Nethermind/Nethermind.Benchmark/Scheduler/BackgroundTaskSchedulerBenchmarks.cs
```diff
@@ -0,0 +1,181 @@
+// SPDX-FileCopyrightText: 2025 Demerzel Solutions Limited
+// SPDX-License-Identifier: LGPL-3.0-only
+
+#nullable enable
+
+using System;
+using System.Collections.Generic;
+using System.Threading;
+using System.Threading.Tasks;
+using BenchmarkDotNet.Attributes;
+using Nethermind.Consensus.Processing;
+using Nethermind.Consensus.Scheduler;
+using Nethermind.Core;
+using Nethermind.Core.Specs;
+using Nethermind.Evm.State;
+using Nethermind.Evm.Tracing;
+using Nethermind.Int256;
+using Nethermind.Logging;
+using Nethermind.TxPool;
+
+namespace Nethermind.Benchmarks.Scheduler;
+
+/// <summary>
+/// Benchmarks the throughput of the BackgroundTaskScheduler under concurrent task
+/// scheduling with periodic block-processing pauses — the scenario that caused
+/// the "Background task queue is full" issue on synced nodes.
+/// </summary>
+[MemoryDiagnoser]
+[SimpleJob(warmupCount: 2, iterationCount: 5)]
+public class BackgroundTaskSchedulerBenchmarks
+{
+    private StubBranchProcessor _branchProcessor = null!;
+    private StubChainHeadInfoProvider _chainHeadInfo = null!;
+
+    [Params(1024, 2048)]
+    public int Capacity { get; set; }
+
+    [Params(2)]
+    public int Concurrency { get; set; }
+
+    [Params(50)]
+    public int BlockProcessingDurationMs { get; set; }
+
+    [Params(5)]
+    public int BlockProcessingCycles { get; set; }
+
+    [GlobalSetup]
+    public void Setup()
+    {
+        _branchProcessor = new StubBranchProcessor();
+        _chainHeadInfo = new StubChainHeadInfoProvider();
+    }
+
+    /// <summary>
+    /// Simulates the real-world scenario: a background producer keeps scheduling tasks
+    /// while block-processing cycles pause and resume execution.  Measures total wall-clock
+    /// time for scheduling + draining all tasks across several block-processing windows.
+    /// </summary>
+    [Benchmark]
+    public async Task ScheduleAndDrainDuringBlockProcessing()
+    {
+        await using BackgroundTaskScheduler scheduler = new(
+            _branchProcessor, _chainHeadInfo, Concurrency, Capacity, LimboLogs.Instance);
+
+        int totalScheduled = 0;
+        int totalExecuted = 0;
+        int totalDropped = 0;
+
+        for (int cycle = 0; cycle < BlockProcessingCycles; cycle++)
+        {
+            // Simulate block arriving — cancels current tasks, pauses non-expired ones
+            _branchProcessor.RaiseBlocksProcessing();
+
+            // Schedule a burst of tasks while block is being processed
+            int batchSize = Capacity / 2;
+            for (int i = 0; i < batchSize; i++)
+            {
+                bool accepted = scheduler.TryScheduleTask(i, (_, token) =>
+                {
+                    Interlocked.Increment(ref totalExecuted);
+                    return Task.CompletedTask;
+                }, TimeSpan.FromMilliseconds(BlockProcessingDurationMs + 100));
+
+                if (accepted)
+                    Interlocked.Increment(ref totalScheduled);
+                else
+                    Interlocked.Increment(ref totalDropped);
+            }
+
+            // Simulate block processing time
+            await Task.Delay(BlockProcessingDurationMs);
+
+            // Block done — resume normal task execution
+            _branchProcessor.RaiseBlockProcessed();
+
+            // Wait for all scheduled tasks to drain before next cycle
+            SpinWait spin = default;
+            while (Volatile.Read(ref totalExecuted) < Volatile.Read(ref totalScheduled))
+            {
+                spin.SpinOnce();
+                if (spin.Count % 100 == 0)
+                    await Task.Yield();
+            }
+        }
+    }
+
+    /// <summary>
+    /// Measures pure scheduling throughput without block-processing interruptions.
+    /// Useful as a baseline to compare against <see cref="ScheduleAndDrainDuringBlockProcessing"/>.
+    /// </summary>
+    [Benchmark(Baseline = true)]
+    public async Task ScheduleAndDrainWithoutBlockProcessing()
+    {
+        await using BackgroundTaskScheduler scheduler = new(
+            _branchProcessor, _chainHeadInfo, Concurrency, Capacity, LimboLogs.Instance);
+
+        int totalScheduled = 0;
+        int totalExecuted = 0;
+
+        int totalTasks = (Capacity / 2) * BlockProcessingCycles;
+        for (int i = 0; i < totalTasks; i++)
+        {
+            bool accepted = scheduler.TryScheduleTask(i, (_, _) =>
+            {
+                Interlocked.Increment(ref totalExecuted);
+                return Task.CompletedTask;
+            });
+            if (accepted)
+                Interlocked.Increment(ref totalScheduled);
+        }
+
+        SpinWait spin = default;
+        while (Volatile.Read(ref totalExecuted) < Volatile.Read(ref totalScheduled))
+        {
+            spin.SpinOnce();
+            if (spin.Count % 100 == 0)
+                await Task.Yield();
+        }
+    }
+
+    /// <summary>
+    /// Minimal stub for <see cref="IBranchProcessor"/> to expose events without any real block processing.
+    /// </summary>
+    private sealed class StubBranchProcessor : IBranchProcessor
+    {
+        public event EventHandler<BlockProcessedEventArgs>? BlockProcessed;
+        public event EventHandler<BlocksProcessingEventArgs>? BlocksProcessing;
+#pragma warning disable CS0067 // Event is never used
+        public event EventHandler<BlockEventArgs>? BlockProcessing;
+#pragma warning restore CS0067
+
+        public Block[] Process(BlockHeader? baseBlock, IReadOnlyList<Block> suggestedBlocks,
+            ProcessingOptions processingOptions, IBlockTracer blockTracer, CancellationToken token = default)
+            => [];
+
+        public void RaiseBlocksProcessing() =>
+            BlocksProcessing?.Invoke(this, new BlocksProcessingEventArgs([]));
+
+        public void RaiseBlockProcessed() =>
+            BlockProcessed?.Invoke(this, new BlockProcessedEventArgs(null!, null!));
+    }
+
+    /// <summary>
+    /// Minimal stub for <see cref="IChainHeadInfoProvider"/> — reports node as not syncing.
+    /// </summary>
+    private sealed class StubChainHeadInfoProvider : IChainHeadInfoProvider
+    {
+        public IChainHeadSpecProvider SpecProvider => null!;
+        public IReadOnlyStateProvider ReadOnlyStateProvider => null!;
+        public long HeadNumber => 0;
+        public long? BlockGasLimit => null;
+        public UInt256 CurrentBaseFee => UInt256.Zero;
+        public UInt256 CurrentFeePerBlobGas => UInt256.Zero;
+        public ProofVersion CurrentProofVersion => ProofVersion.V0;
+        public bool IsSyncing => false;
+        public bool IsProcessingBlock => false;
+#pragma warning disable CS0067 // Event is never used
+        public event EventHandler<BlockReplacementEventArgs>? HeadChanged;
+#pragma warning restore CS0067
+    }
+}
```

### src/Nethermind/Nethermind.Consensus.Test/Scheduler/BackgroundTaskSchedulerTests.cs
```diff
@@ -142,4 +142,179 @@ public async Task Test_task_that_is_scheduled_during_block_processing_but_deadli
 
         wasCancelled.Should().BeTrue();
     }
+
+    [Test]
+    public async Task Test_expired_tasks_are_drained_during_block_processing()
+    {
+        int capacity = 16;
+        await using BackgroundTaskScheduler scheduler = new(_branchProcessor, _chainHeadInfo, 1, capacity, LimboLogs.Instance);
+
+        // Start block processing — signal is reset, token cancelled
+        _branchProcessor.BlocksProcessing += Raise.EventWith(new BlocksProcessingEventArgs(null));
+
+        int cancelledCount = 0;
+        for (int i = 0; i < capacity; i++)
+        {
+            scheduler.TryScheduleTask(1, (_, token) =>
+            {
+                if (token.IsCancellationRequested)
+                {
+                    Interlocked.Increment(ref cancelledCount);
+                }
+                return Task.CompletedTask;
+            }, TimeSpan.FromMilliseconds(1));
+        }
+
+        // Expired tasks should be drained even while block processing is in progress
+        Assert.That(() => cancelledCount, Is.EqualTo(capacity).After(2000, 10));
+
+        _branchProcessor.BlockProcessed += Raise.EventWith(new BlockProcessedEventArgs(null, null));
+    }
+
+    [Test]
+    public async Task Test_queue_accepts_new_tasks_after_expired_tasks_drain_during_block_processing()
+    {
+        int capacity = 16;
+        await using BackgroundTaskScheduler scheduler = new(_branchProcessor, _chainHeadInfo, 1, capacity, LimboLogs.Instance);
+
+        // Start block processing — signal is reset, token cancelled
+        _branchProcessor.BlocksProcessing += Raise.EventWith(new BlocksProcessingEventArgs(null));
+
+        // Fill the queue with short-lived tasks
+        for (int i = 0; i < capacity; i++)
+        {
+            scheduler.TryScheduleTask(1, (_, _) => Task.CompletedTask, TimeSpan.FromMilliseconds(1)).Should().BeTrue();
+        }
+
+        // Wait for deadlines to pass and expired tasks to be drained
+        await Task.Delay(200);
+
+        // New tasks should be accepted because expired tasks freed up queue space
+        for (int i = 0; i < capacity; i++)
+        {
+            bool accepted = scheduler.TryScheduleTask(1, (_, _) => Task.CompletedTask, TimeSpan.FromMilliseconds(1));
+            accepted.Should().BeTrue($"Task {i} should be accepted after expired tasks were drained");
+        }
+
+        _branchProcessor.BlockProcessed += Raise.EventWith(new BlockProcessedEventArgs(null, null));
+    }
+
+    [Test]
+    public async Task Test_high_capacity_queue_survives_repeated_block_processing_cycles()
+    {
+        int capacity = 1024;
+        int concurrency = 2;
+        await using BackgroundTaskScheduler scheduler = new(_branchProcessor, _chainHeadInfo, concurrency, capacity, LimboLogs.Instance);
+
+        int executedCount = 0;
+        int cancelledCount = 0;
+
+        // --- Phase 1: Fill the queue to capacity during block processing ---
+        _branchProcessor.BlocksProcessing += Raise.EventWith(new BlocksProcessingEventArgs(null));
+
+        for (int i = 0; i < capacity; i++)
+        {
+            bool accepted = scheduler.TryScheduleTask(1, (_, token) =>
+            {
+                if (token.IsCancellationRequested)
+                    Interlocked.Increment(ref cancelledCount);
+                else
+                    Interlocked.Increment(ref executedCount);
+                return Task.CompletedTask;
+            }, TimeSpan.FromMilliseconds(10));
+            accepted.Should().BeTrue($"Phase 1: task {i} should be accepted up to capacity");
+        }
+
+        // Wait for deadlines to expire and tasks to drain
+        Assert.That(
+            () => Volatile.Read(ref cancelledCount),
+            Is.EqualTo(capacity).After(5000, 10),
+            "all tasks should be drained with cancelled tokens during block processing");
+
+        // --- Phase 2: End block processing, verify queue accepts tasks and runs them normally ---
+        _branchProcessor.BlockProcessed += Raise.EventWith(new BlockProcessedEventArgs(null, null));
+
+        Interlocked.Exchange(ref executedCount, 0);
+
+        int phase2Count = capacity / 2;
+        for (int i = 0; i < phase2Count; i++)
+        {
+            bool accepted = scheduler.TryScheduleTask(1, (_, _) =>
+            {
+                Interlocked.Increment(ref executedCount);
+                return Task.CompletedTask;
+            });
+            accepted.Should().BeTrue($"Phase 2: task {i} should be accepted after queue drained");
+        }
+
+        Assert.That(
+            () => Volatile.Read(ref executedCount),
+            Is.EqualTo(phase2Count).After(5000, 10),
+            "all phase 2 tasks should execute normally after block processing ends");
+
+        // --- Phase 3: Another block processing cycle with mixed short and long timeouts ---
+        _branchProcessor.BlocksProcessing += Raise.EventWith(new BlocksProcessingEventArgs(null));
+
+        int phase3CancelledCount = 0;
+        int phase3ExecutedCount = 0;
+
+        // Short-lived tasks (will expire during block processing)
+        int shortLivedCount = capacity / 2;
+        for (int i = 0; i < shortLivedCount; i++)
+        {
+            scheduler.TryScheduleTask(1, (_, token) =>
+            {
+                if (token.IsCancellationRequested)
+                    Interlocked.Increment(ref phase3CancelledCount);
+                return Task.CompletedTask;
+            }, TimeSpan.FromMilliseconds(5)).Should().BeTrue($"Phase 3: short-lived task {i} should be accepted");
+        }
+
+        // Long-lived tasks (will survive until block processing ends)
+        int longLivedCount = capacity / 4;
+        for (int i = 0; i < longLivedCount; i++)
+        {
+            scheduler.TryScheduleTask(1, (_, token) =>
+            {
+                if (!token.IsCancellationRequested)
+                    Interlocked.Increment(ref phase3ExecutedCount);
+                return Task.CompletedTask;
+            }, TimeSpan.FromSeconds(30)).Should().BeTrue($"Phase 3: long-lived task {i} should be accepted");
+        }
+
+        // Wait for short-lived tasks to expire and drain
+        Assert.That(
+            () => Volatile.Read(ref phase3CancelledCount),
+            Is.EqualTo(shortLivedCount).After(5000, 10),
+            "short-lived tasks should drain with cancelled tokens during block processing");
+
+        // Long-lived tasks should not have executed yet (still waiting for block processing to end)
+        Volatile.Read(ref phase3ExecutedCount).Should().Be(0,
+            "long-lived tasks should wait during block processing");
+
+        // End block processing — long-lived tasks should now execute
+        _branchProcessor.BlockProcessed += Raise.EventWith(new BlockProcessedEventArgs(null, null));
+
+        Assert.That(
+            () => Volatile.Read(ref phase3ExecutedCount),
+            Is.EqualTo(longLivedCount).After(5000, 10),
+            "long-lived tasks should execute after block processing ends");
+
+        // --- Phase 4: Verify queue is fully operational with one more fill-and-drain ---
+        Interlocked.Exchange(ref executedCount, 0);
+
+        for (int i = 0; i < capacity; i++)
+        {
+            scheduler.TryScheduleTask(1, (_, _) =>
+            {
+                Interlocked.Increment(ref executedCount);
+                return Task.CompletedTask;
+            }).Should().BeTrue($"Phase 4: task {i} should be accepted in fully recovered queue");
+        }
+
+        Assert.That(
+            () => Volatile.Read(ref executedCount),
+            Is.EqualTo(capacity).After(5000, 10),
+            "all tasks in the final phase should execute successfully");
+    }
 }
```

### src/Nethermind/Nethermind.Consensus/Scheduler/BackgroundTaskScheduler.cs
```diff
@@ -34,7 +34,6 @@ public class BackgroundTaskScheduler : IBackgroundTaskScheduler, IAsyncDisposabl
     private readonly CancellationTokenSource _mainCancellationTokenSource;
     private readonly Channel<IActivity> _taskQueue;
     private readonly BelowNormalPriorityTaskScheduler _scheduler;
-    private readonly ManualResetEventSlim _restartQueueSignal;
     private readonly Task[] _tasksExecutors;
     private readonly ILogger _logger;
     private readonly IBranchProcessor _branchProcessor;
@@ -43,6 +42,7 @@ public class BackgroundTaskScheduler : IBackgroundTaskScheduler, IAsyncDisposabl
     private long _queueCount;
 
     private CancellationTokenSource _blockProcessorCancellationTokenSource;
+    private volatile TaskCompletionSource? _blockProcessingDoneSignal;
     private bool _disposed = false;
 
     public BackgroundTaskScheduler(IBranchProcessor branchProcessor, IChainHeadInfoProvider headInfo, int concurrency, int capacity, ILogManager logManager)
@@ -65,7 +65,6 @@ public BackgroundTaskScheduler(IBranchProcessor branchProcessor, IChainHeadInfoP
         _logger = logManager.GetClassLogger();
         _branchProcessor = branchProcessor;
         _headInfo = headInfo;
-        _restartQueueSignal = new ManualResetEventSlim(initialState: true);
         _capacity = capacity;
 
         _branchProcessor.BlocksProcessing += BranchProcessorOnBranchesProcessing;
@@ -74,7 +73,6 @@ public BackgroundTaskScheduler(IBranchProcessor branchProcessor, IChainHeadInfoP
         // TaskScheduler to run tasks at BelowNormal priority
         _scheduler = new BelowNormalPriorityTaskScheduler(
             concurrency,
-            _restartQueueSignal,
             logManager,
             _mainCancellationTokenSource.Token);
 
@@ -88,8 +86,9 @@ private void BranchProcessorOnBranchesProcessing(object? sender, BlocksProcessin
         // as there are potentially no gaps between blocks
         if (!_headInfo.IsSyncing)
         {
-            // Reset the background queue processing signal, causing it to wait
-            _restartQueueSignal.Reset();
+            // Signal that block processing is in progress so the Throttle path in StartChannel
+            // can async-wait instead of busy-polling
+            _blockProcessingDoneSignal = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
             // On block processing, we cancel the block process cts, causing the current task to get canceled.
             _blockProcessorCancellationTokenSource.Cancel();
         }
@@ -102,8 +101,8 @@ private void BranchProcessorOnBranchProcessed(object? sender, BlockProcessedEven
             ref _blockProcessorCancellationTokenSource,
             new CancellationTokenSource());
 
-        // We also set a queue signal causing it to continue processing the task.
-        _restartQueueSignal.Set();
+        // Signal that block processing is done so the Throttle path can resume
+        Interlocked.Exchange(ref _blockProcessingDoneSignal, null)?.TrySetResult();
     }
 
     private async Task StartChannel()
@@ -157,7 +156,16 @@ private async Task StartChannel()
             continue;
 
         Throttle:
-            await Task.Delay(millisecondsDelay: 1);
+            // Wait for block processing to complete, with periodic wake-ups to drain newly expired tasks
+            TaskCompletionSource? signal = _blockProcessingDoneSignal;
+            if (signal is not null)
+            {
+                await Task.WhenAny(signal.Task, Task.Delay(millisecondsDelay: 1));
+            }
+            else
+            {
+                await Task.Delay(millisecondsDelay: 1);
+            }
         }
     }
 
@@ -250,17 +258,15 @@ private sealed class BelowNormalPriorityTaskScheduler : TaskScheduler, IDisposab
     {
         private readonly BlockingCollection<Task> _tasks = [];
         private readonly Thread[] workerThreads;
-        private readonly ManualResetEventSlim _restartQueueSignal;
         private readonly int _maxDegreeOfParallelism;
         private readonly ILogger _logger;
         private readonly CancellationToken _cancellationToken;
 
-        public BelowNormalPriorityTaskScheduler(int maxDegreeOfParallelism, ManualResetEventSlim restartQueueSignal, ILogManager logManager, CancellationToken cancellationToken)
+        public BelowNormalPriorityTaskScheduler(int maxDegreeOfParallelism, ILogManager logManager, CancellationToken cancellationToken)
         {
             ArgumentOutOfRangeException.ThrowIfLessThan(maxDegreeOfParallelism, 1);
 
             _logger = logManager.GetClassLogger();
-            _restartQueueSignal = restartQueueSignal;
             _maxDegreeOfParallelism = maxDegreeOfParallelism;
             _cancellationToken = cancellationToken;
             workerThreads = [.. Enumerable.Range(0, maxDegreeOfParallelism)
@@ -283,8 +289,6 @@ private void ProcessBackgroundTasks(object _)
             {
                 foreach (Task task in _tasks.GetConsumingEnumerable(_cancellationToken))
                 {
-                    // Wait if processing blocks
-                    _restartQueueSignal.Wait(_cancellationToken);
                     try
                     {
                         TryExecuteTask(task);
```
