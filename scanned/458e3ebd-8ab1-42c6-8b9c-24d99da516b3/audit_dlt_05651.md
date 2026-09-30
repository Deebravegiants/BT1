# [?] Fix data race in SyncDurationMetrics timers map (#10277)

## Summary
Severity: Unknown
Chain: Ethereum
Component: hyperledger/besu
Published: 2026-04-24
Source: https://github.com/besu-eth/besu/commit/412dc182ff386ec822d8a012fd3f40bafe731d8e
Type: security-commit

## Details
Fix data race in SyncDurationMetrics timers map (#10277)

* Fix data race in SyncDurationMetrics timers map

Switch the backing map to ConcurrentHashMap; the API surface used
(computeIfAbsent, remove) is unchanged and both operations are atomic.
Metrics-only change, no behavioural impact on sync.

Signed-off-by: Alejandro <26930485+alejandroGM0@users.noreply.github.com>

* Update CHANGELOG.md

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>
Signed-off-by: Alejandro <26930485+alejandroGM0@users.noreply.github.com>

---------

Signed-off-by: Alejandro <26930485+alejandroGM0@users.noreply.github.com>
Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>
Co-authored-by: Sally MacFarlane <macfarla.github@gmail.com>

## Patch
### CHANGELOG.md
```diff
@@ -18,6 +18,7 @@
 - BFT option `xemptyblockperiodseconds` has been taken out of experimental and been renamed `emptyblockperiodseconds`. The old config option is deprecated and will be removed in a future release.
 
 ### Bug fixes
+- Fix data race in `SyncDurationMetrics` where the backing `HashMap` was mutated from multiple sync threads in parallel, causing missing or zero `sync_duration` samples. [#10277](https://github.com/besu-eth/besu/pull/10277)
 
 ### Additions and Improvements
 - The option to set a different block period for empty BFT blocks (`emptyblockperiodseconds`) is no longer experimental. The experimental flag `xemptyblockperiodseconds` will be removed in a future release.
```

### metrics/core/src/main/java/org/hyperledger/besu/metrics/SyncDurationMetrics.java
```diff
@@ -19,7 +19,8 @@
 import org.hyperledger.besu.plugin.services.metrics.LabelledMetric;
 import org.hyperledger.besu.plugin.services.metrics.OperationTimer;
 
-import java.util.HashMap;
+import java.util.Map;
+import java.util.concurrent.ConcurrentHashMap;
 
 /**
  * This class manages the synchronization duration metrics for the Hyperledger Besu project. It
@@ -33,7 +34,7 @@ public class SyncDurationMetrics {
 
   private final LabelledMetric<OperationTimer> timer;
 
-  private final HashMap<String, OperationTimer.TimingContext> timers = new HashMap<>();
+  private final Map<String, OperationTimer.TimingContext> timers = new ConcurrentHashMap<>();
 
   /**
    * Creates a new {@link SyncDurationMetrics} instance.
```
