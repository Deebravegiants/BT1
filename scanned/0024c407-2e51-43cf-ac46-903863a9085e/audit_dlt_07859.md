# [?] Regenerate checkpoint state before taking out the fork choice lock to avoid deadlock (#2635)

## Summary
Severity: Unknown
Chain: Ethereum
Component: Consensys-Incorporated/teku
Published: 2020-08-21
Source: https://github.com/Consensys-Incorporated/teku/commit/81c560adff41273a78c692f7da46103974f781fc
Type: security-commit

## Details
Regenerate checkpoint state before taking out the fork choice lock to avoid deadlock (#2635)

## Patch
### ethereum/statetransition/src/main/java/tech/pegasys/teku/statetransition/forkchoice/ForkChoice.java
```diff
@@ -20,6 +20,8 @@
 import java.util.Optional;
 import java.util.concurrent.Semaphore;
 import java.util.function.Supplier;
+import org.apache.logging.log4j.LogManager;
+import org.apache.logging.log4j.Logger;
 import org.apache.tuweni.bytes.Bytes32;
 import tech.pegasys.teku.core.StateTransition;
 import tech.pegasys.teku.core.results.BlockImportResult;
@@ -37,7 +39,7 @@
 import tech.pegasys.teku.storage.store.UpdatableStore.StoreTransaction;
 
 public class ForkChoice {
-
+  private static final Logger LOG = LogManager.getLogger();
   private final Semaphore lock = new Semaphore(1);
   private final RecentChainData recentChainData;
   private final StateTransition stateTransition;
@@ -61,38 +63,47 @@ public void processHead(UInt64 nodeSlot) {
   }
 
   private void processHead(Optional<UInt64> nodeSlot) {
-    withLock(
-            () -> {
-              final Checkpoint finalizedCheckpoint =
-                  recentChainData.getStore().getFinalizedCheckpoint();
-              final Checkpoint justifiedCheckpoint =
-                  recentChainData.getStore().getJustifiedCheckpoint();
-              return recentChainData
-                  .retrieveCheckpointState(justifiedCheckpoint)
-                  .thenCompose(
-                      justifiedCheckpointState -> {
-                        final StoreTransaction transaction =
-                            recentChainData.startStoreTransaction();
-                        final ForkChoiceStrategy forkChoiceStrategy = getForkChoiceStrategy();
-                        Bytes32 headBlockRoot =
-                            forkChoiceStrategy.findHead(
-                                transaction,
-                                finalizedCheckpoint,
-                                justifiedCheckpoint,
-                                justifiedCheckpointState.orElseThrow());
-
-                        recentChainData.updateHead(
-                            headBlockRoot,
-                            nodeSlot.orElse(
-                                forkChoiceStrategy
-                                    .blockSlot(headBlockRoot)
-                                    .orElseThrow(
-                                        () ->
-                                            new IllegalStateException(
-                                                "Unable to retrieve the slot of fork choice head"))));
-                        return transaction.commit();
-                      });
-            })
+    final Checkpoint retrievedJustifiedCheckpoint =
+        recentChainData.getStore().getJustifiedCheckpoint();
+    recentChainData
+        .retrieveCheckpointState(retrievedJustifiedCheckpoint)
+        .thenCompose(
+            justifiedCheckpointState ->
+                withLock(
+                    () -> {
+                      final Checkpoint finalizedCheckpoint =
+                          recentChainData.getStore().getFinalizedCheckpoint();
+                      final Checkpoint justifiedCheckpoint =
+                          recentChainData.getStore().getJustifiedCheckpoint();
+                      if (!justifiedCheckpoint.equals(retrievedJustifiedCheckpoint)) {
+                        LOG.info(
+                            "Skipping head block update as justified checkpoint was updated while loading checkpoint state. Was {} ({}) but now {} ({})",
+                            retrievedJustifiedCheckpoint.getEpoch(),
+                            retrievedJustifiedCheckpoint.getRoot(),
+                            justifiedCheckpoint.getEpoch(),
+                            justifiedCheckpoint.getRoot());
+                      }
+                      final StoreTransaction transaction = recentChainData.startStoreTransaction();
+                      final ForkChoiceStrategy forkChoiceStrategy = getForkChoiceStrategy();
+                      Bytes32 headBlockRoot =
+                          forkChoiceStrategy.findHead(
+                              transaction,
+                              finalizedCheckpoint,
+                              justifiedCheckpoint,
+                              justifiedCheckpointState.orElseThrow());
+
+                      recentChainData.updateHead(
+                          headBlockRoot,
+                          nodeSlot.orElse(
+                              forkChoiceStrategy
+                                  .blockSlot(headBlockRoot)
+                                  .orElseThrow(
+                                      () ->
+                                          new IllegalStateException(
+                                              "Unable to retrieve the slot of fork choice head: "
+                                                  + headBlockRoot))));
+                      return transaction.commit();
+                    }))
         .join();
   }
 
```
