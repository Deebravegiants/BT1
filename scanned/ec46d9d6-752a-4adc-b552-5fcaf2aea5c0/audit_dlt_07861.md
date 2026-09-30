# [?] Fix underflow in on_tick between genesis state becoming known and the chain actually starting. (#2568)

## Summary
Severity: Unknown
Chain: Ethereum
Component: Consensys-Incorporated/teku
Published: 2020-08-14
Source: https://github.com/Consensys-Incorporated/teku/commit/db84fe399f2e7a8ae16cb2a4a7122be2f9ecf6a6
Type: security-commit

## Details
Fix underflow in on_tick between genesis state becoming known and the chain actually starting. (#2568)

## Patch
### ethereum/core/src/main/java/tech/pegasys/teku/core/ForkChoiceUtil.java
```diff
@@ -169,6 +169,9 @@ private static boolean should_update_justified_checkpoint(
    *     <a>https://github.com/ethereum/eth2.0-specs/blob/v0.8.1/specs/core/0_fork-choice.md#on_tick</a>
    */
   public static void on_tick(MutableStore store, UInt64 time) {
+    if (store.getGenesisTime().isGreaterThan(time)) {
+      return;
+    }
     UInt64 previous_slot = get_current_slot(store);
 
     // Update store time
```

### ethereum/core/src/test/java/tech/pegasys/teku/core/ForkChoiceUtilTest.java
```diff
@@ -14,6 +14,11 @@
 package tech.pegasys.teku.core;
 
 import static org.assertj.core.api.Assertions.assertThat;
+import static org.mockito.ArgumentMatchers.any;
+import static org.mockito.Mockito.mock;
+import static org.mockito.Mockito.never;
+import static org.mockito.Mockito.verify;
+import static org.mockito.Mockito.when;
 import static tech.pegasys.teku.util.config.Constants.SECONDS_PER_SLOT;
 
 import java.util.List;
@@ -27,6 +32,7 @@
 import tech.pegasys.teku.bls.BLSKeyPair;
 import tech.pegasys.teku.datastructures.blocks.SignedBeaconBlock;
 import tech.pegasys.teku.datastructures.blocks.SignedBlockAndState;
+import tech.pegasys.teku.datastructures.forkchoice.MutableStore;
 import tech.pegasys.teku.datastructures.forkchoice.ReadOnlyStore;
 import tech.pegasys.teku.datastructures.forkchoice.TestStoreFactory;
 import tech.pegasys.teku.infrastructure.unsigned.UInt64;
@@ -45,7 +51,7 @@ class ForkChoiceUtilTest {
       ProtoArrayForkChoiceStrategy.initialize(store, new StubProtoArrayStorageChannel()).join();
 
   @Test
-  void getAncestors_shouldGetSimpleSequenceOfAncestors() throws Exception {
+  void getAncestors_shouldGetSimpleSequenceOfAncestors() {
     chainBuilder.generateBlocksUpToSlot(10).forEach(this::addBlock);
 
     final NavigableMap<UInt64, Bytes32> rootsBySlot =
@@ -60,7 +66,7 @@ void getAncestors_shouldGetSimpleSequenceOfAncestors() throws Exception {
   }
 
   @Test
-  void getAncestors_shouldGetSequenceOfRootsWhenSkipping() throws Exception {
+  void getAncestors_shouldGetSequenceOfRootsWhenSkipping() {
     chainBuilder.generateBlocksUpToSlot(10).forEach(this::addBlock);
 
     final NavigableMap<UInt64, Bytes32> rootsBySlot =
@@ -75,8 +81,7 @@ void getAncestors_shouldGetSequenceOfRootsWhenSkipping() throws Exception {
   }
 
   @Test
-  void getAncestors_shouldGetSequenceOfRootsWhenStartIsPriorToFinalizedCheckpoint()
-      throws Exception {
+  void getAncestors_shouldGetSequenceOfRootsWhenStartIsPriorToFinalizedCheckpoint() {
     chainBuilder.generateBlocksUpToSlot(10).forEach(this::addBlock);
     forkChoiceStrategy.setPruneThreshold(0);
     forkChoiceStrategy.maybePrune(chainBuilder.getBlockAtSlot(4).getRoot());
@@ -93,7 +98,7 @@ void getAncestors_shouldGetSequenceOfRootsWhenStartIsPriorToFinalizedCheckpoint(
   }
 
   @Test
-  void getAncestors_shouldGetSequenceOfRootsWhenEndIsAfterChainHead() throws Exception {
+  void getAncestors_shouldGetSequenceOfRootsWhenEndIsAfterChainHead() {
     chainBuilder.generateBlocksUpToSlot(10).forEach(this::addBlock);
 
     final NavigableMap<UInt64, Bytes32> rootsBySlot =
@@ -108,7 +113,7 @@ void getAncestors_shouldGetSequenceOfRootsWhenEndIsAfterChainHead() throws Excep
   }
 
   @Test
-  void getAncestors_shouldNotIncludeEntryForEmptySlots() throws Exception {
+  void getAncestors_shouldNotIncludeEntryForEmptySlots() {
     addBlock(chainBuilder.generateBlockAtSlot(3));
     addBlock(chainBuilder.generateBlockAtSlot(5));
 
@@ -144,6 +149,16 @@ public void getSlotStartTime_shouldGetCorrectTimePastGenesis() {
         .isEqualTo(SLOT_50);
   }
 
+  @Test
+  void on_tick_shouldExitImmediatelyWhenCurrentTimeIsBeforeGenesisTime() {
+    final MutableStore store = mock(MutableStore.class);
+    when(store.getGenesisTime()).thenReturn(UInt64.valueOf(3000));
+    when(store.getTime()).thenReturn(UInt64.ZERO);
+    ForkChoiceUtil.on_tick(store, UInt64.valueOf(2000));
+
+    verify(store, never()).setTime(any());
+  }
+
   private Map<UInt64, Bytes32> getRootsForBlocks(final int... blockNumbers) {
     return IntStream.of(blockNumbers)
         .mapToObj(chainBuilder::getBlockAtSlot)
```
