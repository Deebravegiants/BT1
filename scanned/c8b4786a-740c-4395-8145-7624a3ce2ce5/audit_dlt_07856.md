# [?] Fix SyncDataProvider to avoid an underflow error when the sync target is actually a lower slot than our current head. (#3479)

## Summary
Severity: Unknown
Chain: Ethereum
Component: Consensys-Incorporated/teku
Published: 2021-01-22
Source: https://github.com/Consensys-Incorporated/teku/commit/3458dba6864cc070b41f84525139c5fb2f90867e
Type: security-commit

## Details
Fix SyncDataProvider to avoid an underflow error when the sync target is actually a lower slot than our current head. (#3479)

## Patch
### data/provider/src/main/java/tech/pegasys/teku/api/SyncDataProvider.java
```diff
@@ -46,7 +46,7 @@ public boolean isSyncing() {
   private UInt64 getSlotsBehind(final tech.pegasys.teku.sync.events.SyncingStatus syncingStatus) {
     if (syncingStatus.isSyncing() && syncingStatus.getHighestSlot().isPresent()) {
       final UInt64 highestSlot = syncingStatus.getHighestSlot().get();
-      return highestSlot.minus(syncingStatus.getCurrentSlot());
+      return highestSlot.minusMinZero(syncingStatus.getCurrentSlot());
     }
     return UInt64.ZERO;
   }
```
