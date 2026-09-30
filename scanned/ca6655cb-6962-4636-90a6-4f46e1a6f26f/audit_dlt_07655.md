# [?] Fix/initsteps race condition (#8145)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2025-02-21
Source: https://github.com/NethermindEth/nethermind/commit/bb3ca1fc1254e5b00323bf4a65ce1deaead65422
Type: security-commit

## Details
Fix/initsteps race condition (#8145)

## Patch
### src/Nethermind/Nethermind.Init/Steps/EthereumStepsManager.cs
```diff
@@ -7,6 +7,7 @@
 using System.Diagnostics;
 using System.Linq;
 using System.Runtime.ExceptionServices;
+using System.Runtime.InteropServices;
 using System.Threading;
 using System.Threading.Tasks;
 using Nethermind.Api;
@@ -19,10 +20,8 @@ public class EthereumStepsManager
     {
         private readonly ILogger _logger;
 
-        private readonly AutoResetEvent _autoResetEvent = new AutoResetEvent(true);
         private readonly INethermindApi _api;
         private readonly List<StepInfo> _allSteps;
-        private readonly Dictionary<Type, StepInfo> _allStepsByBaseType;
 
         public EthereumStepsManager(
             IEthereumStepsLoader loader,
@@ -36,153 +35,97 @@ public EthereumStepsManager(
                       ?? throw new ArgumentNullException(nameof(logManager));
 
             _allSteps = loader.LoadSteps(_api.GetType()).ToList();
-            _allStepsByBaseType = _allSteps.ToDictionary(static s => s.StepBaseType, static s => s);
-        }
-
-        private async Task ReviewDependencies(CancellationToken cancellationToken)
-        {
-            bool changedAnything;
-            do
-            {
-                foreach (StepInfo stepInfo in _allSteps)
-                {
-                    _logger.Debug($"{stepInfo} is {stepInfo.Stage}");
-                }
-
-                await _autoResetEvent.WaitOneAsync(cancellationToken);
-
-                if (_logger.IsDebug) _logger.Debug("Reviewing steps manager dependencies");
-
-                changedAnything = false;
-                foreach (StepInfo stepInfo in _allSteps)
-                {
-                    cancellationToken.ThrowIfCancellationRequested();
-
-                    if (stepInfo.Stage == StepInitializationStage.WaitingForDependencies)
-                    {
-                        bool allDependenciesFinished = true;
-                        foreach (Type dependency in stepInfo.Dependencies)
-                        {
-                            StepInfo dependencyInfo = _allStepsByBaseType[dependency];
-                            if (dependencyInfo.Stage != StepInitializationStage.Complete)
-                            {
-                                if (_logger.IsDebug) _logger.Debug($"{stepInfo} is waiting for {dependencyInfo}");
-                                allDependenciesFinished = false;
-                                break;
-                            }
-                        }
-
-                        if (allDependenciesFinished)
-                        {
-                            stepInfo.Stage = StepInitializationStage.WaitingForExecution;
-                            changedAnything = true;
-                            if (_logger.IsDebug) _logger.Debug($"{stepInfo} stage changed to {stepInfo.Stage}");
-                            _autoResetEvent.Set();
-                        }
-                    }
-                }
-            } while (changedAnything);
         }
 
         public async Task InitializeAll(CancellationToken cancellationToken)
         {
-            while (_allSteps.Any(static s => s.Stage != StepInitializationStage.Complete))
+            List<Task> allRequiredSteps = CreateAndExecuteSteps(cancellationToken);
+            if (allRequiredSteps.Count == 0)
+                return;
+            do
             {
-                cancellationToken.ThrowIfCancellationRequested();
-
-                RunOneRoundOfInitialization(cancellationToken);
-                await ReviewDependencies(cancellationToken);
-                ReviewFailedAndThrow();
-            }
-
-            await Task.WhenAll(_allPending);
+                Task current = await Task.WhenAny(allRequiredSteps);
+                ReviewFailedAndThrow(current);
+                if (current.IsCanceled && _logger.IsDebug)
+                    _logger.Debug($"A required step was cancelled!");
+                allRequiredSteps.Remove(current);
+            } while (allRequiredSteps.Any(s => !s.IsCompleted));
         }
 
-        private readonly ConcurrentQueue<Task> _allPending = new();
 
-        private void RunOneRoundOfInitialization(CancellationToken cancellationToken)
+        private List<Task> CreateAndExecuteSteps(CancellationToken cancellationToken)
         {
-            int startedThisRound = 0;
+            Dictionary<Type, List<StepWrapper>> stepBaseTypeMap = [];
+            Dictionary<Type, StepInfo> stepInfoMap = [];
+
             foreach (StepInfo stepInfo in _allSteps)
             {
                 cancellationToken.ThrowIfCancellationRequested();
 
-                if (stepInfo.Stage != StepInitializationStage.WaitingForExecution)
-                {
-                    continue;
-                }
-
                 IStep? step = CreateStepInstance(stepInfo);
                 if (step is null)
-                {
-                    if (_logger.IsError) _logger.Error($"Unable to create instance of Ethereum runner step {stepInfo}");
-                    continue;
-                }
-
-                if (_logger.IsDebug) _logger.Debug($"Executing step: {stepInfo}");
-
-                stepInfo.Stage = StepInitializationStage.Executing;
-                startedThisRound++;
-                Task task = ExecuteStep(step, stepInfo, cancellationToken);
-
-                if (step.MustInitialize)
-                {
-                    _allPending.Enqueue(task);
-                }
-                else
-                {
-                    stepInfo.Stage = StepInitializationStage.Complete;
-                }
+                    throw new StepDependencyException($"A step {stepInfo} could not be created and initialization cannot proceed.");
+                stepInfoMap.Add(step.GetType(), stepInfo);
+                ref List<StepWrapper>? list = ref CollectionsMarshal.GetValueRefOrAddDefault(stepBaseTypeMap, stepInfo.StepBaseType, out bool keyExists);
+                list ??= new List<StepWrapper>();
+                list.Add(new StepWrapper(step));
             }
-
-            if (startedThisRound == 0 && _allPending.All(static t => t.IsCompleted))
+            List<Task> allRequiredSteps = new();
+            foreach (List<StepWrapper> steps in stepBaseTypeMap.Values)
             {
-                Interlocked.Increment(ref _foreverLoop);
-                if (_foreverLoop > 100)
+                foreach (StepWrapper stepWrapper in steps)
                 {
-                    if (_logger.IsWarn) _logger.Warn($"Didn't start any initialization steps during initialization round and all previous steps are already completed.");
+                    StepInfo stepInfo = stepInfoMap[stepWrapper.Step.GetType()];
+                    Task task = ExecuteStep(stepWrapper, stepInfo, stepBaseTypeMap, cancellationToken);
+                    if (_logger.IsDebug) _logger.Debug($"Executing step: {stepInfo}");
+
+                    if (stepWrapper.Step.MustInitialize)
+                    {
+                        allRequiredSteps.Add(task);
+                    }
                 }
             }
+            return allRequiredSteps;
         }
 
-        private async Task ExecuteStep(IStep step, StepInfo stepInfo, CancellationToken cancellationToken)
+        private async Task ExecuteStep(StepWrapper stepWrapper, StepInfo stepInfo, Dictionary<Type, List<StepWrapper>> stepBaseTypeMap, CancellationToken cancellationToken)
         {
             long startTime = Stopwatch.GetTimestamp();
             try
             {
-                await step.Execute(cancellationToken);
+                List<StepWrapper> dependencies = [];
+                foreach (Type type in stepInfo.Dependencies)
+                {
+                    if (!stepBaseTypeMap.ContainsKey(type))
+                        throw new StepDependencyException($"The dependent step {type.Name} for {stepInfo.StepType.Name} was not created.");
+                    dependencies.AddRange(stepBaseTypeMap[type]);
+                }
+                await stepWrapper.StartExecute(dependencies, cancellationToken);
 
                 if (_logger.IsDebug)
                     _logger.Debug(
-                        $"Step {step.GetType().Name,-24} executed in {Stopwatch.GetElapsedTime(startTime).TotalMilliseconds:N0}ms");
-
-                stepInfo.Stage = StepInitializationStage.Complete;
+                        $"Step {stepWrapper.GetType().Name,-24} executed in {Stopwatch.GetElapsedTime(startTime).TotalMilliseconds:N0}ms");
             }
-            catch (Exception exception)
+            catch (Exception exception) when (exception is not TaskCanceledException)
             {
-                if (step.MustInitialize)
+                if (stepWrapper.Step.MustInitialize)
                 {
                     if (_logger.IsError)
                         _logger.Error(
-                            $"Step {step.GetType().Name,-24} failed after {Stopwatch.GetElapsedTime(startTime).TotalMilliseconds:N0}ms",
+                            $"Step {stepWrapper.GetType().Name,-24} failed after {Stopwatch.GetElapsedTime(startTime).TotalMilliseconds:N0}ms",
                             exception);
-
-                    stepInfo.Stage = StepInitializationStage.Failed;
                     throw;
                 }
 
                 if (_logger.IsWarn)
                 {
                     _logger.Warn(
-                        $"Step {step.GetType().Name,-24} failed after {Stopwatch.GetElapsedTime(startTime).TotalMilliseconds:N0}ms {exception}");
+                        $"Step {stepWrapper.GetType().Name,-24} failed after {Stopwatch.GetElapsedTime(startTime).TotalMilliseconds:N0}ms {exception}");
                 }
-                stepInfo.Stage = StepInitializationStage.Complete;
             }
             finally
             {
-                _autoResetEvent.Set();
-
-                if (_logger.IsDebug) _logger.Debug($"{step.GetType().Name,-24} complete");
+                if (_logger.IsDebug) _logger.Debug($"{stepWrapper.GetType().Name,-24} complete");
             }
         }
 
@@ -201,13 +144,37 @@ private async Task ExecuteStep(IStep step, StepInfo stepInfo, CancellationToken
             return step;
         }
 
-        private int _foreverLoop;
+        private void ReviewFailedAndThrow(Task task)
+        {
+            if (task?.IsFaulted == true && task?.Exception is not null)
+                ExceptionDispatchInfo.Capture(task.Exception.GetBaseException()).Throw();
+        }
 
-        private void ReviewFailedAndThrow()
+        private class StepWrapper(IStep step)
         {
-            Task? anyFaulted = _allPending.FirstOrDefault(static t => t.IsFaulted);
-            if (anyFaulted?.IsFaulted == true && anyFaulted?.Exception is not null)
-                ExceptionDispatchInfo.Capture(anyFaulted.Exception.GetBaseException()).Throw();
+            public IStep Step => step;
+            public Task StepTask => _taskCompletedSource.Task;
+
+            private TaskCompletionSource _taskCompletedSource = new TaskCompletionSource();
+
+            public async Task StartExecute(IEnumerable<StepWrapper> dependentSteps, CancellationToken cancellationToken)
+            {
+                cancellationToken.Register(() => _taskCompletedSource.TrySetCanceled());
+
+                await Task.WhenAll(dependentSteps.Select(s => s.StepTask));
+                try
+                {
+                    await step.Execute(cancellationToken);
+                    _taskCompletedSource.TrySetResult();
+                }
+                catch
+                {
+                    //TaskCompletionSource is transitioned to cancelled state to prevent a cascade effect of log statements
+                    _taskCompletedSource.TrySetCanceled();
+                    throw;
+                }
+            }
         }
     }
+
 }
```

### src/Nethermind/Nethermind.Init/Steps/StepInfo.cs
```diff
@@ -29,11 +29,9 @@ public StepInfo(Type type, Type baseType)
 
         public Type[] Dependencies { get; }
 
-        public StepInitializationStage Stage { get; set; }
-
         public override string ToString()
         {
-            return $"{StepType.Name} : {StepBaseType.Name} ({Stage})";
+            return $"{StepType.Name} : {StepBaseType.Name}";
         }
     }
 }
```

### src/Nethermind/Nethermind.Runner.Test/Ethereum/Steps/EthereumStepsManagerTests.cs
```diff
@@ -47,7 +47,6 @@ public async Task With_steps_from_here()
                 LimboLogs.Instance);
 
             using CancellationTokenSource source = new CancellationTokenSource(TimeSpan.FromSeconds(1));
-
             try
             {
                 await stepsManager.InitializeAll(source.Token);
@@ -96,8 +95,7 @@ public async Task With_failing_steps()
                 runnerContext,
                 LimboLogs.Instance);
 
-            using CancellationTokenSource source = new CancellationTokenSource(TimeSpan.FromSeconds(2));
-
+            using CancellationTokenSource source = new CancellationTokenSource(TimeSpan.FromSeconds(1));
             try
             {
                 await stepsManager.InitializeAll(source.Token);
@@ -133,7 +131,7 @@ public class StepForever : IStep
     {
         public async Task Execute(CancellationToken cancellationToken)
         {
-            await Task.Delay(100000);
+            await Task.Delay(100000, cancellationToken);
         }
 
         public StepForever(NethermindApi runnerContext)
```
