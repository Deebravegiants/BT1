# [?] fix(kute): prevent null label crash in Prometheus metrics reporter (#10109)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-01-06
Source: https://github.com/NethermindEth/nethermind/commit/49ee006d16c112242381b35940d8fb5c031048da
Type: security-commit

## Details
fix(kute): prevent null label crash in Prometheus metrics reporter (#10109)

## Patch
### tools/Kute/Nethermind.Tools.Kute/Metrics/PrometheusPushGatewayMetricsReporter.cs
```diff
@@ -97,17 +97,23 @@ public Task Ignored(CancellationToken token = default)
 
     public Task Batch(JsonRpc.Request.Batch batch, TimeSpan elapsed, CancellationToken token = default)
     {
-        _batchDuration
-            .WithLabels(batch.Id)
-            .Observe(elapsed.TotalSeconds);
+        if (batch.Id is not null)
+        {
+            _batchDuration
+                .WithLabels(batch.Id)
+                .Observe(elapsed.TotalSeconds);
+        }
         return Task.CompletedTask;
     }
 
     public Task Single(JsonRpc.Request.Single single, TimeSpan elapsed, CancellationToken token = default)
     {
-        _singleDuration
-            .WithLabels(single.Id, single.MethodName)
-            .Observe(elapsed.TotalSeconds);
+        if (single.Id is not null && single.MethodName is not null)
+        {
+            _singleDuration
+                .WithLabels(single.Id, single.MethodName)
+                .Observe(elapsed.TotalSeconds);
+        }
         return Task.CompletedTask;
     }
 
```
