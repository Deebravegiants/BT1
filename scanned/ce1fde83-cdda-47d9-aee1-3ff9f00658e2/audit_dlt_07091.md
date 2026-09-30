# [?] Fixes race condition between `NodeAddedListener` and `FullBlockImportStep` (#56)

## Summary
Severity: Unknown
Chain: Ethereum
Component: hyperledger/besu
Published: 2019-10-03
Source: https://github.com/besu-eth/besu/commit/c6ad0f7705b1c7dc5e66339279c06fe1aa9b411c
Type: security-commit

## Details
Fixes race condition between `NodeAddedListener` and `FullBlockImportStep` (#56)

Fixes race condition between attaching the NodeAddedListener and some state from post marked block being persisted. We now prepare and cleanup the listener only once each, on start and stop respectively.

Other changes:

Start the Pruner before FullSyncDownloader. Luckily the downloader took enough time to start downloading that this wasn't an issue but it's safer this way.

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

## Patch
### ethereum/core/src/integration-test/java/org/hyperledger/besu/ethereum/worldstate/PrunerIntegrationTest.java
```diff
@@ -123,6 +123,10 @@ private void testPruner(
       generateBlockchainData(numBlockInCycle, accountsPerBlock);
       assertThat(pruner.getState()).isEqualByComparingTo(Pruner.State.IDLE);
 
+      // Restarting the Pruner shouldn't matter since we're idle
+      pruner.stop();
+      pruner.start();
+
       // Collect the nodes we expect to keep
       final Set<BytesValue> expectedNodes = new HashSet<>();
       for (int i = fullyMarkedBlockNum; i <= blockchain.getChainHeadBlockNumber(); i++) {
```

### ethereum/core/src/main/java/org/hyperledger/besu/ethereum/worldstate/MarkSweepPruner.java
```diff
@@ -97,14 +97,12 @@ public MarkSweepPruner(
   }
 
   public void prepare() {
-    worldStateStorage.removeNodeAddedListener(nodeAddedListenerId); // Just in case.
-    markStorage.clear();
-    pendingMarks.clear();
-    nodeAddedListenerId = worldStateStorage.addNodeAddedListener(this::markNodes);
-  }
+    // Optimization for the case where the previous cycle was interrupted (like the node was shut
+    // down). If the previous cycle was interrupted, there will be marks in the mark storage from
+    // last time, causing the first sweep to be smaller than it needs to be.
+    clearMarks();
 
-  public void cleanup() {
-    worldStateStorage.removeNodeAddedListener(nodeAddedListenerId);
+    nodeAddedListenerId = worldStateStorage.addNodeAddedListener(this::markNodes);
   }
 
   public void mark(final Hash rootHash) {
@@ -151,9 +149,18 @@ public void sweepBefore(final long markedBlockNumber) {
     // Sweep non-state-root nodes
     prunedNodeCount += worldStateStorage.prune(this::isMarked);
     sweptNodesCounter.inc(prunedNodeCount);
+    clearMarks();
+    LOG.debug("Completed sweeping unused nodes");
+  }
+
+  public void cleanup() {
     worldStateStorage.removeNodeAddedListener(nodeAddedListenerId);
+    clearMarks();
+  }
+
+  public void clearMarks() {
     markStorage.clear();
-    LOG.debug("Completed sweeping unused nodes");
+    pendingMarks.clear();
   }
 
   private boolean isMarked(final Bytes32 key) {
@@ -190,7 +197,14 @@ private void processAccountState(final BytesValue value) {
 
   @VisibleForTesting
   void markNode(final Bytes32 hash) {
-    markNodes(Collections.singleton(hash));
+    markedNodesCounter.inc();
+    markLock.lock();
+    try {
+      pendingMarks.add(hash);
+      maybeFlushPendingMarks();
+    } finally {
+      markLock.unlock();
+    }
   }
 
   private void markNodes(final Collection<Bytes32> nodeHashes) {
@@ -210,7 +224,7 @@ private void maybeFlushPendingMarks() {
     }
   }
 
-  void flushPendingMarks() {
+  private void flushPendingMarks() {
     markLock.lock();
     try {
       final KeyValueStorageTransaction transaction = markStorage.startTransaction();
```

### ethereum/core/src/main/java/org/hyperledger/besu/ethereum/worldstate/Pruner.java
```diff
@@ -35,6 +35,7 @@ public class Pruner {
   private final MarkSweepPruner pruningStrategy;
   private final Blockchain blockchain;
   private final ExecutorService executorService;
+  private Long blockAddedObserverId;
   private final long blocksRetained;
   private final AtomicReference<State> state = new AtomicReference<>(State.IDLE);
   private volatile long markBlockNumber = 0;
@@ -58,11 +59,14 @@ public Pruner(
 
   public void start() {
     LOG.info("Starting Pruner.");
-    blockchain.observeBlockAdded((event, blockchain) -> handleNewBlock(event));
+    pruningStrategy.prepare();
+    blockAddedObserverId =
+        blockchain.observeBlockAdded((event, blockchain) -> handleNewBlock(event));
   }
 
   public void stop() throws InterruptedException {
     pruningStrategy.cleanup();
+    blockchain.removeObserver(blockAddedObserverId);
     executorService.awaitTermination(10, TimeUnit.SECONDS);
   }
 
@@ -73,7 +77,6 @@ private void handleNewBlock(final BlockAddedEvent event) {
 
     final long blockNumber = event.getBlock().getHeader().getNumber();
     if (state.compareAndSet(State.IDLE, State.MARK_BLOCK_CONFIRMATIONS_AWAITING)) {
-      pruningStrategy.prepare();
       markBlockNumber = blockNumber;
     } else if (blockNumber >= markBlockNumber + blockConfirmations
         && state.compareAndSet(State.MARK_BLOCK_CONFIRMATIONS_AWAITING, State.MARKING)) {
@@ -87,7 +90,6 @@ private void handleNewBlock(final BlockAddedEvent event) {
   }
 
   private void mark(final BlockHeader header) {
-    markBlockNumber = header.getNumber();
     final Hash stateRoot = header.getStateRoot();
     LOG.debug(
         "Begin marking used nodes for pruning. Block number: {} State root: {}",
@@ -117,6 +119,7 @@ private void execute(final Runnable action) {
       executorService.execute(action);
     } catch (final Throwable t) {
       LOG.error("Pruning failed", t);
+      pruningStrategy.cleanup();
       state.set(State.IDLE);
     }
   }
```

### ethereum/eth/src/main/java/org/hyperledger/besu/ethereum/eth/sync/DefaultSynchronizer.java
```diff
@@ -170,8 +170,8 @@ private void handleFastSyncResult(final FastSyncState result, final Throwable er
   }
 
   private void startFullSync() {
-    fullSyncDownloader.start();
     maybePruner.ifPresent(Pruner::start);
+    fullSyncDownloader.start();
   }
 
   @Override
```
