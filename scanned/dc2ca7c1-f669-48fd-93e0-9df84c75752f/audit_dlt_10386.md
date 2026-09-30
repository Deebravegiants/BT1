# [?] Fix fork choice race condition (#1707)

## Summary
Severity: Unknown
Chain: Ethereum
Component: Consensys-Incorporated/teku
Published: 2020-05-01
Source: https://github.com/Consensys-Incorporated/teku/commit/dffc13fdf2a5176b8a1e48fc7b32dba307459ebb
Type: security-commit

## Details
Fix fork choice race condition (#1707)

## Patch
### ethereum/core/src/main/java/tech/pegasys/artemis/core/ForkChoiceUtil.java
```diff
@@ -149,10 +149,7 @@ && compute_slots_since_epoch_start(current_slot).equals(UnsignedLong.ZERO))) {
    */
   @CheckReturnValue
   public static BlockImportResult on_block(
-      final MutableStore store,
-      final SignedBeaconBlock signed_block,
-      final StateTransition st,
-      final ForkChoiceStrategy forkChoiceStrategy) {
+      final MutableStore store, final SignedBeaconBlock signed_block, final StateTransition st) {
     final BeaconBlock block = signed_block.getMessage();
     final BeaconState preState = store.getBlockState(block.getParent_root());
 
@@ -229,8 +226,6 @@ public static BlockImportResult on_block(
       }
     }
 
-    forkChoiceStrategy.onBlock(store, block);
-
     final BlockProcessingRecord record = new BlockProcessingRecord(preState, signed_block, state);
     return BlockImportResult.successful(record);
   }
```

### ethereum/statetransition/src/main/java/tech/pegasys/artemis/statetransition/blockimport/BlockImporter.java
```diff
@@ -25,7 +25,6 @@
 import tech.pegasys.artemis.statetransition.events.block.ImportedBlockEvent;
 import tech.pegasys.artemis.statetransition.events.block.ProposedBlockEvent;
 import tech.pegasys.artemis.statetransition.forkchoice.ForkChoice;
-import tech.pegasys.artemis.storage.Store;
 import tech.pegasys.artemis.storage.client.RecentChainData;
 import tech.pegasys.artemis.util.async.SafeFuture;
 
@@ -53,8 +52,8 @@ public BlockImportResult importBlock(SignedBeaconBlock block) {
             block.getMessage().hash_tree_root());
         return BlockImportResult.knownBlock(block);
       }
-      Store.Transaction transaction = recentChainData.startStoreTransaction();
-      final BlockImportResult result = forkChoice.onBlock(transaction, block);
+
+      BlockImportResult result = forkChoice.onBlock(block);
       if (!result.isSuccessful()) {
         LOG.trace(
             "Failed to import block for reason {}: {}",
@@ -65,7 +64,6 @@ public BlockImportResult importBlock(SignedBeaconBlock block) {
       LOG.trace("Successfully imported block {}", block.getMessage().hash_tree_root());
 
       final Optional<BlockProcessingRecord> record = result.getBlockProcessingRecord();
-      transaction.commit().join();
       eventBus.post(new ImportedBlockEvent(block));
       record.ifPresent(eventBus::post);
 
```

### ethereum/statetransition/src/main/java/tech/pegasys/artemis/statetransition/forkchoice/ForkChoice.java
```diff
@@ -57,8 +57,17 @@ public Bytes32 processHead() {
     return headBlockRoot;
   }
 
-  public BlockImportResult onBlock(final MutableStore store, final SignedBeaconBlock block) {
-    return on_block(store, block, stateTransition, protoArrayForkChoiceStrategy);
+  public BlockImportResult onBlock(final SignedBeaconBlock block) {
+    Store.Transaction transaction = recentChainData.startStoreTransaction();
+    final BlockImportResult result = on_block(transaction, block, stateTransition);
+
+    if (!result.isSuccessful()) {
+      return result;
+    }
+
+    transaction.commit().join();
+    protoArrayForkChoiceStrategy.onBlock(recentChainData.getStore(), block.getMessage());
+    return result;
   }
 
   public AttestationProcessingResult onAttestation(
```

### ethereum/statetransition/src/testFixtures/java/tech/pegasys/artemis/statetransition/BeaconChainUtil.java
```diff
@@ -35,7 +35,6 @@
 import tech.pegasys.artemis.datastructures.operations.Attestation;
 import tech.pegasys.artemis.datastructures.state.BeaconState;
 import tech.pegasys.artemis.datastructures.util.MockStartValidatorKeyPairFactory;
-import tech.pegasys.artemis.protoarray.StubForkChoiceStrategy;
 import tech.pegasys.artemis.ssz.SSZTypes.SSZList;
 import tech.pegasys.artemis.statetransition.util.StartupUtil;
 import tech.pegasys.artemis.storage.Store.Transaction;
@@ -138,7 +137,7 @@ public SignedBeaconBlock createAndImportBlockAtSlot(
     setSlot(slot);
     final Transaction transaction = recentChainData.startStoreTransaction();
     final BlockImportResult importResult =
-        ForkChoiceUtil.on_block(transaction, block, stateTransition, new StubForkChoiceStrategy());
+        ForkChoiceUtil.on_block(transaction, block, stateTransition);
     if (!importResult.isSuccessful()) {
       throw new IllegalStateException(
           "Produced an invalid block ( reason "
```
