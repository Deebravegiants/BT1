# [?] Fix flaky RetryCache overflow allocation test counting background GC noise (#13745)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-09-24
Source: https://github.com/NethermindEth/nethermind/commit/69099f49fbab8e97c87b85b5e418b51552f917c7
Type: security-commit

## Details
Fix flaky RetryCache overflow allocation test counting background GC noise (#13745)

Stop RetryCache overflow allocation test counting background GC noise

OverflowStorage_ReusesBoundedCapacityAcrossRepeatedBursts measured each
burst with GC.GetAllocatedBytesForCurrentThread. A background GC that
pauses the test thread can add up to one 8 KB allocation buffer to that
counter while the thread allocates nothing, so a burst read 4088 to
8248 bytes against the 4000-byte bound.

A window with a GC pause is now checked only against a bound that
rules out set regrowth, and another burst replaces it, so three
pause-free windows are still held to the 4000-byte bound.

## Patch
### src/Nethermind/Nethermind.TxPool.Test/RetryCacheTests.cs
```diff
@@ -1679,14 +1679,24 @@ public async Task OverflowStorage_ReusesBoundedCapacityAcrossRepeatedBursts(
         Assert.That(AnnounceBurst(), Is.EqualTo(resourceCount));
         Assert.That(AnnounceBurst(), Is.Zero);
 
-        for (int burst = 0; burst < 4; burst++)
+        bool measuresAllocation = resourceCount < 32768;
+        int bursts = 4;
+        int measuredBursts = 0;
+        for (int burst = 0; burst < bursts; burst++)
         {
             timeProvider.Advance(TimeSpan.FromMilliseconds(CacheTimeoutMs * 2));
+            TimeSpan pausedBefore = GC.GetTotalPauseDuration();
             long before = GC.GetAllocatedBytesForCurrentThread();
             cache.ProcessRetryTick();
             int retainedAfterExpiry = cache.OverflowRetainedCapacity;
             int requested = AnnounceBurst();
             long allocated = GC.GetAllocatedBytesForCurrentThread() - before;
+            // A background GC pausing this thread can add up to one 8 KB allocation buffer to its counter without any
+            // allocation, so a paused window only rules out regrowth and another burst takes its place.
+            bool paused = GC.GetTotalPauseDuration() != pausedBefore;
+            bool measured = measuresAllocation && burst > 0 && !paused;
+            if (measured) measuredBursts++;
+            else if (measuresAllocation && burst > 0 && bursts < 16) bursts++;
 
             using (Assert.EnterMultipleScope())
             {
@@ -1695,11 +1705,14 @@ public async Task OverflowStorage_ReusesBoundedCapacityAcrossRepeatedBursts(
                 if (resourceCount == 32768)
                     Assert.That(retainedAfterExpiry, Is.LessThanOrEqualTo(1024), "repeated oversized bursts must not bypass the retention cap");
                 else if (burst > 0)
-                    Assert.That(allocated, Is.LessThan(4_000), "repeated bursts should reuse the grown set after the warm spare proves useful");
+                    Assert.That(allocated, Is.LessThan(paused ? 16_000 : 4_000), "repeated bursts should reuse the grown set after the warm spare proves useful");
             }
             Assert.That(AnnounceBurst(), Is.Zero);
         }
 
+        if (measuresAllocation)
+            Assert.That(measuredBursts, Is.EqualTo(3), "GC pauses interrupted too many allocation measurements");
+
         timeProvider.Advance(TimeSpan.FromMilliseconds(CacheTimeoutMs * idlePeriods));
         cache.ProcessRetryTick();
         Assert.That(cache.OverflowRequestsInUse, Is.Zero);
```
