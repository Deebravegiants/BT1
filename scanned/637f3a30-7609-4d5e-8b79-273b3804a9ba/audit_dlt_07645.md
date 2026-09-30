# [?] Fix startup warmup drain test scheduler deadlock (#13974)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-09-28
Source: https://github.com/NethermindEth/nethermind/commit/83c9fdce8adf6961e26113e20ce04c2f89f70517
Type: security-commit

## Details
Fix startup warmup drain test scheduler deadlock (#13974)

* fix(test): avoid warmup shutdown scheduler deadlock

* fix(test): make warmup drain assertion deterministic

## Patch
### src/Nethermind/Nethermind.Runner.Test/EthereumRunnerTests.cs
```diff
@@ -512,9 +512,7 @@ public async Task Startup_pipeline_warmup_drains_reports_before_container_dispos
         using ManualResetEventSlim release = new();
         TaskCompletionSource reporting = new(TaskCreationOptions.RunContinuationsAsynchronously);
         TaskCompletionSource stopped = new(TaskCreationOptions.RunContinuationsAsynchronously);
-        bool disposing = false;
-        ConcurrentExclusiveSchedulerPair scheduler = new(TaskScheduler.Default, maxConcurrencyLevel: 1);
-        TaskFactory cleanup = new(CancellationToken.None, TaskCreationOptions.None, TaskContinuationOptions.None, scheduler.ExclusiveScheduler);
+        TaskCompletionSource disposing = new(TaskCreationOptions.RunContinuationsAsynchronously);
         InterfaceLogger slowLogger = Substitute.For<InterfaceLogger>();
         slowLogger.IsWarn.Returns(true);
         slowLogger.When(logger => logger.Warn(Arg.Any<string>())).Do(_ =>
@@ -526,38 +524,33 @@ public async Task Startup_pipeline_warmup_drains_reports_before_container_dispos
         ILogger slowBlocks = new(slowLogger);
         logs.GetLogger("SlowBlocks").Returns(slowBlocks);
         logs.GetClassLogger<ProcessingStats>().Returns(LimboLogs.Instance.GetClassLogger<ProcessingStats>());
-        Task warmup = cleanup.StartNew(() => StartupPipelineWarmer.WarmupAsync(LoadWarmupChainSpec(), WarmupConfig(directory.Path), false,
+        Task warmup = StartupPipelineWarmer.WarmupAsync(LoadWarmupChainSpec(), WarmupConfig(directory.Path), false,
             cancellation.Token, configureContainer: builder =>
             {
-                builder.RegisterBuildCallback(container => container.CurrentScopeEnding += (_, _) => disposing = true);
+                builder.RegisterBuildCallback(container => container.CurrentScopeEnding += (_, _) => disposing.TrySetResult());
                 builder.RegisterType<StartupPipelineWarmer.WarmProcessingStats>().As<IProcessingStats>()
                     .WithParameter("logManager", logs)
                     .WithParameter("blocksConfig", new BlocksConfig { SlowBlockThresholdMs = 0 })
                     .InstancePerLifetimeScope();
                 builder.AddDecorator<IServiceStopper>((context, inner) => new ObservedServiceStopper(inner, context.Resolve<Func<GCKeeper>>(), stopped));
-            })).Unwrap();
+            });
         try
         {
             await reporting.Task.WaitAsync(RunnerTimeout);
             await stopped.Task.WaitAsync(RunnerTimeout);
-            // On the same serial scheduler, cleanup reaches either the report drain or disposal before this probe runs.
-            await cleanup.StartNew(() =>
+            Task disposalProbe = await Task.WhenAny(disposing.Task, warmup, Task.Delay(TimeSpan.FromMilliseconds(500), cancellation.Token));
+            using (Assert.EnterMultipleScope())
             {
-                using (Assert.EnterMultipleScope())
-                {
-                    Assert.That(warmup.IsCompleted, Is.False);
-                    Assert.That(disposing, Is.False, "reports still own their storage dependencies");
-                }
-            });
+                Assert.That(warmup.IsCompleted, Is.False);
+                Assert.That(disposalProbe, Is.Not.SameAs(disposing.Task), "reports still own their storage dependencies");
+            }
         }
         finally
         {
             release.Set();
             await warmup.WaitAsync(RunnerTimeout);
-            scheduler.Complete();
-            await scheduler.Completion.WaitAsync(RunnerTimeout);
         }
-        Assert.That(disposing, Is.True);
+        Assert.That(disposing.Task.IsCompleted, Is.True);
     }
 
     private sealed class ObservedServiceStopper(IServiceStopper inner, Func<GCKeeper> gcKeeper, TaskCompletionSource stopped) : IServiceStopper
```
