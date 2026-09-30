# [?] Fix race condition when committing changes to fork choice votes (#2602)

## Summary
Severity: Unknown
Chain: Ethereum
Component: Consensys-Incorporated/teku
Published: 2020-08-18
Source: https://github.com/Consensys-Incorporated/teku/commit/39bfecad0bff96e5ab31aaca970929f45b61b94d
Type: security-commit

## Details
Fix race condition when committing changes to fork choice votes (#2602)

## Patch
### ethereum/statetransition/src/main/java/tech/pegasys/teku/statetransition/attestation/AttestationManager.java
```diff
@@ -27,6 +27,7 @@
 import tech.pegasys.teku.infrastructure.unsigned.UInt64;
 import tech.pegasys.teku.service.serviceutils.Service;
 import tech.pegasys.teku.statetransition.events.block.ImportedBlockEvent;
+import tech.pegasys.teku.statetransition.forkchoice.ForkChoice;
 import tech.pegasys.teku.statetransition.util.FutureItems;
 import tech.pegasys.teku.statetransition.util.PendingPool;
 import tech.pegasys.teku.util.events.Subscribers;
@@ -39,7 +40,7 @@ public class AttestationManager extends Service implements SlotEventsChannel {
       SafeFuture.completedFuture(AttestationProcessingResult.SAVED_FOR_FUTURE);
 
   private final EventBus eventBus;
-  private final ForkChoiceAttestationProcessor attestationProcessor;
+  private final ForkChoice attestationProcessor;
 
   private final PendingPool<ValidateableAttestation> pendingAttestations;
   private final FutureItems<ValidateableAttestation> futureAttestations;
@@ -50,7 +51,7 @@ public class AttestationManager extends Service implements SlotEventsChannel {
 
   AttestationManager(
       final EventBus eventBus,
-      final ForkChoiceAttestationProcessor attestationProcessor,
+      final ForkChoice attestationProcessor,
       final PendingPool<ValidateableAttestation> pendingAttestations,
       final FutureItems<ValidateableAttestation> futureAttestations,
       final AggregatingAttestationPool aggregatingAttestationPool) {
@@ -65,11 +66,11 @@ public static AttestationManager create(
       final EventBus eventBus,
       final PendingPool<ValidateableAttestation> pendingAttestations,
       final FutureItems<ValidateableAttestation> futureAttestations,
-      final ForkChoiceAttestationProcessor forkChoiceAttestationProcessor,
+      final ForkChoice attestationProcessor,
       final AggregatingAttestationPool aggregatingAttestationPool) {
     return new AttestationManager(
         eventBus,
-        forkChoiceAttestationProcessor,
+        attestationProcessor,
         pendingAttestations,
         futureAttestations,
         aggregatingAttestationPool);
@@ -83,10 +84,10 @@ public void subscribeToProcessedAttestations(
   @Override
   public void onSlot(final UInt64 slot) {
     List<ValidateableAttestation> attestations = futureAttestations.prune(slot);
-    attestations.stream()
-        .map(ValidateableAttestation::getIndexedAttestation)
-        .forEach(attestationProcessor::applyIndexedAttestationToForkChoice);
-
+    if (attestations.isEmpty()) {
+      return;
+    }
+    attestationProcessor.applyIndexedAttestations(attestations);
     attestations.forEach(this::notifySubscribers);
   }
 
@@ -121,7 +122,7 @@ public SafeFuture<AttestationProcessingResult> onAttestation(
     }
 
     return attestationProcessor
-        .processAttestation(attestation)
+        .onAttestation(attestation)
         .thenApply(
             result -> {
               switch (result.getStatus()) {
```

### ethereum/statetransition/src/main/java/tech/pegasys/teku/statetransition/attestation/ForkChoiceAttestationProcessor.java
```diff
@@ -1,45 +0,0 @@
-/*
- * Copyright 2020 ConsenSys AG.
- *
- * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
- * the License. You may obtain a copy of the License at
- *
- * http://www.apache.org/licenses/LICENSE-2.0
- *
- * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
- * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
- * specific language governing permissions and limitations under the License.
- */
-
-package tech.pegasys.teku.statetransition.attestation;
-
-import tech.pegasys.teku.datastructures.attestation.ValidateableAttestation;
-import tech.pegasys.teku.datastructures.operations.IndexedAttestation;
-import tech.pegasys.teku.datastructures.util.AttestationProcessingResult;
-import tech.pegasys.teku.infrastructure.async.SafeFuture;
-import tech.pegasys.teku.statetransition.forkchoice.ForkChoice;
-import tech.pegasys.teku.storage.client.RecentChainData;
-import tech.pegasys.teku.storage.store.UpdatableStore.StoreTransaction;
-
-public class ForkChoiceAttestationProcessor {
-
-  private final RecentChainData recentChainData;
-  private final ForkChoice forkChoice;
-
-  public ForkChoiceAttestationProcessor(
-      final RecentChainData recentChainData, final ForkChoice forkChoice) {
-    this.recentChainData = recentChainData;
-    this.forkChoice = forkChoice;
-  }
-
-  public SafeFuture<AttestationProcessingResult> processAttestation(
-      final ValidateableAttestation attestation) {
-    return forkChoice.onAttestation(attestation);
-  }
-
-  public void applyIndexedAttestationToForkChoice(final IndexedAttestation attestation) {
-    final StoreTransaction transaction = recentChainData.startStoreTransaction();
-    forkChoice.applyIndexedAttestation(transaction, attestation);
-    transaction.commit(() -> {}, "Failed to persist attestation result");
-  }
-}
```

### ethereum/statetransition/src/main/java/tech/pegasys/teku/statetransition/blockimport/BlockImporter.java
```diff
@@ -39,13 +39,13 @@ public class BlockImporter {
   private final ForkChoice forkChoice;
   private final EventBus eventBus;
 
-  private Subscribers<VerifiedBlockOperationsListener<Attestation>> attestationSubscribers =
+  private final Subscribers<VerifiedBlockOperationsListener<Attestation>> attestationSubscribers =
       Subscribers.create(true);
-  private Subscribers<VerifiedBlockOperationsListener<AttesterSlashing>>
+  private final Subscribers<VerifiedBlockOperationsListener<AttesterSlashing>>
       attesterSlashingSubscribers = Subscribers.create(true);
-  private Subscribers<VerifiedBlockOperationsListener<ProposerSlashing>>
+  private final Subscribers<VerifiedBlockOperationsListener<ProposerSlashing>>
       proposerSlashingSubscribers = Subscribers.create(true);
-  private Subscribers<VerifiedBlockOperationsListener<SignedVoluntaryExit>>
+  private final Subscribers<VerifiedBlockOperationsListener<SignedVoluntaryExit>>
       voluntaryExitSubscribers = Subscribers.create(true);
 
   public BlockImporter(
@@ -68,9 +68,9 @@ public SafeFuture<BlockImportResult> importBlock(SignedBeaconBlock block) {
 
     return recentChainData
         .retrieveBlockState(block.getParent_root())
+        .thenCompose(preState -> forkChoice.onBlock(block, preState))
         .thenApply(
-            preState -> {
-              BlockImportResult result = forkChoice.onBlock(block, preState);
+            result -> {
               if (!result.isSuccessful()) {
                 LOG.trace(
                     "Failed to import block for reason {}: {}",
```

### ethereum/statetransition/src/main/java/tech/pegasys/teku/statetransition/forkchoice/ForkChoice.java
```diff
@@ -16,25 +16,29 @@
 import static tech.pegasys.teku.core.ForkChoiceUtil.on_attestation;
 import static tech.pegasys.teku.core.ForkChoiceUtil.on_block;
 
+import java.util.List;
 import java.util.Optional;
+import java.util.concurrent.Semaphore;
+import java.util.function.Supplier;
 import org.apache.tuweni.bytes.Bytes32;
 import tech.pegasys.teku.core.StateTransition;
 import tech.pegasys.teku.core.results.BlockImportResult;
 import tech.pegasys.teku.datastructures.attestation.ValidateableAttestation;
 import tech.pegasys.teku.datastructures.blocks.SignedBeaconBlock;
 import tech.pegasys.teku.datastructures.blocks.SlotAndBlockRoot;
-import tech.pegasys.teku.datastructures.forkchoice.MutableStore;
-import tech.pegasys.teku.datastructures.operations.IndexedAttestation;
 import tech.pegasys.teku.datastructures.state.BeaconState;
 import tech.pegasys.teku.datastructures.state.Checkpoint;
 import tech.pegasys.teku.datastructures.util.AttestationProcessingResult;
 import tech.pegasys.teku.infrastructure.async.SafeFuture;
 import tech.pegasys.teku.infrastructure.unsigned.UInt64;
 import tech.pegasys.teku.protoarray.ForkChoiceStrategy;
 import tech.pegasys.teku.storage.client.RecentChainData;
+import tech.pegasys.teku.storage.server.ShuttingDownException;
 import tech.pegasys.teku.storage.store.UpdatableStore.StoreTransaction;
 
 public class ForkChoice {
+
+  private final Semaphore lock = new Semaphore(1);
   private final RecentChainData recentChainData;
   private final StateTransition stateTransition;
 
@@ -48,97 +52,121 @@ private void initializeProtoArrayForkChoice() {
     processHead();
   }
 
-  public synchronized void processHead() {
+  private void processHead() {
     processHead(Optional.empty());
   }
 
-  public synchronized void processHead(UInt64 nodeSlot) {
+  public void processHead(UInt64 nodeSlot) {
     processHead(Optional.of(nodeSlot));
   }
 
-  private synchronized void processHead(Optional<UInt64> nodeSlot) {
-    final Checkpoint finalizedCheckpoint = recentChainData.getStore().getFinalizedCheckpoint();
-    final Checkpoint justifiedCheckpoint = recentChainData.getStore().getJustifiedCheckpoint();
-    recentChainData
-        .retrieveCheckpointState(justifiedCheckpoint)
-        .thenAccept(
-            justifiedCheckpointState -> {
-              StoreTransaction transaction = recentChainData.startStoreTransaction();
-              final ForkChoiceStrategy forkChoiceStrategy = getForkChoiceStrategy();
-              Bytes32 headBlockRoot =
-                  forkChoiceStrategy.findHead(
-                      transaction,
-                      finalizedCheckpoint,
-                      justifiedCheckpoint,
-                      justifiedCheckpointState.orElseThrow());
-              transaction.commit(() -> {}, "Failed to persist validator vote changes.");
-
-              recentChainData.updateHead(
-                  headBlockRoot,
-                  nodeSlot.orElse(
-                      forkChoiceStrategy
-                          .blockSlot(headBlockRoot)
-                          .orElseThrow(
-                              () ->
-                                  new IllegalStateException(
-                                      "Unable to retrieve the slot of fork choice head"))));
+  private void processHead(Optional<UInt64> nodeSlot) {
+    withLock(
+            () -> {
+              final Checkpoint finalizedCheckpoint =
+                  recentChainData.getStore().getFinalizedCheckpoint();
+              final Checkpoint justifiedCheckpoint =
+                  recentChainData.getStore().getJustifiedCheckpoint();
+              return recentChainData
+                  .retrieveCheckpointState(justifiedCheckpoint)
+                  .thenCompose(
+                      justifiedCheckpointState -> {
+                        final StoreTransaction transaction =
+                            recentChainData.startStoreTransaction();
+                        final ForkChoiceStrategy forkChoiceStrategy = getForkChoiceStrategy();
+                        Bytes32 headBlockRoot =
+                            forkChoiceStrategy.findHead(
+                                transaction,
+                                finalizedCheckpoint,
+                                justifiedCheckpoint,
+                                justifiedCheckpointState.orElseThrow());
+
+                        recentChainData.updateHead(
+                            headBlockRoot,
+                            nodeSlot.orElse(
+                                forkChoiceStrategy
+                                    .blockSlot(headBlockRoot)
+                                    .orElseThrow(
+                                        () ->
+                                            new IllegalStateException(
+                                                "Unable to retrieve the slot of fork choice head"))));
+                        return transaction.commit();
+                      });
             })
         .join();
   }
 
-  public synchronized BlockImportResult onBlock(
+  public SafeFuture<BlockImportResult> onBlock(
       final SignedBeaconBlock block, Optional<BeaconState> preState) {
-    final ForkChoiceStrategy forkChoiceStrategy = getForkChoiceStrategy();
-    StoreTransaction transaction = recentChainData.startStoreTransaction();
-    final BlockImportResult result =
-        on_block(
-            transaction,
-            block,
-            preState,
-            stateTransition,
-            forkChoiceStrategy,
-            beaconState ->
-                transaction.putStateRoot(
-                    beaconState.hash_tree_root(),
-                    new SlotAndBlockRoot(
-                        beaconState.getSlot(),
-                        beaconState.getLatest_block_header().hash_tree_root())));
-
-    if (!result.isSuccessful()) {
-      return result;
-    }
-
-    transaction.commit().join();
-    result
-        .getBlockProcessingRecord()
-        .ifPresent(record -> forkChoiceStrategy.onBlock(block.getMessage(), record.getPostState()));
-
-    return result;
+    return withLock(
+        () -> {
+          final ForkChoiceStrategy forkChoiceStrategy = getForkChoiceStrategy();
+          final StoreTransaction transaction = recentChainData.startStoreTransaction();
+          final BlockImportResult result =
+              on_block(
+                  transaction,
+                  block,
+                  preState,
+                  stateTransition,
+                  forkChoiceStrategy,
+                  beaconState ->
+                      transaction.putStateRoot(
+                          beaconState.hash_tree_root(),
+                          new SlotAndBlockRoot(
+                              beaconState.getSlot(),
+                              beaconState.getLatest_block_header().hash_tree_root())));
+
+          if (!result.isSuccessful()) {
+            return SafeFuture.completedFuture(result);
+          }
+          return transaction
+              .commit()
+              .thenRun(
+                  () ->
+                      result
+                          .getBlockProcessingRecord()
+                          .ifPresent(
+                              record ->
+                                  forkChoiceStrategy.onBlock(
+                                      block.getMessage(), record.getPostState())))
+              .thenApply(__ -> result);
+        });
   }
 
   public SafeFuture<AttestationProcessingResult> onAttestation(
       final ValidateableAttestation attestation) {
     return recentChainData
         .retrieveCheckpointState(attestation.getData().getTarget())
-        .thenApply(
-            targetState -> {
-              StoreTransaction transaction = recentChainData.startStoreTransaction();
-              final AttestationProcessingResult result =
-                  on_attestation(transaction, attestation, targetState, getForkChoiceStrategy());
-              if (result.isSuccessful()) {
-                transaction.commit(() -> {}, "Failed to persist attestation result");
-              }
-              return result;
-            });
+        .thenCompose(
+            targetState ->
+                withLock(
+                    () -> {
+                      final StoreTransaction transaction = recentChainData.startStoreTransaction();
+                      final AttestationProcessingResult result =
+                          on_attestation(
+                              transaction, attestation, targetState, getForkChoiceStrategy());
+                      return result.isSuccessful()
+                          ? transaction.commit().thenApply(__ -> result)
+                          : SafeFuture.completedFuture(result);
+                    }));
   }
 
   public void save() {
     getForkChoiceStrategy().save();
   }
 
-  public void applyIndexedAttestation(
-      final MutableStore store, final IndexedAttestation indexedAttestation) {
-    getForkChoiceStrategy().onAttestation(store, indexedAttestation);
+  public void applyIndexedAttestations(final List<ValidateableAttestation> attestations) {
+    withLock(
+            () -> {
+              final StoreTransaction transaction = recentChainData.startStoreTransaction();
+              final ForkChoiceStrategy forkChoiceStrategy = getForkChoiceStrategy();
+              attestations.stream()
+                  .map(ValidateableAttestation::getIndexedAttestation)
+                  .forEach(
+                      attestation -> forkChoiceStrategy.onAttestation(transaction, attestation));
+              return transaction.commit();
+            })
+        .reportExceptions();
   }
 
   private ForkChoiceStrategy getForkChoiceStrategy() {
@@ -149,4 +177,13 @@ private ForkChoiceStrategy getForkChoiceStrategy() {
                 new IllegalStateException(
                     "Attempting to perform fork choice operations before store has been initialized"));
   }
+
+  private <T> SafeFuture<T> withLock(final Supplier<SafeFuture<T>> action) {
+    try {
+      lock.acquire();
+    } catch (InterruptedException e) {
+      throw new ShuttingDownException();
+    }
+    return SafeFuture.ofComposed(action::get).alwaysRun(lock::release);
+  }
 }
```

### ethereum/statetransition/src/test/java/tech/pegasys/teku/statetransition/attestation/AttestationManagerTest.java
```diff
@@ -15,7 +15,6 @@
 
 import static org.assertj.core.api.Assertions.assertThat;
 import static org.mockito.ArgumentMatchers.any;
-import static org.mockito.ArgumentMatchers.eq;
 import static org.mockito.Mockito.mock;
 import static org.mockito.Mockito.never;
 import static org.mockito.Mockito.times;
@@ -29,6 +28,7 @@
 import static tech.pegasys.teku.infrastructure.async.SafeFuture.completedFuture;
 
 import com.google.common.eventbus.EventBus;
+import java.util.List;
 import org.apache.tuweni.bytes.Bytes32;
 import org.junit.jupiter.api.AfterEach;
 import org.junit.jupiter.api.BeforeEach;
@@ -47,6 +47,7 @@
 import tech.pegasys.teku.ssz.SSZTypes.Bitlist;
 import tech.pegasys.teku.ssz.SSZTypes.SSZList;
 import tech.pegasys.teku.statetransition.events.block.ImportedBlockEvent;
+import tech.pegasys.teku.statetransition.forkchoice.ForkChoice;
 import tech.pegasys.teku.statetransition.util.FutureItems;
 import tech.pegasys.teku.statetransition.util.PendingPool;
 
@@ -55,16 +56,15 @@ class AttestationManagerTest {
   private final EventBus eventBus = new EventBus();
 
   private final AggregatingAttestationPool attestationPool = mock(AggregatingAttestationPool.class);
-  private final ForkChoiceAttestationProcessor attestationProcessor =
-      mock(ForkChoiceAttestationProcessor.class);
+  private final ForkChoice forkChoice = mock(ForkChoice.class);
   private final PendingPool<ValidateableAttestation> pendingAttestations =
       PendingPool.createForAttestations();
   private final FutureItems<ValidateableAttestation> futureAttestations =
       new FutureItems<>(ValidateableAttestation::getEarliestSlotForForkChoiceProcessing);
 
   private final AttestationManager attestationManager =
       new AttestationManager(
-          eventBus, attestationProcessor, pendingAttestations, futureAttestations, attestationPool);
+          eventBus, forkChoice, pendingAttestations, futureAttestations, attestationPool);
 
   @BeforeEach
   public void setup() {
@@ -80,7 +80,7 @@ public void cleanup() {
   public void shouldProcessAttestationsThatAreReadyImmediately() {
     final ValidateableAttestation attestation =
         ValidateableAttestation.fromAttestation(dataStructureUtil.randomAttestation());
-    when(attestationProcessor.processAttestation(any())).thenReturn(completedFuture(SUCCESSFUL));
+    when(forkChoice.onAttestation(any())).thenReturn(completedFuture(SUCCESSFUL));
     attestationManager.onAttestation(attestation).reportExceptions();
 
     verifyAttestationProcessed(attestation);
@@ -94,7 +94,7 @@ public void shouldProcessAggregatesThatAreReadyImmediately() {
     final ValidateableAttestation aggregate =
         ValidateableAttestation.fromSignedAggregate(
             dataStructureUtil.randomSignedAggregateAndProof());
-    when(attestationProcessor.processAttestation(any())).thenReturn(completedFuture(SUCCESSFUL));
+    when(forkChoice.onAttestation(any())).thenReturn(completedFuture(SUCCESSFUL));
     attestationManager.onAttestation(aggregate).reportExceptions();
 
     verifyAttestationProcessed(aggregate);
@@ -108,25 +108,25 @@ public void shouldAddAttestationsThatHaveNotYetReachedTargetSlotToFutureItemsAnd
     ValidateableAttestation attestation =
         ValidateableAttestation.fromAttestation(attestationFromSlot(100));
     IndexedAttestation randomIndexedAttestation = dataStructureUtil.randomIndexedAttestation();
-    when(attestationProcessor.processAttestation(any()))
-        .thenReturn(completedFuture(SAVED_FOR_FUTURE));
+    when(forkChoice.onAttestation(any())).thenReturn(completedFuture(SAVED_FOR_FUTURE));
     attestationManager.onAttestation(attestation).reportExceptions();
 
     ArgumentCaptor<ValidateableAttestation> captor =
         ArgumentCaptor.forClass(ValidateableAttestation.class);
-    verify(attestationProcessor).processAttestation(captor.capture());
-    captor.getValue().setIndexedAttestation(randomIndexedAttestation);
+    verify(forkChoice).onAttestation(captor.capture());
+    final ValidateableAttestation validateableAttestation = captor.getValue();
+    attestation.setIndexedAttestation(randomIndexedAttestation);
     verify(attestationPool).add(attestation);
     assertThat(futureAttestations.contains(captor.getValue())).isTrue();
     assertThat(pendingAttestations.size()).isEqualTo(0);
 
     // Shouldn't try to process the attestation until after it's slot.
     attestationManager.onSlot(UInt64.valueOf(100));
     assertThat(futureAttestations.size()).isEqualTo(1);
-    verify(attestationProcessor, never()).applyIndexedAttestationToForkChoice(any());
+    verify(forkChoice, never()).applyIndexedAttestations(any());
 
     attestationManager.onSlot(UInt64.valueOf(101));
-    verify(attestationProcessor).applyIndexedAttestationToForkChoice(eq(randomIndexedAttestation));
+    verify(forkChoice).applyIndexedAttestations(List.of(validateableAttestation));
     assertThat(futureAttestations.size()).isZero();
     assertThat(pendingAttestations.size()).isZero();
   }
@@ -137,28 +137,28 @@ public void shouldDeferProcessingForAttestationsThatAreMissingBlockDependencies(
     final Bytes32 requiredBlockRoot = block.getMessage().hash_tree_root();
     final ValidateableAttestation attestation =
         ValidateableAttestation.fromAttestation(attestationFromSlot(1, requiredBlockRoot));
-    when(attestationProcessor.processAttestation(any()))
+    when(forkChoice.onAttestation(any()))
         .thenReturn(completedFuture(UNKNOWN_BLOCK))
         .thenReturn(completedFuture(SUCCESSFUL));
     attestationManager.onAttestation(attestation).reportExceptions();
 
     ArgumentCaptor<ValidateableAttestation> captor =
         ArgumentCaptor.forClass(ValidateableAttestation.class);
-    verify(attestationProcessor).processAttestation(captor.capture());
+    verify(forkChoice).onAttestation(captor.capture());
     assertThat(futureAttestations.size()).isZero();
     assertThat(pendingAttestations.contains(captor.getValue())).isTrue();
     assertThat(pendingAttestations.size()).isEqualTo(1);
 
     // Slots progressing shouldn't cause the attestation to be processed
     attestationManager.onSlot(UInt64.valueOf(100));
-    verifyNoMoreInteractions(attestationProcessor);
+    verifyNoMoreInteractions(forkChoice);
 
     // Importing a different block shouldn't cause the attestation to be processed
     eventBus.post(new ImportedBlockEvent(dataStructureUtil.randomSignedBeaconBlock(2)));
-    verifyNoMoreInteractions(attestationProcessor);
+    verifyNoMoreInteractions(forkChoice);
 
     eventBus.post(new ImportedBlockEvent(block));
-    verify(attestationProcessor, times(2)).processAttestation(captor.getValue());
+    verify(forkChoice, times(2)).onAttestation(captor.getValue());
     assertThat(futureAttestations.size()).isZero();
     assertThat(pendingAttestations.size()).isZero();
     verify(attestationPool).add(attestation);
@@ -168,7 +168,7 @@ public void shouldDeferProcessingForAttestationsThatAreMissingBlockDependencies(
   public void shouldNotPublishProcessedAttestationEventWhenAttestationIsInvalid() {
     final ValidateableAttestation attestation =
         ValidateableAttestation.fromAttestation(dataStructureUtil.randomAttestation());
-    when(attestationProcessor.processAttestation(any()))
+    when(forkChoice.onAttestation(any()))
         .thenReturn(completedFuture(AttestationProcessingResult.invalid("Didn't like it")));
     attestationManager.onAttestation(attestation).reportExceptions();
 
@@ -183,7 +183,7 @@ public void shouldNotPublishProcessedAggregationEventWhenAttestationIsInvalid()
     final ValidateableAttestation aggregateAndProof =
         ValidateableAttestation.fromSignedAggregate(
             dataStructureUtil.randomSignedAggregateAndProof());
-    when(attestationProcessor.processAttestation(any()))
+    when(forkChoice.onAttestation(any()))
         .thenReturn(completedFuture(AttestationProcessingResult.invalid("Don't wanna")));
     attestationManager.onAttestation(aggregateAndProof).reportExceptions();
 
@@ -223,7 +223,7 @@ private Attestation attestationFromSlot(final long slot, final Bytes32 targetRoo
   private void verifyAttestationProcessed(final ValidateableAttestation attestation) {
     ArgumentCaptor<ValidateableAttestation> captor =
         ArgumentCaptor.forClass(ValidateableAttestation.class);
-    verify(attestationProcessor).processAttestation(captor.capture());
+    verify(forkChoice).onAttestation(captor.capture());
     assertThat(captor.getValue().getAttestation()).isSameAs(attestation.getAttestation());
   }
 }
```

### ethereum/statetransition/src/testFixtures/java/tech/pegasys/teku/statetransition/BeaconChainUtil.java
```diff
@@ -186,7 +186,7 @@ public SignedBeaconBlock createAndImportBlockAtSlot(
     setSlot(slot);
     final Optional<BeaconState> preState =
         recentChainData.retrieveBlockState(block.getParent_root()).join();
-    final BlockImportResult importResult = forkChoice.onBlock(block, preState);
+    final BlockImportResult importResult = forkChoice.onBlock(block, preState).join();
     if (!importResult.isSuccessful()) {
       throw new IllegalStateException(
           "Produced an invalid block ( reason "
```

### protoarray/src/main/java/tech/pegasys/teku/protoarray/ProtoArrayForkChoiceStrategy.java
```diff
@@ -93,13 +93,12 @@ public void onAttestation(final MutableStore store, final IndexedAttestation att
       attestation.getAttesting_indices().stream()
           .parallel()
           .forEach(
-              validatorIndex -> {
-                processAttestation(
-                    store,
-                    validatorIndex,
-                    attestation.getData().getBeacon_block_root(),
-                    attestation.getData().getTarget().getEpoch());
-              });
+              validatorIndex ->
+                  processAttestation(
+                      store,
+                      validatorIndex,
+                      attestation.getData().getBeacon_block_root(),
+                      attestation.getData().getTarget().getEpoch()));
     } finally {
       votesLock.writeLock().unlock();
     }
@@ -175,7 +174,7 @@ void processAttestation(
       MutableStore store, UInt64 validatorIndex, Bytes32 blockRoot, UInt64 targetEpoch) {
     VoteTracker vote = store.getVote(validatorIndex);
 
-    if (targetEpoch.compareTo(vote.getNextEpoch()) > 0 || vote.equals(VoteTracker.Default())) {
+    if (targetEpoch.isGreaterThan(vote.getNextEpoch()) || vote.equals(VoteTracker.Default())) {
       vote.setNextRoot(blockRoot);
       vote.setNextEpoch(targetEpoch);
     }
```

### protoarray/src/main/java/tech/pegasys/teku/protoarray/ProtoNode.java
```diff
@@ -62,9 +62,12 @@ public class ProtoNode {
   public void adjustWeight(long delta) {
     if (delta < 0) {
       UInt64 deltaAbsoluteValue = UInt64.valueOf(Math.abs(delta));
-      if (deltaAbsoluteValue.compareTo(weight) > 0) {
+      if (deltaAbsoluteValue.isGreaterThan(weight)) {
         throw new RuntimeException(
-            "ProtoNode: Delta to be subtracted is greater than node weight.");
+            "ProtoNode: Delta to be subtracted is greater than node weight. Attempting to subtract "
+                + deltaAbsoluteValue
+                + " from "
+                + weight);
       }
       weight = weight.minus(deltaAbsoluteValue);
     } else {
```

### services/beaconchain/src/main/java/tech/pegasys/teku/services/beaconchain/BeaconChainController.java
```diff
@@ -64,7 +64,6 @@
 import tech.pegasys.teku.statetransition.OperationPool;
 import tech.pegasys.teku.statetransition.attestation.AggregatingAttestationPool;
 import tech.pegasys.teku.statetransition.attestation.AttestationManager;
-import tech.pegasys.teku.statetransition.attestation.ForkChoiceAttestationProcessor;
 import tech.pegasys.teku.statetransition.blockimport.BlockImporter;
 import tech.pegasys.teku.statetransition.forkchoice.ForkChoice;
 import tech.pegasys.teku.statetransition.genesis.GenesisHandler;
@@ -346,15 +345,9 @@ private void initAttestationManager() {
         PendingPool.createForAttestations();
     final FutureItems<ValidateableAttestation> futureAttestations =
         new FutureItems<>(ValidateableAttestation::getEarliestSlotForForkChoiceProcessing);
-    final ForkChoiceAttestationProcessor forkChoiceAttestationProcessor =
-        new ForkChoiceAttestationProcessor(recentChainData, forkChoice);
     attestationManager =
         AttestationManager.create(
-            eventBus,
-            pendingAttestations,
-            futureAttestations,
-            forkChoiceAttestationProcessor,
-            attestationPool);
+            eventBus, pendingAttestations, futureAttestations, forkChoice, attestationPool);
     eventChannels
         .subscribe(SlotEventsChannel.class, attestationManager)
         .subscribe(FinalizedCheckpointChannel.class, pendingAttestations);
```
