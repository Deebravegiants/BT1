# [?] fix(flat-history): prevent history walk ETA overflow from killing progress and discarding the walk (#13761)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-09-24
Source: https://github.com/NethermindEth/nethermind/commit/f85c66af0076e58b07862c5661ed25163b7e81d3
Type: security-commit

## Details
fix(flat-history): prevent history walk ETA overflow from killing progress and discarding the walk (#13761)

* fix(flat-history): prevent history walk ETA overflow from killing progress and discarding the walk

WalkProgress.Report computed elapsed * (total - done) / doneThisRun, so the
TimeSpan multiply ran first and threw OverflowException about 69 h into a
mainnet walk. That fault killed the heartbeat silently, and Dispose rethrew
it after the walk had finished, replacing the walk verdict.

Compute the ETA ratio first in a shared Eta helper that reports "n/a" beyond
the TimeSpan range, log and continue on a failed heartbeat report, and never
let Dispose rethrow a reporter fault.

Fixes #13760

* docs(flat-history): move Eta overflow note into XML remarks

## Patch
### src/Nethermind/Nethermind.State.Flat.History.Test/WalkProgressTests.cs
```diff
@@ -0,0 +1,33 @@
+// SPDX-FileCopyrightText: 2026 Demerzel Solutions Limited
+// SPDX-License-Identifier: LGPL-3.0-only
+
+using System;
+using Nethermind.State.Flat.History.Walk;
+using NUnit.Framework;
+
+namespace Nethermind.State.Flat.History.Test;
+
+[TestFixture]
+public class WalkProgressTests
+{
+    [Test]
+    public void Eta_LongMainnetWalk_DoesNotOverflow()
+    {
+        // 512 items x 10,000 units at 27% done after 69 h: elapsed ticks * remaining exceeds long.MaxValue (#13760).
+        const long total = 512L * 10_000;
+        const long done = total * 27 / 100;
+        TimeSpan elapsed = TimeSpan.FromHours(69);
+        Assert.That(() => elapsed * (total - done), Throws.TypeOf<OverflowException>(), "the old multiply-first order overflows here");
+
+        Assert.That(WalkProgress.Eta(elapsed, total - done, done), Is.EqualTo("7d 18h"));
+    }
+
+    [Test]
+    public void Eta_BeyondTimeSpanRange_IsUnknown() =>
+        Assert.That(WalkProgress.Eta(TimeSpan.FromDays(365), long.MaxValue, 1), Is.EqualTo("n/a"));
+
+    [TestCase(0)]
+    [TestCase(-1)]
+    public void Eta_WithoutProgressThisRun_IsUnknown(double doneThisRun) =>
+        Assert.That(WalkProgress.Eta(TimeSpan.FromHours(1), 100, doneThisRun), Is.EqualTo("n/a"));
+}
```

### src/Nethermind/Nethermind.State.Flat.History/Walk/WalkProgress.cs
```diff
@@ -46,7 +46,15 @@ public void Start()
                 while (!_stop.IsCancellationRequested)
                 {
                     await Task.Delay(Heartbeat, _stop.Token);
-                    logger.Info(Report());
+                    try
+                    {
+                        logger.Info(Report());
+                    }
+                    catch (Exception e) when (e is not OperationCanceledException)
+                    {
+                        // A progress line must never end the heartbeat, let alone the walk.
+                        if (logger.IsWarn) logger.Warn($"History walk progress report failed: {e}");
+                    }
                 }
             }
             catch (OperationCanceledException)
@@ -118,7 +126,7 @@ public void Folding(ulong block)
         double seconds = Stopwatch.GetElapsedTime(_foldLastReportAt, now).TotalSeconds;
         double blocksPerSecond = seconds > 0 ? (block - _foldLastBlock) / seconds : 0;
         ulong doneThisRun = block - _foldStartBlock;
-        string eta = doneThisRun == 0 ? "n/a" : Format(Stopwatch.GetElapsedTime(_foldStartedAt) * ((double)(to - block) / doneThisRun));
+        string eta = Eta(Stopwatch.GetElapsedTime(_foldStartedAt), to - block, doneThisRun);
         _foldLastReportAt = now;
         _foldLastBlock = block;
 
@@ -155,13 +163,24 @@ private string Report()
 
         TimeSpan elapsed = Stopwatch.GetElapsedTime(_startedAt);
         long doneThisRun = done - _startingUnits;
-        string eta = doneThisRun <= 0 ? "n/a" : Format(elapsed * (total - done) / doneThisRun);
+        string eta = Eta(elapsed, total - done, doneThisRun);
 
         return $"{"History walk",ProgressLogger.PrefixAlignment}{Volatile.Read(ref _completed),ProgressLogger.BlockPaddingLength:N0} / {items,ProgressLogger.BlockPaddingLength:N0} ({fraction.ToString("P2", CultureInfo.InvariantCulture),8}) {Progress.GetMeter(fraction, 1)}| {stepsPerSecond,ProgressLogger.SpeedPaddingLength:N0} subtree steps/s (~{blocksPerSecond:N0} per subtree) | ETA {eta} | {GC.GetTotalMemory(false) >> 20:N0} MB managed{inFlight}";
     }
 
     private static string Name(int item) => item < HistoryWalkRun.AccountPartitions ? $"accounts 0x{item:x2}" : $"storage 0x{item - HistoryWalkRun.AccountPartitions:x2}";
 
+    /// <remarks>
+    /// Divides before multiplying and works in double ticks: <c>elapsed * remaining</c> overflows <see cref="TimeSpan"/> days into a long walk.
+    /// </remarks>
+    internal static string Eta(TimeSpan elapsed, double remaining, double doneThisRun)
+    {
+        if (doneThisRun <= 0) return "n/a";
+
+        double ticks = elapsed.Ticks * (remaining / doneThisRun);
+        return ticks < TimeSpan.MaxValue.Ticks ? Format(TimeSpan.FromTicks((long)ticks)) : "n/a";
+    }
+
     private static string Format(TimeSpan span) => span.TotalDays >= 1 ? $"{(int)span.TotalDays}d {span.Hours:D2}h" : $"{(int)span.TotalHours}h {span.Minutes:D2}m";
 
     public void Dispose()
@@ -174,6 +193,11 @@ public void Dispose()
         catch (OperationCanceledException)
         {
         }
+        catch (Exception e)
+        {
+            // Disposal follows the walk's verdict; a reporter fault must not replace it.
+            if (logger.IsWarn) logger.Warn($"History walk progress reporter failed: {e}");
+        }
 
         _stop.Dispose();
     }
```
