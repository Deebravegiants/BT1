# [?] World state halt and chain halt fixes (#7027)

## Summary
Severity: Unknown
Chain: Ethereum
Component: besu-eth/besu
Published: 2024-05-03
Source: https://github.com/besu-eth/besu/commit/bbbfc4c822e27565eb514ffae51e5b42acd98072
Type: security-commit

## Details
World state halt and chain halt fixes (#7027)

Signed-off-by: Jason Frame <jason.frame@consensys.net>
Signed-off-by: stefan.pingel@consensys.net <stefan.pingel@consensys.net>

## Patch
### CHANGELOG.md
```diff
@@ -55,6 +55,7 @@
 - Snap client fixes discovered during snap server testing [#6847](https://github.com/hyperledger/besu/pull/6847)
 - Correctly initialize the txpool as disabled on creation [#6890](https://github.com/hyperledger/besu/pull/6890)
 - Fix worldstate download halt when using snap sync during initial sync [#6981](https://github.com/hyperledger/besu/pull/6981)
+- Fix chain halt due to peers only partially responding with headers. And worldstate halts caused by a halt in the chain sync [#7027](https://github.com/hyperledger/besu/pull/7027)
 
 ### Download Links
 
```

### besu/src/main/java/org/hyperledger/besu/cli/options/unstable/SynchronizerOptions.java
```diff
@@ -39,6 +39,8 @@ public class SynchronizerOptions implements CLIOptions<SynchronizerConfiguration
       "--Xsynchronizer-downloader-header-request-size";
   private static final String DOWNLOADER_CHECKPOINT_TIMEOUTS_PERMITTED_FLAG =
       "--Xsynchronizer-downloader-checkpoint-timeouts-permitted";
+  private static final String DOWNLOADER_CHECKPOINT_RETRIES_FLAG =
+      "--Xsynchronizer-downloader-checkpoint-RETRIES";
   private static final String DOWNLOADER_CHAIN_SEGMENT_SIZE_FLAG =
       "--Xsynchronizer-downloader-chain-segment-size";
   private static final String DOWNLOADER_PARALLELISM_FLAG =
@@ -132,12 +134,12 @@ public void parseBlockPropagationRange(final String arg) {
       SynchronizerConfiguration.DEFAULT_DOWNLOADER_HEADER_REQUEST_SIZE;
 
   @CommandLine.Option(
-      names = DOWNLOADER_CHECKPOINT_TIMEOUTS_PERMITTED_FLAG,
+      names = {DOWNLOADER_CHECKPOINT_RETRIES_FLAG, DOWNLOADER_CHECKPOINT_TIMEOUTS_PERMITTED_FLAG},
       hidden = true,
       paramLabel = "<INTEGER>",
       description =
           "Number of tries to attempt to download checkpoints before stopping (default: ${DEFAULT-VALUE})")
-  private int downloaderCheckpointTimeoutsPermitted =
+  private int downloaderCheckpointRetries =
       SynchronizerConfiguration.DEFAULT_DOWNLOADER_CHECKPOINT_TIMEOUTS_PERMITTED;
 
   @CommandLine.Option(
@@ -354,8 +356,7 @@ public static SynchronizerOptions fromConfig(final SynchronizerConfiguration con
         config.getDownloaderChangeTargetThresholdByHeight();
     options.downloaderChangeTargetThresholdByTd = config.getDownloaderChangeTargetThresholdByTd();
     options.downloaderHeaderRequestSize = config.getDownloaderHeaderRequestSize();
-    options.downloaderCheckpointTimeoutsPermitted =
-        config.getDownloaderCheckpointTimeoutsPermitted();
+    options.downloaderCheckpointRetries = config.getDownloaderCheckpointRetries();
     options.downloaderChainSegmentSize = config.getDownloaderChainSegmentSize();
     options.downloaderParallelism = config.getDownloaderParallelism();
     options.transactionsParallelism = config.getTransactionsParallelism();
@@ -394,7 +395,7 @@ public SynchronizerConfiguration.Builder toDomainObject() {
     builder.downloaderChangeTargetThresholdByHeight(downloaderChangeTargetThresholdByHeight);
     builder.downloaderChangeTargetThresholdByTd(downloaderChangeTargetThresholdByTd);
     builder.downloaderHeadersRequestSize(downloaderHeaderRequestSize);
-    builder.downloaderCheckpointTimeoutsPermitted(downloaderCheckpointTimeoutsPermitted);
+    builder.downloaderCheckpointRetries(downloaderCheckpointRetries);
     builder.downloaderChainSegmentSize(downloaderChainSegmentSize);
     builder.downloaderParallelism(downloaderParallelism);
     builder.transactionsParallelism(transactionsParallelism);
@@ -436,7 +437,7 @@ public List<String> getCLIOptions() {
             DOWNLOADER_HEADER_REQUEST_SIZE_FLAG,
             OptionParser.format(downloaderHeaderRequestSize),
             DOWNLOADER_CHECKPOINT_TIMEOUTS_PERMITTED_FLAG,
-            OptionParser.format(downloaderCheckpointTimeoutsPermitted),
+            OptionParser.format(downloaderCheckpointRetries),
             DOWNLOADER_CHAIN_SEGMENT_SIZE_FLAG,
             OptionParser.format(downloaderChainSegmentSize),
             DOWNLOADER_PARALLELISM_FLAG,
```

### besu/src/test/java/org/hyperledger/besu/cli/options/SynchronizerOptionsTest.java
```diff
@@ -60,7 +60,7 @@ protected SynchronizerConfiguration.Builder createCustomizedDomainObject() {
             SynchronizerConfiguration.DEFAULT_DOWNLOADER_CHANGE_TARGET_THRESHOLD_BY_TD.add(2L))
         .downloaderHeadersRequestSize(
             SynchronizerConfiguration.DEFAULT_DOWNLOADER_HEADER_REQUEST_SIZE + 2)
-        .downloaderCheckpointTimeoutsPermitted(
+        .downloaderCheckpointRetries(
             SynchronizerConfiguration.DEFAULT_DOWNLOADER_CHECKPOINT_TIMEOUTS_PERMITTED + 2)
         .downloaderChainSegmentSize(
             SynchronizerConfiguration.DEFAULT_DOWNLOADER_CHAIN_SEGMENT_SIZE + 2)
```

### ethereum/eth/src/main/java/org/hyperledger/besu/ethereum/eth/sync/SynchronizerConfiguration.java
```diff
@@ -77,7 +77,7 @@ public class SynchronizerConfiguration {
   private final long downloaderChangeTargetThresholdByHeight;
   private final UInt256 downloaderChangeTargetThresholdByTd;
   private final int downloaderHeaderRequestSize;
-  private final int downloaderCheckpointTimeoutsPermitted;
+  private final int downloaderCheckpointRetries;
   private final int downloaderChainSegmentSize;
   private final int downloaderParallelism;
   private final int transactionsParallelism;
@@ -101,7 +101,7 @@ private SynchronizerConfiguration(
       final long downloaderChangeTargetThresholdByHeight,
       final UInt256 downloaderChangeTargetThresholdByTd,
       final int downloaderHeaderRequestSize,
-      final int downloaderCheckpointTimeoutsPermitted,
+      final int downloaderCheckpointRetries,
       final int downloaderChainSegmentSize,
       final int downloaderParallelism,
       final int transactionsParallelism,
@@ -123,7 +123,7 @@ private SynchronizerConfiguration(
     this.downloaderChangeTargetThresholdByHeight = downloaderChangeTargetThresholdByHeight;
     this.downloaderChangeTargetThresholdByTd = downloaderChangeTargetThresholdByTd;
     this.downloaderHeaderRequestSize = downloaderHeaderRequestSize;
-    this.downloaderCheckpointTimeoutsPermitted = downloaderCheckpointTimeoutsPermitted;
+    this.downloaderCheckpointRetries = downloaderCheckpointRetries;
     this.downloaderChainSegmentSize = downloaderChainSegmentSize;
     this.downloaderParallelism = downloaderParallelism;
     this.transactionsParallelism = transactionsParallelism;
@@ -191,8 +191,8 @@ public int getDownloaderHeaderRequestSize() {
     return downloaderHeaderRequestSize;
   }
 
-  public int getDownloaderCheckpointTimeoutsPermitted() {
-    return downloaderCheckpointTimeoutsPermitted;
+  public int getDownloaderCheckpointRetries() {
+    return downloaderCheckpointRetries;
   }
 
   public int getDownloaderChainSegmentSize() {
@@ -264,8 +264,7 @@ public static class Builder {
     private UInt256 downloaderChangeTargetThresholdByTd =
         DEFAULT_DOWNLOADER_CHANGE_TARGET_THRESHOLD_BY_TD;
     private int downloaderHeaderRequestSize = DEFAULT_DOWNLOADER_HEADER_REQUEST_SIZE;
-    private int downloaderCheckpointTimeoutsPermitted =
-        DEFAULT_DOWNLOADER_CHECKPOINT_TIMEOUTS_PERMITTED;
+    private int downloaderCheckpointRetries = DEFAULT_DOWNLOADER_CHECKPOINT_TIMEOUTS_PERMITTED;
     private SnapSyncConfiguration snapSyncConfiguration = SnapSyncConfiguration.getDefault();
     private int downloaderChainSegmentSize = DEFAULT_DOWNLOADER_CHAIN_SEGMENT_SIZE;
     private int downloaderParallelism = DEFAULT_DOWNLOADER_PARALLELISM;
@@ -327,9 +326,8 @@ public Builder downloaderHeadersRequestSize(final int downloaderHeaderRequestSiz
       return this;
     }
 
-    public Builder downloaderCheckpointTimeoutsPermitted(
-        final int downloaderCheckpointTimeoutsPermitted) {
-      this.downloaderCheckpointTimeoutsPermitted = downloaderCheckpointTimeoutsPermitted;
+    public Builder downloaderCheckpointRetries(final int downloaderCheckpointRetries) {
+      this.downloaderCheckpointRetries = downloaderCheckpointRetries;
       return this;
     }
 
@@ -422,7 +420,7 @@ public SynchronizerConfiguration build() {
           downloaderChangeTargetThresholdByHeight,
           downloaderChangeTargetThresholdByTd,
           downloaderHeaderRequestSize,
-          downloaderCheckpointTimeoutsPermitted,
+          downloaderCheckpointRetries,
           downloaderChainSegmentSize,
           downloaderParallelism,
           transactionsParallelism,
```

### ethereum/eth/src/main/java/org/hyperledger/besu/ethereum/eth/sync/fastsync/FastSyncDownloadPipelineFactory.java
```diff
@@ -125,7 +125,7 @@ public Pipeline<SyncTargetRange> createDownloadPipelineForSyncTarget(final SyncT
             ethContext.getScheduler(),
             target.peer(),
             getCommonAncestor(target),
-            syncConfig.getDownloaderCheckpointTimeoutsPermitted(),
+            syncConfig.getDownloaderCheckpointRetries(),
             SyncTerminationCondition.never());
     final DownloadHeadersStep downloadHeadersStep =
         new DownloadHeadersStep(
```

### ethereum/eth/src/main/java/org/hyperledger/besu/ethereum/eth/sync/fastsync/PivotSelectorFromSafeBlock.java
```diff
@@ -28,6 +28,7 @@
 
 import java.util.Optional;
 import java.util.concurrent.CompletableFuture;
+import java.util.concurrent.TimeUnit;
 import java.util.function.Supplier;
 
 import org.slf4j.Logger;
@@ -127,7 +128,7 @@ public long getBestChainHeight() {
                                           maybeCachedHeadBlockHeader = Optional.of(blockHeader);
                                           return blockHeader.getNumber();
                                         })
-                                    .get();
+                                    .get(20, TimeUnit.SECONDS);
                               } catch (Throwable t) {
                                 LOG.debug(
                                     "Error trying to download chain head block header by hash {}",
```

### ethereum/eth/src/main/java/org/hyperledger/besu/ethereum/eth/sync/fullsync/FullSyncDownloadPipelineFactory.java
```diff
@@ -91,7 +91,7 @@ public Pipeline<?> createDownloadPipelineForSyncTarget(final SyncTarget target)
             ethContext.getScheduler(),
             target.peer(),
             target.commonAncestor(),
-            syncConfig.getDownloaderCheckpointTimeoutsPermitted(),
+            syncConfig.getDownloaderCheckpointRetries(),
             fullSyncTerminationCondition);
     final DownloadHeadersStep downloadHeadersStep =
         new DownloadHeadersStep(
```

### ethereum/eth/src/main/java/org/hyperledger/besu/ethereum/eth/sync/range/SyncTargetRangeSource.java
```diff
@@ -22,6 +22,7 @@
 import org.hyperledger.besu.ethereum.eth.manager.EthPeer;
 import org.hyperledger.besu.ethereum.eth.manager.EthScheduler;
 import org.hyperledger.besu.ethereum.eth.sync.fullsync.SyncTerminationCondition;
+import org.hyperledger.besu.ethereum.p2p.rlpx.wire.messages.DisconnectMessage;
 
 import java.time.Duration;
 import java.util.ArrayDeque;
@@ -44,31 +45,31 @@ public class SyncTargetRangeSource implements Iterator<SyncTargetRange> {
   private final SyncTargetChecker syncTargetChecker;
   private final EthPeer peer;
   private final EthScheduler ethScheduler;
-  private final int rangeTimeoutsPermitted;
+  private final int retriesPermitted;
   private final Duration newHeaderWaitDuration;
   private final SyncTerminationCondition terminationCondition;
 
   private final Queue<SyncTargetRange> retrievedRanges = new ArrayDeque<>();
   private BlockHeader lastRangeEnd;
   private boolean reachedEndOfRanges = false;
   private Optional<CompletableFuture<List<BlockHeader>>> pendingRequests = Optional.empty();
-  private int requestFailureCount = 0;
+  private int retryCount = 0;
 
   public SyncTargetRangeSource(
       final RangeHeadersFetcher fetcher,
       final SyncTargetChecker syncTargetChecker,
       final EthScheduler ethScheduler,
       final EthPeer peer,
       final BlockHeader commonAncestor,
-      final int rangeTimeoutsPermitted,
+      final int retriesPermitted,
       final SyncTerminationCondition terminationCondition) {
     this(
         fetcher,
         syncTargetChecker,
         ethScheduler,
         peer,
         commonAncestor,
-        rangeTimeoutsPermitted,
+        retriesPermitted,
         Duration.ofSeconds(5),
         terminationCondition);
   }
@@ -79,15 +80,15 @@ public SyncTargetRangeSource(
       final EthScheduler ethScheduler,
       final EthPeer peer,
       final BlockHeader commonAncestor,
-      final int rangeTimeoutsPermitted,
+      final int retriesPermitted,
       final Duration newHeaderWaitDuration,
       final SyncTerminationCondition terminationCondition) {
     this.fetcher = fetcher;
     this.syncTargetChecker = syncTargetChecker;
     this.ethScheduler = ethScheduler;
     this.peer = peer;
     this.lastRangeEnd = commonAncestor;
-    this.rangeTimeoutsPermitted = rangeTimeoutsPermitted;
+    this.retriesPermitted = retriesPermitted;
     this.newHeaderWaitDuration = newHeaderWaitDuration;
     this.terminationCondition = terminationCondition;
   }
@@ -96,7 +97,7 @@ public SyncTargetRangeSource(
   public boolean hasNext() {
     return terminationCondition.shouldContinueDownload()
         && (!retrievedRanges.isEmpty()
-            || (requestFailureCount < rangeTimeoutsPermitted
+            || (retryCount < retriesPermitted
                 && syncTargetChecker.shouldContinueDownloadingFromSyncTarget(peer, lastRangeEnd)
                 && !reachedEndOfRanges));
   }
@@ -148,13 +149,21 @@ private SyncTargetRange getRangeFromPendingRequest() {
           pendingRequest.get(newHeaderWaitDuration.toMillis(), MILLISECONDS);
       this.pendingRequests = Optional.empty();
       if (newHeaders.isEmpty()) {
-        requestFailureCount++;
+        retryCount++;
+        if (retryCount >= retriesPermitted) {
+          LOG.atDebug()
+              .setMessage(
+                  "Disconnecting target peer for providing useless or empty range header: {}.")
+              .addArgument(peer)
+              .log();
+          peer.disconnect(DisconnectMessage.DisconnectReason.USELESS_PEER_USELESS_RESPONSES);
+        }
       } else {
-        requestFailureCount = 0;
-      }
-      for (final BlockHeader header : newHeaders) {
-        retrievedRanges.add(new SyncTargetRange(peer, lastRangeEnd, header));
-        lastRangeEnd = header;
+        retryCount = 0;
+        for (final BlockHeader header : newHeaders) {
+          retrievedRanges.add(new SyncTargetRange(peer, lastRangeEnd, header));
+          lastRangeEnd = header;
+        }
       }
       return retrievedRanges.poll();
     } catch (final InterruptedException e) {
@@ -163,7 +172,7 @@ private SyncTargetRange getRangeFromPendingRequest() {
     } catch (final ExecutionException e) {
       LOG.debug("Failed to retrieve new range headers", e);
       this.pendingRequests = Optional.empty();
-      requestFailureCount++;
+      retryCount++;
       return null;
     } catch (final TimeoutException e) {
       return null;
```

### ethereum/eth/src/main/java/org/hyperledger/besu/ethereum/eth/sync/snapsync/DynamicPivotBlockSelector.java
```diff
@@ -161,7 +161,7 @@ private CompletableFuture<Void> downloadNewPivotBlock(final FastSyncState fss) {
                   .addArgument(this::logLastPivotBlockFound)
                   .log();
             })
-        .orTimeout(5, TimeUnit.MINUTES);
+        .orTimeout(20, TimeUnit.SECONDS);
   }
 
   private boolean isSamePivotBlock(final FastSyncState fss) {
```

### ethereum/eth/src/main/java/org/hyperledger/besu/ethereum/eth/sync/snapsync/SnapWorldDownloadState.java
```diff
@@ -21,6 +21,7 @@
 import org.hyperledger.besu.ethereum.chain.BlockAddedObserver;
 import org.hyperledger.besu.ethereum.chain.Blockchain;
 import org.hyperledger.besu.ethereum.core.BlockHeader;
+import org.hyperledger.besu.ethereum.eth.manager.EthContext;
 import org.hyperledger.besu.ethereum.eth.sync.snapsync.context.SnapSyncStatePersistenceManager;
 import org.hyperledger.besu.ethereum.eth.sync.snapsync.request.AccountRangeDataRequest;
 import org.hyperledger.besu.ethereum.eth.sync.snapsync.request.BytecodeRequest;
@@ -86,6 +87,7 @@ public class SnapWorldDownloadState extends WorldDownloadState<SnapDataRequest>
   // blockchain
   private final Blockchain blockchain;
   private final Long blockObserverId;
+  private final EthContext ethContext;
 
   // metrics around the snapsync
   private final SnapSyncMetricsManager metricsManager;
@@ -99,7 +101,8 @@ public SnapWorldDownloadState(
       final int maxRequestsWithoutProgress,
       final long minMillisBeforeStalling,
       final SnapSyncMetricsManager metricsManager,
-      final Clock clock) {
+      final Clock clock,
+      final EthContext ethContext) {
     super(
         worldStateStorageCoordinator,
         pendingRequests,
@@ -111,6 +114,7 @@ public SnapWorldDownloadState(
     this.snapSyncState = snapSyncState;
     this.metricsManager = metricsManager;
     this.blockObserverId = blockchain.observeBlockAdded(createBlockchainObserver());
+    this.ethContext = ethContext;
 
     metricsManager
         .getMetricsSystem()
@@ -423,23 +427,29 @@ public void setPivotBlockSelector(final DynamicPivotBlockSelector pivotBlockSele
   }
 
   public BlockAddedObserver createBlockchainObserver() {
-    return addedBlockContext -> {
-      final AtomicBoolean foundNewPivotBlock = new AtomicBoolean(false);
-      pivotBlockSelector.check(
-          (____, isNewPivotBlock) -> {
-            if (isNewPivotBlock) {
-              foundNewPivotBlock.set(true);
-            }
-          });
-
-      final boolean isNewPivotBlockFound = foundNewPivotBlock.get();
-      final boolean isBlockchainCaughtUp =
-          snapSyncState.isWaitingBlockchain() && !pivotBlockSelector.isBlockchainBehind();
-
-      if (snapSyncState.isHealTrieInProgress() && (isNewPivotBlockFound || isBlockchainCaughtUp)) {
-        snapSyncState.setWaitingBlockchain(false);
-        reloadTrieHeal();
-      }
-    };
+    return addedBlockContext ->
+        ethContext
+            .getScheduler()
+            .executeServiceTask(
+                () -> {
+                  final AtomicBoolean foundNewPivotBlock = new AtomicBoolean(false);
+                  pivotBlockSelector.check(
+                      (____, isNewPivotBlock) -> {
+                        if (isNewPivotBlock) {
+                          foundNewPivotBlock.set(true);
+                        }
+                      });
+
+                  final boolean isNewPivotBlockFound = foundNewPivotBlock.get();
+                  final boolean isBlockchainCaughtUp =
+                      snapSyncState.isWaitingBlockchain()
+                          && !pivotBlockSelector.isBlockchainBehind();
+
+                  if (snapSyncState.isHealTrieInProgress()
+                      && (isNewPivotBlockFound || isBlockchainCaughtUp)) {
+                    snapSyncState.setWaitingBlockchain(false);
+                    reloadTrieHeal();
+                  }
+                });
   }
 }
```

### ethereum/eth/src/main/java/org/hyperledger/besu/ethereum/eth/sync/snapsync/SnapWorldStateDownloadProcess.java
```diff
@@ -15,6 +15,7 @@
 package org.hyperledger.besu.ethereum.eth.sync.snapsync;
 
 import static com.google.common.base.Preconditions.checkNotNull;
+import static org.hyperledger.besu.ethereum.eth.sync.snapsync.DynamicPivotBlockSelector.doNothingOnPivotChange;
 import static org.hyperledger.besu.services.pipeline.PipelineBuilder.createPipelineFrom;
 
 import org.hyperledger.besu.ethereum.eth.manager.EthScheduler;
@@ -158,12 +159,19 @@ public static class Builder {
     private SnapSyncProcessState snapSyncState;
     private PersistDataStep persistDataStep;
     private CompleteTaskStep completeTaskStep;
+    private DynamicPivotBlockSelector pivotBlockManager;
 
     public Builder configuration(final SnapSyncConfiguration snapSyncConfiguration) {
       this.snapSyncConfiguration = snapSyncConfiguration;
       return this;
     }
 
+    public Builder dynamicPivotBlockSelector(
+        final DynamicPivotBlockSelector dynamicPivotBlockSelector) {
+      this.pivotBlockManager = dynamicPivotBlockSelector;
+      return this;
+    }
+
     public Builder maxOutstandingRequests(final int maxOutstandingRequests) {
       this.maxOutstandingRequests = maxOutstandingRequests;
       return this;
@@ -257,6 +265,12 @@ public SnapWorldStateDownloadProcess build() {
                   outputCounter,
                   true,
                   "world_state_download")
+              .thenProcess(
+                  "checkNewPivotBlock-Account",
+                  tasks -> {
+                    pivotBlockManager.check(doNothingOnPivotChange);
+                    return tasks;
+                  })
               .thenProcessAsync(
                   "batchDownloadAccountData",
                   requestTask -> requestDataStep.requestAccount(requestTask),
@@ -274,6 +288,12 @@ public SnapWorldStateDownloadProcess build() {
                   true,
                   "world_state_download")
               .inBatches(snapSyncConfiguration.getStorageCountPerRequest())
+              .thenProcess(
+                  "checkNewPivotBlock-Storage",
+                  tasks -> {
+                    pivotBlockManager.check(doNothingOnPivotChange);
+                    return tasks;
+                  })
               .thenProcessAsyncOrdered(
                   "batchDownloadStorageData",
                   requestTask -> requestDataStep.requestStorage(requestTask),
@@ -294,6 +314,12 @@ public SnapWorldStateDownloadProcess build() {
                   outputCounter,
                   true,
                   "world_state_download")
+              .thenProcess(
+                  "checkNewPivotBlock-LargeStorage",
+                  tasks -> {
+                    pivotBlockManager.check(doNothingOnPivotChange);
+                    return tasks;
+                  })
               .thenProcessAsyncOrdered(
                   "batchDownloadLargeStorageData",
                   requestTask -> requestDataStep.requestStorage(List.of(requestTask)),
@@ -328,6 +354,14 @@ public SnapWorldStateDownloadProcess build() {
                                   .map(BytecodeRequest::getCodeHash)
                                   .distinct()
                                   .count())
+              .thenProcess(
+                  "checkNewPivotBlock-Code",
+                  tasks -> {
+                    pivotBlockManager.check(
+                        (blockHeader, newBlockFound) ->
+                            reloadHealWhenNeeded(snapSyncState, downloadState, newBlockFound));
+                    return tasks;
+                  })
               .thenProcessAsyncOrdered(
                   "batchDownloadCodeData",
                   tasks -> requestDataStep.requestCode(tasks),
@@ -356,6 +390,14 @@ public SnapWorldStateDownloadProcess build() {
                   3,
                   bufferCapacity)
               .inBatches(snapSyncConfiguration.getTrienodeCountPerRequest())
+              .thenProcess(
+                  "checkNewPivotBlock-TrieNode",
+                  tasks -> {
+                    pivotBlockManager.check(
+                        (blockHeader, newBlockFound) ->
+                            reloadHealWhenNeeded(snapSyncState, downloadState, newBlockFound));
+                    return tasks;
+                  })
               .thenProcessAsync(
                   "batchDownloadTrieNodeData",
                   tasks -> requestDataStep.requestTrieNodeByPath(tasks),
@@ -419,4 +461,13 @@ public SnapWorldStateDownloadProcess build() {
           requestsToComplete);
     }
   }
+
+  private static void reloadHealWhenNeeded(
+      final SnapSyncProcessState snapSyncState,
+      final SnapWorldDownloadState downloadState,
+      final boolean newBlockFound) {
+    if (snapSyncState.isHealTrieInProgress() && newBlockFound) {
+      downloadState.reloadTrieHeal();
+    }
+  }
 }
```

### ethereum/eth/src/main/java/org/hyperledger/besu/ethereum/eth/sync/snapsync/SnapWorldStateDownloader.java
```diff
@@ -147,7 +147,8 @@ public CompletableFuture<Void> run(
               maxNodeRequestsWithoutProgress,
               minMillisBeforeStalling,
               snapsyncMetricsManager,
-              clock);
+              clock,
+              ethContext);
 
       final Map<Bytes32, Bytes32> ranges = RangeManager.generateAllRanges(16);
       snapsyncMetricsManager.initRange(ranges);
@@ -214,6 +215,7 @@ public CompletableFuture<Void> run(
           SnapWorldStateDownloadProcess.builder()
               .configuration(snapSyncConfiguration)
               .maxOutstandingRequests(maxOutstandingRequests)
+              .dynamicPivotBlockSelector(dynamicPivotBlockManager)
               .loadLocalDataStep(
                   new LoadLocalDataStep(
                       worldStateStorageCoordinator,
```
