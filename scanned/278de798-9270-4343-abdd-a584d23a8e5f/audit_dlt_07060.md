# [?] fix(core): stop ElapsedMicroseconds overflowing on long-running stopwatches (#13416)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-09-14
Source: https://github.com/NethermindEth/nethermind/commit/0e24eefc17d29d2fe6bf1dc3053bb179ea5311ce
Type: security-commit

## Details
fix(core): stop ElapsedMicroseconds overflowing on long-running stopwatches (#13416)

* fix(core): stop ElapsedMicroseconds overflowing on long-running stopwatches

ticks * 1_000_000 overflowed long once elapsed ticks exceeded ~9.22e12,
which is ~2h33m on Linux's 1GHz Stopwatch.Frequency, turning slot timing
figures negative on long-running processes. Split the conversion into a
whole-second part and a sub-second remainder so neither multiplication
can overflow for realistic Stopwatch frequencies.

* fix(core): clarify ToMicroseconds overflow-safety doc and add summary

The remarks tied exactness of the truncating split to the 1MHz frequency
bound, but the split is exact for any positive frequency; the 1MHz bound
only governs overflow-safety at the extreme end of the tick range. Also
adds the missing <summary> per AGENTS.md doc guidance.

---------

Co-authored-by: Mattéo Pecher <matteo.pecher@grenoble-inp.org>

## Patch
### src/Nethermind/Nethermind.Core.Test/StopwatchExtensionsTests.cs
```diff
@@ -0,0 +1,39 @@
+// SPDX-FileCopyrightText: 2026 Demerzel Solutions Limited
+// SPDX-License-Identifier: LGPL-3.0-only
+
+using System.Diagnostics;
+using System.Threading;
+using Nethermind.Core.Extensions;
+using NUnit.Framework;
+
+namespace Nethermind.Core.Test;
+
+[TestFixture]
+public class StopwatchExtensionsTests
+{
+    // On Linux, Stopwatch.Frequency is 1_000_000_000 (nanosecond ticks), so `ticks * 1_000_000`
+    // overflows long once ticks exceeds ~9.22e12 (~2h33m of elapsed time).
+    [TestCase(10_000_000_000_000L, 1_000_000_000L, 10_000_000_000L)] // ~2h46m of 1GHz ticks: overflows the naive `ticks * 1_000_000` formula
+    [TestCase(long.MaxValue, 1_000_000_000L, 9_223_372_036_854_775L)] // largest possible tick count: the naive formula wraps clean through zero here
+    [TestCase(123_456_789L, 10_000_000L, 12_345_678L)] // Windows-style 10MHz QPC frequency, non-multiple ticks
+    [TestCase(1_500L, 1_000_000_000L, 1L)] // sub-microsecond precision truncates rather than rounds
+    [TestCase(0L, 1_000_000_000L, 0L)] // zero elapsed ticks
+    public void ToMicroseconds_computes_elapsed_microseconds_without_overflow(long ticks, long frequency, long expected) =>
+        Assert.That(StopwatchExtensions.ToMicroseconds(ticks, frequency), Is.EqualTo(expected));
+
+    [Test]
+    public void ElapsedMicroseconds_matches_stopwatch_elapsed()
+    {
+        Stopwatch stopwatch = Stopwatch.StartNew();
+        Thread.Sleep(5);
+        stopwatch.Stop();
+
+        long microseconds = stopwatch.ElapsedMicroseconds();
+
+        using (Assert.EnterMultipleScope())
+        {
+            Assert.That(microseconds, Is.GreaterThanOrEqualTo(0));
+            Assert.That((double)microseconds, Is.EqualTo(stopwatch.Elapsed.TotalMicroseconds).Within(1));
+        }
+    }
+}
```

### src/Nethermind/Nethermind.Core/Extensions/StopwatchExtensions.cs
```diff
@@ -7,6 +7,19 @@ namespace Nethermind.Core.Extensions
 {
     public static class StopwatchExtensions
     {
-        public static long ElapsedMicroseconds(this Stopwatch stopwatch) => stopwatch.ElapsedTicks * 1000000 / Stopwatch.Frequency;
+        public static long ElapsedMicroseconds(this Stopwatch stopwatch) => ToMicroseconds(stopwatch.ElapsedTicks, Stopwatch.Frequency);
+
+        /// <summary>Converts a raw <see cref="Stopwatch"/> tick count to whole microseconds, truncating any remainder.</summary>
+        /// <remarks>
+        /// Splitting <paramref name="ticks"/> into a whole-second part and a sub-second remainder keeps
+        /// every intermediate value within <see langword="long"/> range, unlike
+        /// <c>ticks * 1000000 / frequency</c>, which overflows once <paramref name="ticks"/> exceeds
+        /// roughly <see langword="long"/>.MaxValue / 1000000 (about 2h33m at the 1GHz
+        /// <see cref="Stopwatch.Frequency"/> on Linux). The split stays overflow-free for any
+        /// <paramref name="ticks"/> up to <see langword="long"/>.MaxValue provided
+        /// <paramref name="frequency"/> is at least 1MHz; the truncating division itself is exact
+        /// for any positive <paramref name="frequency"/>.
+        /// </remarks>
+        internal static long ToMicroseconds(long ticks, long frequency) => ticks / frequency * 1000000 + ticks % frequency * 1000000 / frequency;
     }
 }
```
