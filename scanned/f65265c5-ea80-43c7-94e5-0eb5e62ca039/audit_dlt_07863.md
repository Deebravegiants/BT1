# [?] Fix Attestation Invalid Signature Bug (#2305)

## Summary
Severity: Unknown
Chain: Ethereum
Component: Consensys-Incorporated/teku
Published: 2020-07-02
Source: https://github.com/Consensys-Incorporated/teku/commit/6d117919c19c2440aaf8a6a0b87390447ad1303d
Type: security-commit

## Details
Fix Attestation Invalid Signature Bug (#2305)

Ensure that a reorg event is fired when fork choice switches chain head from an empty slot to one with a block at the same slot.

## Patch
### ethereum/statetransition/src/main/java/tech/pegasys/teku/statetransition/forkchoice/ForkChoice.java
```diff
@@ -16,6 +16,8 @@
 import static tech.pegasys.teku.core.ForkChoiceUtil.on_attestation;
 import static tech.pegasys.teku.core.ForkChoiceUtil.on_block;
 
+import com.google.common.primitives.UnsignedLong;
+import java.util.Optional;
 import org.apache.tuweni.bytes.Bytes32;
 import tech.pegasys.teku.core.StateTransition;
 import tech.pegasys.teku.core.results.BlockImportResult;
@@ -44,17 +46,27 @@ private void initializeProtoArrayForkChoice() {
   }
 
   public synchronized Bytes32 processHead() {
+    return processHead(Optional.empty());
+  }
+
+  public synchronized Bytes32 processHead(UnsignedLong nodeSlot) {
+    return processHead(Optional.of(nodeSlot));
+  }
+
+  public synchronized Bytes32 processHead(Optional<UnsignedLong> nodeSlot) {
     StoreTransaction transaction = recentChainData.startStoreTransaction();
     final ForkChoiceStrategy forkChoiceStrategy = getForkChoiceStrategy();
     Bytes32 headBlockRoot = forkChoiceStrategy.findHead(transaction);
     transaction.commit(() -> {}, "Failed to persist validator vote changes.");
     recentChainData.updateBestBlock(
         headBlockRoot,
-        forkChoiceStrategy
-            .blockSlot(headBlockRoot)
-            .orElseThrow(
-                () ->
-                    new IllegalStateException("Unable to retrieve the slot of fork choice head")));
+        nodeSlot.orElse(
+            forkChoiceStrategy
+                .blockSlot(headBlockRoot)
+                .orElseThrow(
+                    () ->
+                        new IllegalStateException(
+                            "Unable to retrieve the slot of fork choice head"))));
     return headBlockRoot;
   }
 
```

### ethereum/statetransition/src/test/java/tech/pegasys/teku/statetransition/forkchoice/ForkChoiceTest.java
```diff
@@ -0,0 +1,63 @@
+/*
+ * Copyright 2020 ConsenSys AG.
+ *
+ * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
+ * the License. You may obtain a copy of the License at
+ *
+ * http://www.apache.org/licenses/LICENSE-2.0
+ *
+ * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
+ * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
+ * specific language governing permissions and limitations under the License.
+ */
+
+package tech.pegasys.teku.statetransition.forkchoice;
+
+import static com.google.common.primitives.UnsignedLong.ONE;
+import static org.assertj.core.api.Assertions.assertThat;
+import static org.mockito.Mockito.mock;
+
+import java.util.List;
+import java.util.Optional;
+import org.junit.jupiter.api.BeforeEach;
+import org.junit.jupiter.api.Test;
+import tech.pegasys.teku.core.ChainBuilder;
+import tech.pegasys.teku.core.StateTransition;
+import tech.pegasys.teku.datastructures.blocks.SignedBlockAndState;
+import tech.pegasys.teku.storage.api.TrackingReorgEventChannel.ReorgEvent;
+import tech.pegasys.teku.storage.client.RecentChainData;
+import tech.pegasys.teku.storage.storageSystem.InMemoryStorageSystem;
+import tech.pegasys.teku.storage.storageSystem.StorageSystem;
+import tech.pegasys.teku.util.config.StateStorageMode;
+
+class ForkChoiceTest {
+
+  private final StateTransition stateTransition = mock(StateTransition.class);
+  private final StorageSystem storageSystem =
+      InMemoryStorageSystem.createEmptyV3StorageSystem(StateStorageMode.PRUNE);
+  private final ChainBuilder chainBuilder = storageSystem.chainBuilder();
+  private final SignedBlockAndState genesis = chainBuilder.generateGenesis();
+  private final RecentChainData recentChainData = storageSystem.recentChainData();
+
+  private final ForkChoice forkChoice = new ForkChoice(recentChainData, stateTransition);
+
+  @BeforeEach
+  public void setup() {
+    recentChainData.initializeFromGenesis(genesis.getState());
+  }
+
+  @Test
+  void shouldTriggerReorgWhenEmptyHeadSlotFilled() {
+    // Run fork choice with an empty slot 1
+    forkChoice.processHead(Optional.of(ONE));
+
+    // Then rerun with a filled slot 1
+    final SignedBlockAndState slot1Block = storageSystem.chainUpdater().advanceChain(ONE);
+    forkChoice.processHead(Optional.of(ONE));
+
+    final List<ReorgEvent> reorgEvents = storageSystem.reorgEventChannel().getReorgEvents();
+    assertThat(reorgEvents).hasSize(1);
+    assertThat(reorgEvents.get(0).getBestSlot()).isEqualTo(ONE);
+    assertThat(reorgEvents.get(0).getBestBlockRoot()).isEqualTo(slot1Block.getRoot());
+  }
+}
```

### ethereum/statetransition/src/testFixtures/java/tech/pegasys/teku/statetransition/BeaconChainUtil.java
```diff
@@ -193,7 +193,7 @@ public SignedBeaconBlock createAndImportBlockAtSlot(
               + ": "
               + block);
     }
-    forkChoice.processHead();
+    forkChoice.processHead(slot);
     return importResult.getBlock();
   }
 
```

### services/beaconchain/src/main/java/tech/pegasys/teku/services/beaconchain/SlotProcessor.java
```diff
@@ -126,10 +126,10 @@ public void onTick(final UnsignedLong currentTime) {
   }
 
   private void processSlotWhileSyncing() {
-    this.forkChoice.processHead();
-    eventLog.syncEvent(
-        nodeSlot.getValue(), recentChainData.getBestSlot(), p2pNetwork.getPeerCount());
-    slotEventsChannelPublisher.onSlot(nodeSlot.getValue());
+    UnsignedLong slot = nodeSlot.getValue();
+    this.forkChoice.processHead(slot);
+    eventLog.syncEvent(slot, recentChainData.getBestSlot(), p2pNetwork.getPeerCount());
+    slotEventsChannelPublisher.onSlot(slot);
   }
 
   boolean isNextSlotDue(final UnsignedLong currentTime, final UnsignedLong genesisTime) {
@@ -186,7 +186,7 @@ private void processSlotStart(final UnsignedLong nodeEpoch) {
 
   private void processSlotAttestation(final UnsignedLong nodeEpoch) {
     onTickSlotAttestation = nodeSlot.getValue();
-    Bytes32 headBlockRoot = this.forkChoice.processHead();
+    Bytes32 headBlockRoot = this.forkChoice.processHead(onTickSlotAttestation);
     eventLog.slotEvent(
         nodeSlot.getValue(),
         recentChainData.getBestSlot(),
```

### services/beaconchain/src/test/java/tech/pegasys/teku/services/beaconchain/SlotProcessorTest.java
```diff
@@ -212,7 +212,7 @@ public void onTick_shouldRunAttestationsDuringProcessing() {
         EventSink.capture(eventBus, BroadcastAttestationEvent.class);
     when(syncService.isSyncActive()).thenReturn(false);
 
-    when(forkChoice.processHead()).thenReturn(bestRoot);
+    when(forkChoice.processHead(slotProcessor.getNodeSlot().getValue())).thenReturn(bestRoot);
     when(p2pNetwork.getPeerCount()).thenReturn(1);
 
     slotProcessor.onTick(
```

### storage/src/main/java/tech/pegasys/teku/storage/client/RecentChainData.java
```diff
@@ -66,7 +66,7 @@ public abstract class RecentChainData implements StoreUpdateHandler {
 
   private volatile UpdatableStore store;
   private volatile Optional<ProtoArrayForkChoiceStrategy> forkChoiceStrategy;
-  private volatile Optional<SignedBlockAndState> chainHead = Optional.empty();
+  private volatile Optional<SignedBlockAndStateAndSlot> chainHead = Optional.empty();
   private volatile UnsignedLong genesisTime;
 
   RecentChainData(
@@ -181,11 +181,12 @@ public void updateBestBlock(Bytes32 root, UnsignedLong slot) {
             newBestBlock == null ? "block" : "state");
         return;
       }
-      final SignedBlockAndState newChainHead = new SignedBlockAndState(newBestBlock, newBestState);
+      final SignedBlockAndStateAndSlot newChainHead =
+          new SignedBlockAndStateAndSlot(newBestBlock, newBestState, slot);
 
       final Optional<Bytes32> originalBestRoot = chainHead.map(SignedBlockAndState::getRoot);
       final UnsignedLong originalBestSlot =
-          chainHead.map(SignedBlockAndState::getSlot).orElse(UnsignedLong.ZERO);
+          chainHead.map(SignedBlockAndStateAndSlot::getHeadSlot).orElse(UnsignedLong.ZERO);
 
       this.chainHead = Optional.of(newChainHead);
       if (originalBestRoot
@@ -356,4 +357,18 @@ public void onNewFinalizedCheckpoint(Checkpoint finalizedCheckpoint) {
     finalizedCheckpointChannel.onNewFinalizedCheckpoint(finalizedCheckpoint);
     forkChoiceStrategy.ifPresent(strategy -> strategy.maybePrune(finalizedCheckpoint.getRoot()));
   }
+
+  private static class SignedBlockAndStateAndSlot extends SignedBlockAndState {
+    private final UnsignedLong headSlot;
+
+    public SignedBlockAndStateAndSlot(
+        SignedBeaconBlock block, BeaconState state, UnsignedLong headSlot) {
+      super(block, state);
+      this.headSlot = headSlot;
+    }
+
+    public UnsignedLong getHeadSlot() {
+      return headSlot;
+    }
+  }
 }
```

### storage/src/test/java/tech/pegasys/teku/storage/client/RecentChainDataTest.java
```diff
@@ -13,6 +13,7 @@
 
 package tech.pegasys.teku.storage.client;
 
+import static com.google.common.primitives.UnsignedLong.ONE;
 import static java.util.stream.Collectors.toList;
 import static org.assertj.core.api.Assertions.assertThat;
 import static tech.pegasys.teku.datastructures.util.BeaconStateUtil.compute_epoch_at_slot;
@@ -107,8 +108,8 @@ public void getStateInEffectAtSlot_returnGenesisStateWhenItIsTheBestState() {
   @Test
   public void getStateInEffectAtSlot_returnStateFromLastBlockWhenSlotsAreEmpty() throws Exception {
     // Request block for an empty slot immediately after genesis
-    final UnsignedLong requestedSlot = genesisBlock.getSlot().plus(UnsignedLong.ONE);
-    final UnsignedLong bestSlot = requestedSlot.plus(UnsignedLong.ONE);
+    final UnsignedLong requestedSlot = genesisBlock.getSlot().plus(ONE);
+    final UnsignedLong bestSlot = requestedSlot.plus(ONE);
 
     final SignedBlockAndState bestBlock = chainBuilder.generateBlockAtSlot(bestSlot);
     updateBestBlock(storageClient, bestBlock);
@@ -118,7 +119,7 @@ public void getStateInEffectAtSlot_returnStateFromLastBlockWhenSlotsAreEmpty() t
 
   @Test
   public void getStateInEffectAtSlot_returnStateFromLastBlockWhenHeadSlotIsEmpty() {
-    assertThat(storageClient.getStateInEffectAtSlot(UnsignedLong.ONE)).contains(genesisState);
+    assertThat(storageClient.getStateInEffectAtSlot(ONE)).contains(genesisState);
   }
 
   @Test
@@ -138,7 +139,7 @@ public void startStoreTransaction_mutateFinalizedCheckpoint() throws StateTransi
 
     // Add a new finalized checkpoint
     final SignedBlockAndState newBlock = advanceChain(preGenesisStorageClient);
-    final UnsignedLong finalizedEpoch = originalCheckpoint.getEpoch().plus(UnsignedLong.ONE);
+    final UnsignedLong finalizedEpoch = originalCheckpoint.getEpoch().plus(ONE);
     final Checkpoint newCheckpoint = new Checkpoint(finalizedEpoch, newBlock.getRoot());
     assertThat(originalCheckpoint).isNotEqualTo(newCheckpoint); // Sanity check
 
@@ -193,6 +194,28 @@ public void updateBestBlock_noReorgEventWhenChainAdvances() throws Exception {
     assertThat(preGenesisStorageSystem.reorgEventChannel().getReorgEvents()).isEmpty();
   }
 
+  @Test
+  public void updateBestBlock_reorgEventWhenBlockFillsEmptyHeadSlot() throws Exception {
+    final ChainBuilder chainBuilder = ChainBuilder.create(BLSKeyGenerator.generateKeyPairs(1));
+    chainBuilder.generateGenesis();
+    preGenesisStorageClient.initializeFromGenesis(chainBuilder.getStateAtSlot(0));
+    assertThat(preGenesisStorageSystem.reorgEventChannel().getReorgEvents()).isEmpty();
+
+    final SignedBlockAndState slot1Block = chainBuilder.generateBlockAtSlot(1);
+    importBlocksAndStates(chainBuilder);
+    preGenesisStorageClient.updateBestBlock(slot1Block.getRoot(), UnsignedLong.valueOf(2));
+    assertThat(preGenesisStorageSystem.reorgEventChannel().getReorgEvents()).isEmpty();
+
+    final SignedBlockAndState slot2Block = chainBuilder.generateBlockAtSlot(2);
+    importBlocksAndStates(chainBuilder);
+    preGenesisStorageClient.updateBestBlock(slot2Block.getRoot(), slot2Block.getSlot());
+    final List<ReorgEvent> reorgEvents =
+        preGenesisStorageSystem.reorgEventChannel().getReorgEvents();
+    assertThat(reorgEvents).hasSize(1);
+    assertThat(reorgEvents.get(0).getBestBlockRoot()).isEqualTo(slot2Block.getRoot());
+    assertThat(reorgEvents.get(0).getBestSlot()).isEqualTo(slot2Block.getSlot());
+  }
+
   @Test
   public void updateBestBlock_reorgEventWhenChainSwitchesToNewBlockAtSameSlot() throws Exception {
     final ChainBuilder chainBuilder = ChainBuilder.create(BLSKeyGenerator.generateKeyPairs(16));
@@ -206,7 +229,7 @@ public void updateBestBlock_reorgEventWhenChainSwitchesToNewBlockAtSameSlot() th
     // and generate block options to make each block unique
     final List<BlockOptions> blockOptions =
         chainBuilder
-            .streamValidAttestationsForBlockAtSlot(UnsignedLong.ONE)
+            .streamValidAttestationsForBlockAtSlot(ONE)
             .map(attestation -> BlockOptions.create().addAttestation(attestation))
             .limit(2)
             .collect(toList());
@@ -246,7 +269,7 @@ public void updateBestBlock_reorgEventWhenChainSwitchesToNewBlockAtLaterSlot() t
     // and generate block options to make each block unique
     final List<BlockOptions> blockOptions =
         chainBuilder
-            .streamValidAttestationsForBlockAtSlot(UnsignedLong.ONE)
+            .streamValidAttestationsForBlockAtSlot(ONE)
             .map(attestation -> BlockOptions.create().addAttestation(attestation))
             .limit(2)
             .collect(toList());
@@ -283,9 +306,9 @@ public void getLatestFinalizedBlockSlot_genesis() {
   @Test
   public void getLatestFinalizedBlockSlot_postGenesisFinalizedBlockOutsideOfEpochBoundary()
       throws Exception {
-    final UnsignedLong epoch = UnsignedLong.ONE;
+    final UnsignedLong epoch = ONE;
     final UnsignedLong epochBoundarySlot = compute_start_slot_at_epoch(epoch);
-    final UnsignedLong finalizedBlockSlot = epochBoundarySlot.minus(UnsignedLong.ONE);
+    final UnsignedLong finalizedBlockSlot = epochBoundarySlot.minus(ONE);
     final SignedBlockAndState finalizedBlock = chainBuilder.generateBlockAtSlot(finalizedBlockSlot);
     saveBlock(storageClient, finalizedBlock);
 
@@ -332,9 +355,8 @@ public void getBlockRootBySlot_forOutOfRangeSlot() throws Exception {
     disableForkChoicePruneThreshold();
     final UnsignedLong historicalRoots = UnsignedLong.valueOf(Constants.SLOTS_PER_HISTORICAL_ROOT);
     final UnsignedLong targetSlot = UnsignedLong.valueOf(10);
-    final UnsignedLong finalizedBlockSlot = targetSlot.plus(historicalRoots).plus(UnsignedLong.ONE);
-    final UnsignedLong finalizedEpoch =
-        compute_epoch_at_slot(finalizedBlockSlot).plus(UnsignedLong.ONE);
+    final UnsignedLong finalizedBlockSlot = targetSlot.plus(historicalRoots).plus(ONE);
+    final UnsignedLong finalizedEpoch = compute_epoch_at_slot(finalizedBlockSlot).plus(ONE);
 
     // Add a block within the finalized range
     final SignedBlockAndState historicalBlock = chainBuilder.generateBlockAtSlot(targetSlot);
@@ -351,8 +373,7 @@ public void getBlockRootBySlot_forHistoricalSlotInRange() throws Exception {
     final UnsignedLong historicalRoots = UnsignedLong.valueOf(Constants.SLOTS_PER_HISTORICAL_ROOT);
     final UnsignedLong targetSlot = UnsignedLong.valueOf(10);
     final UnsignedLong finalizedBlockSlot = targetSlot.plus(historicalRoots);
-    final UnsignedLong finalizedEpoch =
-        compute_epoch_at_slot(finalizedBlockSlot).plus(UnsignedLong.ONE);
+    final UnsignedLong finalizedEpoch = compute_epoch_at_slot(finalizedBlockSlot).plus(ONE);
 
     // Add a block within the finalized range
     final SignedBlockAndState historicalBlock = chainBuilder.generateBlockAtSlot(targetSlot);
@@ -384,7 +405,7 @@ public void getBlockRootBySlot_forBlockPriorToBestBlock() throws Exception {
   public void getBlockRootBySlot_forSlotAfterBestBlock() throws Exception {
     final SignedBlockAndState bestBlock = advanceBestBlock(storageClient);
 
-    final UnsignedLong targetSlot = bestBlock.getSlot().plus(UnsignedLong.ONE);
+    final UnsignedLong targetSlot = bestBlock.getSlot().plus(ONE);
     assertThat(storageClient.getBlockRootBySlot(targetSlot)).contains(bestBlock.getRoot());
   }
 
@@ -399,8 +420,7 @@ public void getBlockRootBySlot_queryEntireChain() throws Exception {
     final UnsignedLong finalizedBlockSlot = UnsignedLong.valueOf(10).plus(historicalRoots);
     final UnsignedLong finalizedEpoch =
         ChainProperties.computeBestEpochFinalizableAtSlot(finalizedBlockSlot);
-    final UnsignedLong recentSlot =
-        compute_start_slot_at_epoch(finalizedEpoch).plus(UnsignedLong.ONE);
+    final UnsignedLong recentSlot = compute_start_slot_at_epoch(finalizedEpoch).plus(ONE);
     final UnsignedLong chainHeight =
         historicalRoots
             .times(UnsignedLong.valueOf(2))
```
