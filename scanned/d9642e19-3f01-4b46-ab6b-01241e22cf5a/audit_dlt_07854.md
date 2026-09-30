# [?] Fix potential race condition in DefaultPerformanceTracker (#4201)

## Summary
Severity: Unknown
Chain: Ethereum
Component: Consensys-Incorporated/teku
Published: 2021-08-02
Source: https://github.com/Consensys-Incorporated/teku/commit/3227675fbd4e8369b25e3f37110028ac8079f77a
Type: security-commit

## Details
Fix potential race condition in DefaultPerformanceTracker (#4201)

start is called from a different thread to onSlot so need to ensure a consistent view of nodeStartEpoch.

## Patch
### CHANGELOG.md
```diff
@@ -15,8 +15,8 @@ For information on changes in released versions of Teku, see the [releases page]
 - Docker images now include `curl` to support adding health checks.
 
 ### Bug Fixes
-- Fixed `ConcurrentModificationException` in validator performance reporting.
-- Upgraded the discovery library, providing better memory management and standards compliance. 
+- Fixed `ConcurrentModificationException` and `NoSuchElementException` in validator performance reporting.
+- Upgraded the discovery library, providing better memory management and standards compliance.
 
 ### Experimental: New Altair REST APIs
 - implement POST `/eth/v1/beacon/pool/sync_committees` to allow validators to submit sync committee signatures to the beacon node.
```

### validator/coordinator/src/main/java/tech/pegasys/teku/validator/coordinator/performance/DefaultPerformanceTracker.java
```diff
@@ -74,7 +74,7 @@ public class DefaultPerformanceTracker implements PerformanceTracker {
   private final SyncCommitteePerformanceTracker syncCommitteePerformanceTracker;
   private final Spec spec;
 
-  private Optional<UInt64> nodeStartEpoch = Optional.empty();
+  private volatile Optional<UInt64> nodeStartEpoch = Optional.empty();
   private final AtomicReference<UInt64> latestAnalyzedEpoch = new AtomicReference<>(UInt64.ZERO);
 
   public DefaultPerformanceTracker(
@@ -101,6 +101,8 @@ public void start(UInt64 nodeStartSlot) {
 
   @Override
   public void onSlot(UInt64 slot) {
+    // Ensure a consistent view as the field is volatile.
+    final Optional<UInt64> nodeStartEpoch = this.nodeStartEpoch;
     if (nodeStartEpoch.isEmpty()) {
       return;
     }
```
