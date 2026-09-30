# [?] Fix potential overflow error when pruning blobs (#7432)

## Summary
Severity: Unknown
Chain: Ethereum
Component: Consensys-Incorporated/teku
Published: 2023-08-18
Source: https://github.com/Consensys-Incorporated/teku/commit/c15379aa2c75cc9bc179afb3e6ebc5c29ad31ae2
Type: security-commit

## Details
Fix potential overflow error when pruning blobs (#7432)

## Patch
### storage/src/main/java/tech/pegasys/teku/storage/server/pruner/BlobSidecarPruner.java
```diff
@@ -181,9 +181,10 @@ private UInt64 getLatestPrunableSlot(final UInt64 currentSlot) {
 
     final SpecConfig config = spec.atSlot(currentSlot).getConfig();
     final SpecConfigDeneb specConfigDeneb = SpecConfigDeneb.required(config);
-    return currentSlot.minusMinZero(
-        ((long) (specConfigDeneb.getEpochsStoreBlobs() + 1)
+    final long slotsToKeep =
+        (((long) specConfigDeneb.getEpochsStoreBlobs() + 1)
                 * spec.atSlot(currentSlot).getSlotsPerEpoch())
-            + 1);
+            + 1;
+    return currentSlot.minusMinZero(slotsToKeep);
   }
 }
```
