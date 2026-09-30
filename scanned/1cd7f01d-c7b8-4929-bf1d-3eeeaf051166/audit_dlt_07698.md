# [?] Fixes: GHSA-pcv4-pxhv-99m7 Cap concurrent snap/1-2 GET_* requests scheduled onto EthScheduler (#11101)

## Summary
Severity: Unknown
Chain: Ethereum
Component: besu-eth/besu
Published: 2026-08-21
Source: https://github.com/besu-eth/besu/commit/683880baa609111e6fee47ef1122dce7a76a154b
Type: security-commit

## Details
Fixes: GHSA-pcv4-pxhv-99m7 Cap concurrent snap/1-2 GET_* requests scheduled onto EthScheduler (#11101)

Signed-off-by: Sally MacFarlane <macfarla.github@gmail.com>

## Patch
### CHANGELOG.md
```diff
@@ -69,6 +69,7 @@
 
 ### Bug fixes
 - Bound the DiscV4 inbound packet pipeline with an admission gate (256 in-flight packets) and a bounded crypto executor queue, preventing a UDP flood from exhausting memory.
+- Cap the number of snap/1-2 GET_* requests concurrently scheduled for processing on a snap-serving node, both per-peer (--Xsnapsync-server-max-concurrent-requests-per-peer, default 8) and globally (--Xsnapsync-server-max-concurrent-requests, default 200). [#11101](https://github.com/besu-eth/besu/pull/11101)
 - Cap the QBFT/IBFT round change number to prevent unbounded memory growth from malformed round-change messages.
 - Cap pre-STATUS RLPx connections and close them on eviction to prevent resource exhaustion.
 - Improve logging for malformed discv4 UDP packets.
```

### app/src/main/java/org/hyperledger/besu/cli/options/SynchronizerOptions.java
```diff
@@ -101,6 +101,12 @@ public class SynchronizerOptions implements CLIOptions<SynchronizerConfiguration
   private static final String SNAP_FLAT_STORAGE_HEALED_COUNT_PER_REQUEST_FLAG =
       "--Xsnapsync-synchronizer-flat-slot-healed-count-per-request";
 
+  private static final String SNAP_SERVER_MAX_CONCURRENT_REQUESTS_PER_PEER_FLAG =
+      "--Xsnapsync-server-max-concurrent-requests-per-peer";
+
+  private static final String SNAP_SERVER_MAX_CONCURRENT_REQUESTS_FLAG =
+      "--Xsnapsync-server-max-concurrent-requests";
+
   private static final String CHECKPOINT_POST_MERGE_FLAG = "--Xcheckpoint-post-merge-enabled";
 
   private static final String SNAP_SYNC_SAVE_PRE_CHECKPOINT_HEADERS_ONLY_FLAG =
@@ -388,6 +394,24 @@ public void parseBlockPropagationRange(final String arg) {
           "Enable advertising the snap/2 protocol capability. (default: ${DEFAULT-VALUE})")
   private Boolean snap2Enabled = SnapSyncConfiguration.DEFAULT_SNAP2_ENABLED;
 
+  @CommandLine.Option(
+      names = SNAP_SERVER_MAX_CONCURRENT_REQUESTS_PER_PEER_FLAG,
+      hidden = true,
+      paramLabel = "<INTEGER>",
+      description =
+          "Maximum number of snap sync GET_* requests from a single peer that may be concurrently scheduled for processing. 0 specifies no limit (default: ${DEFAULT-VALUE})")
+  private int snapsyncServerMaxConcurrentRequestsPerPeer =
+      SnapSyncConfiguration.DEFAULT_MAX_CONCURRENT_SNAP_REQUESTS_PER_PEER;
+
+  @CommandLine.Option(
+      names = SNAP_SERVER_MAX_CONCURRENT_REQUESTS_FLAG,
+      hidden = true,
+      paramLabel = "<INTEGER>",
+      description =
+          "Maximum total number of snap sync GET_* requests, across all peers, that may be concurrently scheduled for processing. 0 specifies no limit (default: ${DEFAULT-VALUE})")
+  private int snapsyncServerMaxConcurrentRequests =
+      SnapSyncConfiguration.DEFAULT_MAX_CONCURRENT_SNAP_REQUESTS_GLOBAL;
+
   @SuppressWarnings("unused")
   @CommandLine.Option(
       names = {CHECKPOINT_POST_MERGE_FLAG},
@@ -516,6 +540,10 @@ public static SynchronizerOptions fromConfig(final SynchronizerConfiguration con
         config.getSnapSyncConfiguration().getLocalFlatStorageCountToHealPerRequest();
     options.snapsyncServerEnabled = config.getSnapSyncConfiguration().isSnapServerEnabled();
     options.snap2Enabled = config.getSnapSyncConfiguration().isSnap2Enabled();
+    options.snapsyncServerMaxConcurrentRequestsPerPeer =
+        config.getSnapSyncConfiguration().getMaxConcurrentSnapRequestsPerPeer();
+    options.snapsyncServerMaxConcurrentRequests =
+        config.getSnapSyncConfiguration().getMaxConcurrentSnapRequestsGlobal();
     options.snapTransactionIndexingEnabled =
         config.getSnapSyncConfiguration().isSnapSyncTransactionIndexingEnabled();
     options.era1ImportPrepipelineEnabled = config.era1ImportPrepipelineEnabled();
@@ -560,6 +588,8 @@ public SynchronizerConfiguration.Builder toDomainObject() {
             .localFlatStorageCountToHealPerRequest(snapsyncFlatStorageHealedCountPerRequest)
             .isSnapServerEnabled(snapsyncServerEnabled)
             .isSnap2Enabled(snap2Enabled)
+            .maxConcurrentSnapRequestsPerPeer(snapsyncServerMaxConcurrentRequestsPerPeer)
+            .maxConcurrentSnapRequestsGlobal(snapsyncServerMaxConcurrentRequests)
             .isSnapSyncTransactionIndexingEnabled(snapTransactionIndexingEnabled)
             .build());
     builder.receiptsDownloadStepTimeoutMillis(receiptsDownloadStepTimeoutMillis);
@@ -633,6 +663,10 @@ public List<String> getCLIOptions() {
             OptionParser.format(snapsyncServerEnabled),
             SNAP2_ENABLED_FLAG,
             OptionParser.format(snap2Enabled),
+            SNAP_SERVER_MAX_CONCURRENT_REQUESTS_PER_PEER_FLAG,
+            OptionParser.format(snapsyncServerMaxConcurrentRequestsPerPeer),
+            SNAP_SERVER_MAX_CONCURRENT_REQUESTS_FLAG,
+            OptionParser.format(snapsyncServerMaxConcurrentRequests),
             SNAP_TRANSACTION_INDEXING_ENABLED_FLAG,
             OptionParser.format(snapTransactionIndexingEnabled),
             ERA1_IMPORT_PREPIPELINE_ENABLED_FLAG,
```

### app/src/main/java/org/hyperledger/besu/controller/BesuControllerBuilder.java
```diff
@@ -1425,7 +1425,8 @@ private Optional<SnapProtocolManager> createSnapProtocolManager(
             snapMessages,
             ethScheduler,
             protocolContext,
-            synchronizer));
+            synchronizer,
+            metricsSystem));
   }
 
   WorldStateArchive createWorldStateArchive(
```

### ethereum/eth/src/main/java/org/hyperledger/besu/ethereum/eth/manager/snap/SnapProtocolManager.java
```diff
@@ -35,13 +35,18 @@
 import org.hyperledger.besu.ethereum.p2p.rlpx.wire.messages.DisconnectMessage.DisconnectReason;
 import org.hyperledger.besu.ethereum.rlp.RLPException;
 import org.hyperledger.besu.ethereum.worldstate.WorldStateStorageCoordinator;
+import org.hyperledger.besu.metrics.BesuMetricCategory;
+import org.hyperledger.besu.plugin.services.MetricsSystem;
+import org.hyperledger.besu.plugin.services.metrics.Counter;
 
 import java.math.BigInteger;
 import java.util.Comparator;
 import java.util.List;
 import java.util.Map;
 import java.util.Optional;
 import java.util.concurrent.CancellationException;
+import java.util.concurrent.ConcurrentHashMap;
+import java.util.concurrent.atomic.AtomicInteger;
 
 import com.google.common.collect.ImmutableList;
 import org.slf4j.Logger;
@@ -55,20 +60,41 @@ public class SnapProtocolManager implements ProtocolManager {
   private final EthMessages snapMessages;
   private final EthScheduler ethScheduler;
 
+  private final int maxConcurrentRequestsPerPeer;
+  private final int maxConcurrentRequestsGlobal;
+  private final AtomicInteger globalInFlightRequests = new AtomicInteger(0);
+  private final Map<PeerConnection, AtomicInteger> perPeerInFlightRequests =
+      new ConcurrentHashMap<>();
+  private final Counter rejectedRequestsCounter;
+
   public SnapProtocolManager(
       final WorldStateStorageCoordinator worldStateStorageCoordinator,
       final SnapSyncConfiguration snapConfig,
       final EthPeers ethPeers,
       final EthMessages snapMessages,
       final EthScheduler ethScheduler,
       final ProtocolContext protocolContext,
-      final Synchronizer synchronizer) {
+      final Synchronizer synchronizer,
+      final MetricsSystem metricsSystem) {
     this.ethPeers = ethPeers;
     this.snapMessages = snapMessages;
     this.ethScheduler = ethScheduler;
     this.supportedCapabilities = calculateCapabilities(snapConfig);
+    this.maxConcurrentRequestsPerPeer = snapConfig.getMaxConcurrentSnapRequestsPerPeer();
+    this.maxConcurrentRequestsGlobal = snapConfig.getMaxConcurrentSnapRequestsGlobal();
     new SnapServer(
         snapConfig, snapMessages, worldStateStorageCoordinator, protocolContext, synchronizer);
+
+    metricsSystem.createIntegerGauge(
+        BesuMetricCategory.PEERS,
+        "snap_service_requests_in_flight_current",
+        "The current number of snap sync GET_* requests concurrently scheduled for processing",
+        globalInFlightRequests::get);
+    this.rejectedRequestsCounter =
+        metricsSystem.createCounter(
+            BesuMetricCategory.PEERS,
+            "snap_service_requests_rejected_total",
+            "Total number of snap sync GET_* requests answered with an empty response because a concurrency cap was reached");
   }
 
   private List<Capability> calculateCapabilities(final SnapSyncConfiguration snapConfig) {
@@ -151,6 +177,54 @@ private void scheduleSnapRequest(
       final EthMessage decodedEthMessage,
       final Capability cap,
       final int code) {
+    if (!reserveSnapRequestSlot(ethPeer)) {
+      respondEmptyDueToOverload(ethPeer, decodedEthMessage, code);
+      return;
+    }
+    try {
+      scheduleReservedSnapRequest(ethPeer, decodedEthMessage, cap, code);
+    } catch (final RuntimeException e) {
+      // Only reachable during shutdown: the services executor rejects synchronously once shut
+      // down. Release the slot so it isn't leaked.
+      releaseSnapRequestSlot(ethPeer);
+      throw e;
+    }
+  }
+
+  /** Cap was hit; reply empty instead of leaving the peer to time out. */
+  private void respondEmptyDueToOverload(
+      final EthPeer ethPeer, final EthMessage decodedEthMessage, final int code) {
+    final BigInteger requestId;
+    try {
+      requestId = decodedEthMessage.getData().unwrapMessageData().getKey();
+    } catch (final RLPException e) {
+      LOG.debug(
+          "Received malformed snap message code={} (BREACH_OF_PROTOCOL), disconnecting: {}",
+          code,
+          ethPeer,
+          e);
+      ethPeer.disconnect(DisconnectReason.BREACH_OF_PROTOCOL_MALFORMED_MESSAGE_RECEIVED);
+      return;
+    }
+    sendSnapResponse(ethPeer, emptyResponseFor(code).wrapMessageData(requestId));
+  }
+
+  private static MessageData emptyResponseFor(final int code) {
+    return switch (code) {
+      case SnapV1.GET_ACCOUNT_RANGE -> SnapServer.EMPTY_ACCOUNT_RANGE;
+      case SnapV1.GET_STORAGE_RANGE -> SnapServer.EMPTY_STORAGE_RANGE;
+      case SnapV1.GET_BYTECODES -> SnapServer.EMPTY_BYTE_CODES_MESSAGE;
+      case SnapV1.GET_TRIE_NODES -> SnapServer.EMPTY_TRIE_NODES_MESSAGE;
+      case SnapV2.GET_BLOCK_ACCESS_LISTS -> SnapServer.EMPTY_BLOCK_ACCESS_LISTS;
+      default -> throw new IllegalStateException("Unhandled snap GET_* code: " + code);
+    };
+  }
+
+  private void scheduleReservedSnapRequest(
+      final EthPeer ethPeer,
+      final EthMessage decodedEthMessage,
+      final Capability cap,
+      final int code) {
     ethScheduler
         .scheduleServiceTask(
             () -> {
@@ -185,7 +259,61 @@ private void scheduleSnapRequest(
                     .log();
               }
               return null;
-            });
+            })
+        .whenComplete((result, error) -> releaseSnapRequestSlot(ethPeer));
+  }
+
+  /**
+   * Reserves a global and per-peer slot before scheduling; increment-then-check avoids a TOCTOU
+   * race.
+   *
+   * @return true if reserved; false if a cap was hit (request answered empty instead).
+   */
+  private boolean reserveSnapRequestSlot(final EthPeer ethPeer) {
+    if (maxConcurrentRequestsGlobal > 0) {
+      final int reservedGlobal = globalInFlightRequests.incrementAndGet();
+      if (reservedGlobal > maxConcurrentRequestsGlobal) {
+        globalInFlightRequests.decrementAndGet();
+        rejectSnapRequest(ethPeer, "global");
+        return false;
+      }
+    }
+    if (maxConcurrentRequestsPerPeer > 0) {
+      final AtomicInteger perPeerCount =
+          perPeerInFlightRequests.computeIfAbsent(
+              ethPeer.getConnection(), unused -> new AtomicInteger(0));
+      final int reservedPerPeer = perPeerCount.incrementAndGet();
+      if (reservedPerPeer > maxConcurrentRequestsPerPeer) {
+        perPeerCount.decrementAndGet();
+        if (maxConcurrentRequestsGlobal > 0) {
+          globalInFlightRequests.decrementAndGet();
+        }
+        rejectSnapRequest(ethPeer, "per-peer");
+        return false;
+      }
+    }
+    return true;
+  }
+
+  private void releaseSnapRequestSlot(final EthPeer ethPeer) {
+    if (maxConcurrentRequestsGlobal > 0) {
+      globalInFlightRequests.decrementAndGet();
+    }
+    if (maxConcurrentRequestsPerPeer > 0) {
+      final AtomicInteger perPeerCount = perPeerInFlightRequests.get(ethPeer.getConnection());
+      if (perPeerCount != null) {
+        perPeerCount.decrementAndGet();
+      }
+    }
+  }
+
+  private void rejectSnapRequest(final EthPeer ethPeer, final String scope) {
+    rejectedRequestsCounter.inc();
+    LOG.atDebug()
+        .setMessage("Answering snap request from peer {} empty: {} concurrency cap reached")
+        .addArgument(ethPeer::getLoggableId)
+        .addArgument(scope)
+        .log();
   }
 
   private void sendSnapResponse(final EthPeer ethPeer, final MessageData responseData) {
@@ -206,7 +334,9 @@ public void handleNewConnection(final PeerConnection connection) {}
   public void handleDisconnect(
       final PeerConnection connection,
       final DisconnectReason reason,
-      final boolean initiatedByPeer) {}
+      final boolean initiatedByPeer) {
+    perPeerInFlightRequests.remove(connection);
+  }
 
   @Override
   public int getHighestProtocolVersion() {
```

### ethereum/eth/src/main/java/org/hyperledger/besu/ethereum/eth/manager/snap/SnapServer.java
```diff
@@ -76,14 +76,16 @@ class SnapServer implements BesuEvents.InitialSyncCompletionListener {
   private static final int MAX_RESPONSE_SIZE = 2 * 1024 * 1024;
   private static final int MAX_CODE_LOOKUPS_PER_REQUEST = 1024;
   private static final int MAX_STORAGE_RANGE_ACCOUNTS_PER_REQUEST = 4096;
-  private static final AccountRangeMessage EMPTY_ACCOUNT_RANGE =
+  static final AccountRangeMessage EMPTY_ACCOUNT_RANGE =
       AccountRangeMessage.create(new HashMap<>(), new ArrayDeque<>());
-  private static final StorageRangeMessage EMPTY_STORAGE_RANGE =
+  static final StorageRangeMessage EMPTY_STORAGE_RANGE =
       StorageRangeMessage.create(new ArrayDeque<>(), Collections.emptyList());
-  private static final TrieNodesMessage EMPTY_TRIE_NODES_MESSAGE =
+  static final TrieNodesMessage EMPTY_TRIE_NODES_MESSAGE =
       TrieNodesMessage.create(new ArrayList<>());
-  private static final ByteCodesMessage EMPTY_BYTE_CODES_MESSAGE =
+  static final ByteCodesMessage EMPTY_BYTE_CODES_MESSAGE =
       ByteCodesMessage.create(new ArrayDeque<>());
+  static final BlockAccessListsMessage EMPTY_BLOCK_ACCESS_LISTS =
+      BlockAccessListsMessage.create(List.of());
 
   static final Hash HASH_LAST = Hash.wrap(Bytes32.leftPad(Bytes.fromHexString("FF"), (byte) 0xFF));
 
@@ -253,7 +255,7 @@ private void registerResponseConstructors() {
 
   MessageData constructGetBlockAccessListsResponse(final MessageData message) {
     if (!isStarted.get()) {
-      return BlockAccessListsMessage.create(List.of());
+      return EMPTY_BLOCK_ACCESS_LISTS;
     }
 
     final StopWatch stopWatch = StopWatch.createStarted();
```

### ethereum/eth/src/main/java/org/hyperledger/besu/ethereum/eth/sync/snapsync/SnapSyncConfiguration.java
```diff
@@ -49,6 +49,30 @@ public class SnapSyncConfiguration {
   public static final Boolean DEFAULT_SNAP_SERVER_ENABLED = Boolean.FALSE;
   public static final Boolean DEFAULT_SNAP2_ENABLED = Boolean.FALSE;
 
+  /**
+   * Default cap on the number of snap/1-2 GET_* requests from a single peer that may have a service
+   * task concurrently scheduled on the EthScheduler services pool. Sized with modest headroom above
+   * the number of outstanding requests we ourselves send a peer ({@code
+   * EthPeer.MAX_OUTSTANDING_REQUESTS = 5}). 0 disables the check.
+   */
+  public static final int DEFAULT_MAX_CONCURRENT_SNAP_REQUESTS_PER_PEER = 8;
+
+  /**
+   * Default cap on the total number of snap/1-2 GET_* requests, across all peers, that may have a
+   * service task concurrently scheduled on the EthScheduler services pool. Bounds worst-case
+   * native-thread/stack overhead from an unbounded fan-out of snap requests. 0 disables the check.
+   *
+   * <p>Sized as {@code DEFAULT_MAX_PEERS (25) * DEFAULT_MAX_CONCURRENT_SNAP_REQUESTS_PER_PEER (8) =
+   * 200}, so that a node running with the default peer count never has legitimate,
+   * per-peer-compliant traffic throttled by the global cap, regardless of how many requests any
+   * individual remote client implementation chooses to keep in flight to us -- the per-peer cap
+   * above already bounds that unconditionally, per peer, without relying on the remote client's own
+   * self-throttling behaviour (which varies across clients and isn't something this node can verify
+   * or trust). Operators who raise {@code --max-peers} well above the default should raise this
+   * value proportionally, since the two are not coupled at runtime.
+   */
+  public static final int DEFAULT_MAX_CONCURRENT_SNAP_REQUESTS_GLOBAL = 200;
+
   public static final Boolean DEFAULT_SNAP_SYNC_TRANSACTION_INDEXING_ENABLED = Boolean.FALSE;
   public static final Boolean DEFAULT_SNAP_SYNC_SAVE_PRE_MERGE_HEADERS_ONLY_ENABLED = Boolean.TRUE;
 
@@ -101,6 +125,16 @@ public Boolean isSnap2Enabled() {
     return DEFAULT_SNAP2_ENABLED;
   }
 
+  @Value.Default
+  public int getMaxConcurrentSnapRequestsPerPeer() {
+    return DEFAULT_MAX_CONCURRENT_SNAP_REQUESTS_PER_PEER;
+  }
+
+  @Value.Default
+  public int getMaxConcurrentSnapRequestsGlobal() {
+    return DEFAULT_MAX_CONCURRENT_SNAP_REQUESTS_GLOBAL;
+  }
+
   @Value.Default
   public Boolean isSnapSyncTransactionIndexingEnabled() {
     return DEFAULT_SNAP_SYNC_TRANSACTION_INDEXING_ENABLED;
```

### ethereum/eth/src/test/java/org/hyperledger/besu/ethereum/eth/manager/snap/SnapProtocolManagerTest.java
```diff
@@ -15,9 +15,16 @@
 package org.hyperledger.besu.ethereum.eth.manager.snap;
 
 import static org.assertj.core.api.Assertions.assertThat;
+import static org.assertj.core.api.Assertions.assertThatThrownBy;
 import static org.mockito.ArgumentMatchers.any;
+import static org.mockito.ArgumentMatchers.eq;
+import static org.mockito.Mockito.mock;
+import static org.mockito.Mockito.never;
+import static org.mockito.Mockito.times;
+import static org.mockito.Mockito.verify;
 import static org.mockito.Mockito.when;
 
+import org.hyperledger.besu.datatypes.Hash;
 import org.hyperledger.besu.ethereum.ProtocolContext;
 import org.hyperledger.besu.ethereum.core.Synchronizer;
 import org.hyperledger.besu.ethereum.eth.SnapProtocol;
@@ -26,18 +33,33 @@
 import org.hyperledger.besu.ethereum.eth.manager.EthPeers;
 import org.hyperledger.besu.ethereum.eth.manager.EthScheduler;
 import org.hyperledger.besu.ethereum.eth.manager.MockPeerConnection;
+import org.hyperledger.besu.ethereum.eth.messages.snap.GetTrieNodesMessage;
+import org.hyperledger.besu.ethereum.eth.messages.snap.SnapV1;
+import org.hyperledger.besu.ethereum.eth.messages.snap.TrieNodesMessage;
 import org.hyperledger.besu.ethereum.eth.sync.snapsync.SnapSyncConfiguration;
+import org.hyperledger.besu.ethereum.p2p.rlpx.connections.PeerConnection;
 import org.hyperledger.besu.ethereum.p2p.rlpx.wire.DefaultMessage;
+import org.hyperledger.besu.ethereum.p2p.rlpx.wire.Message;
+import org.hyperledger.besu.ethereum.p2p.rlpx.wire.MessageData;
 import org.hyperledger.besu.ethereum.p2p.rlpx.wire.RawMessage;
 import org.hyperledger.besu.ethereum.p2p.rlpx.wire.messages.DisconnectMessage.DisconnectReason;
 import org.hyperledger.besu.ethereum.worldstate.WorldStateStorageCoordinator;
+import org.hyperledger.besu.metrics.noop.NoOpMetricsSystem;
+import org.hyperledger.besu.plugin.services.MetricsSystem;
 
+import java.math.BigInteger;
+import java.util.ArrayList;
 import java.util.Collections;
 import java.util.HashSet;
+import java.util.List;
+import java.util.concurrent.CompletableFuture;
+import java.util.concurrent.RejectedExecutionException;
 
+import org.apache.tuweni.bytes.Bytes;
 import org.junit.jupiter.api.BeforeEach;
 import org.junit.jupiter.api.Test;
 import org.junit.jupiter.api.extension.ExtendWith;
+import org.mockito.ArgumentCaptor;
 import org.mockito.Mock;
 import org.mockito.junit.jupiter.MockitoExtension;
 import org.mockito.junit.jupiter.MockitoSettings;
@@ -55,6 +77,7 @@ class SnapProtocolManagerTest {
   @Mock private Synchronizer synchronizer;
   @Mock private EthScheduler ethScheduler;
   @Mock private EthPeer ethPeer;
+  private final MetricsSystem metricsSystem = new NoOpMetricsSystem();
 
   private SnapProtocolManager snapProtocolManager;
 
@@ -98,8 +121,235 @@ void disconnectsPeerOnDecompressionFailure() {
 
     assertThat(peerConnection.isDisconnected()).isFalse();
     // ethPeer (mock) receives the disconnect call
-    org.mockito.Mockito.verify(ethPeer)
-        .disconnect(DisconnectReason.BREACH_OF_PROTOCOL_MALFORMED_MESSAGE_RECEIVED);
+    verify(ethPeer).disconnect(DisconnectReason.BREACH_OF_PROTOCOL_MALFORMED_MESSAGE_RECEIVED);
+  }
+
+  @Test
+  void limitsConcurrentSnapRequestsPerPeer() {
+    when(snapConfig.getMaxConcurrentSnapRequestsPerPeer()).thenReturn(2);
+    snapProtocolManager = createSnapProtocolManager();
+
+    final MockPeerConnection peerConnection = snapPeerConnection();
+    stubPeer(ethPeer, peerConnection);
+    stubPendingServiceTasks();
+
+    for (int i = 0; i < 5; i++) {
+      snapProtocolManager.processMessage(
+          SnapProtocol.SNAP1, getTrieNodesMessage(peerConnection, i));
+    }
+
+    // Only the first 2 requests are scheduled; the remaining 3 are dropped once the per-peer cap
+    // (reproducing the unbounded fan-out this test guards against, absent the cap) is reached.
+    verify(ethScheduler, times(2)).scheduleServiceTask(any(Runnable.class));
+  }
+
+  @Test
+  void perPeerCapDoesNotBlockADistinctPeer() {
+    when(snapConfig.getMaxConcurrentSnapRequestsPerPeer()).thenReturn(2);
+    snapProtocolManager = createSnapProtocolManager();
+
+    final MockPeerConnection peerConnectionA = snapPeerConnection();
+    stubPeer(ethPeer, peerConnectionA);
+    final EthPeer ethPeerB = mock(EthPeer.class);
+    final MockPeerConnection peerConnectionB = snapPeerConnection();
+    stubPeer(ethPeerB, peerConnectionB);
+    stubPendingServiceTasks();
+
+    for (int i = 0; i < 2; i++) {
+      snapProtocolManager.processMessage(
+          SnapProtocol.SNAP1, getTrieNodesMessage(peerConnectionA, i));
+      snapProtocolManager.processMessage(
+          SnapProtocol.SNAP1, getTrieNodesMessage(peerConnectionB, i));
+    }
+
+    // Both peers stay within their own per-peer cap, so all 4 requests are scheduled.
+    verify(ethScheduler, times(4)).scheduleServiceTask(any(Runnable.class));
+  }
+
+  @Test
+  void limitsConcurrentSnapRequestsGlobally() {
+    when(snapConfig.getMaxConcurrentSnapRequestsGlobal()).thenReturn(3);
+    snapProtocolManager = createSnapProtocolManager();
+    stubPendingServiceTasks();
+
+    // 3 distinct peers, each individually under any per-peer cap, sending 2 requests each.
+    for (int peerIndex = 0; peerIndex < 3; peerIndex++) {
+      final EthPeer peer = mock(EthPeer.class);
+      final MockPeerConnection peerConnection = snapPeerConnection();
+      stubPeer(peer, peerConnection);
+      for (int i = 0; i < 2; i++) {
+        snapProtocolManager.processMessage(
+            SnapProtocol.SNAP1, getTrieNodesMessage(peerConnection, i));
+      }
+    }
+
+    // Only the first 3 requests (across all peers) are scheduled once the global cap is reached.
+    verify(ethScheduler, times(3)).scheduleServiceTask(any(Runnable.class));
+  }
+
+  @Test
+  void releasesSlotWhenScheduledTaskCompletes() {
+    when(snapConfig.getMaxConcurrentSnapRequestsPerPeer()).thenReturn(1);
+    snapProtocolManager = createSnapProtocolManager();
+
+    final MockPeerConnection peerConnection = snapPeerConnection();
+    stubPeer(ethPeer, peerConnection);
+    final List<CompletableFuture<Void>> scheduledTasks = new ArrayList<>();
+    when(ethScheduler.scheduleServiceTask(any(Runnable.class)))
+        .thenAnswer(
+            invocation -> {
+              final CompletableFuture<Void> future = new CompletableFuture<>();
+              scheduledTasks.add(future);
+              return future;
+            });
+
+    snapProtocolManager.processMessage(SnapProtocol.SNAP1, getTrieNodesMessage(peerConnection, 0));
+    snapProtocolManager.processMessage(SnapProtocol.SNAP1, getTrieNodesMessage(peerConnection, 1));
+    // Second request dropped: the peer's single slot is still held by the first, in-flight task.
+    verify(ethScheduler, times(1)).scheduleServiceTask(any(Runnable.class));
+
+    scheduledTasks.get(0).complete(null);
+
+    snapProtocolManager.processMessage(SnapProtocol.SNAP1, getTrieNodesMessage(peerConnection, 2));
+    // Completing the first task freed the slot, so the third request is now accepted.
+    verify(ethScheduler, times(2)).scheduleServiceTask(any(Runnable.class));
+  }
+
+  @Test
+  void releasesSlotWhenSchedulingThrowsSynchronously() {
+    when(snapConfig.getMaxConcurrentSnapRequestsPerPeer()).thenReturn(1);
+    snapProtocolManager = createSnapProtocolManager();
+
+    final MockPeerConnection peerConnection = snapPeerConnection();
+    stubPeer(ethPeer, peerConnection);
+    // Simulates CompletableFuture.runAsync throwing RejectedExecutionException synchronously,
+    // e.g. because the services executor is shutting down, before scheduleServiceTask ever
+    // returns a future to attach the release-on-complete handler to.
+    when(ethScheduler.scheduleServiceTask(any(Runnable.class)))
+        .thenThrow(new RejectedExecutionException("executor is shutting down"))
+        .thenAnswer(invocation -> new CompletableFuture<Void>());
+
+    assertThatThrownBy(
+            () ->
+                snapProtocolManager.processMessage(
+                    SnapProtocol.SNAP1, getTrieNodesMessage(peerConnection, 0)))
+        .isInstanceOf(RejectedExecutionException.class);
+
+    snapProtocolManager.processMessage(SnapProtocol.SNAP1, getTrieNodesMessage(peerConnection, 1));
+    // If the failed first attempt had leaked its reserved slot, this second request would be
+    // dropped (only 1 call to scheduleServiceTask) instead of being scheduled (2 calls).
+    verify(ethScheduler, times(2)).scheduleServiceTask(any(Runnable.class));
+  }
+
+  @Test
+  void clearsPeerSlotsOnDisconnectPreventingALeak() {
+    when(snapConfig.getMaxConcurrentSnapRequestsPerPeer()).thenReturn(1);
+    snapProtocolManager = createSnapProtocolManager();
+
+    final MockPeerConnection peerConnection = snapPeerConnection();
+    stubPeer(ethPeer, peerConnection);
+    stubPendingServiceTasks();
+
+    snapProtocolManager.processMessage(SnapProtocol.SNAP1, getTrieNodesMessage(peerConnection, 0));
+    verify(ethScheduler, times(1)).scheduleServiceTask(any(Runnable.class));
+
+    // The peer disconnects before its in-flight task ever completes.
+    snapProtocolManager.handleDisconnect(
+        peerConnection, DisconnectReason.TCP_SUBSYSTEM_ERROR, false);
+
+    snapProtocolManager.processMessage(SnapProtocol.SNAP1, getTrieNodesMessage(peerConnection, 1));
+    // Disconnect cleanup freed the slot rather than leaking it, so this request is accepted.
+    verify(ethScheduler, times(2)).scheduleServiceTask(any(Runnable.class));
+  }
+
+  @Test
+  void respondsEmptyWhenPerPeerCapReached() throws PeerConnection.PeerNotConnected {
+    when(snapConfig.getMaxConcurrentSnapRequestsPerPeer()).thenReturn(1);
+    snapProtocolManager = createSnapProtocolManager();
+
+    final MockPeerConnection peerConnection = snapPeerConnection();
+    stubPeer(ethPeer, peerConnection);
+    stubPendingServiceTasks();
+
+    snapProtocolManager.processMessage(SnapProtocol.SNAP1, getTrieNodesMessage(peerConnection, 0));
+    snapProtocolManager.processMessage(SnapProtocol.SNAP1, getTrieNodesMessage(peerConnection, 1));
+
+    // The first request holds the peer's only slot; the second is rejected but still answered
+    // rather than left to time out.
+    verify(ethScheduler, times(1)).scheduleServiceTask(any(Runnable.class));
+    final ArgumentCaptor<MessageData> sent = ArgumentCaptor.forClass(MessageData.class);
+    verify(ethPeer).send(sent.capture(), eq(SnapProtocol.NAME));
+    assertThat(sent.getValue().getCode()).isEqualTo(SnapV1.TRIE_NODES);
+    assertThat(TrieNodesMessage.readFrom(sent.getValue()).nodes(true)).isEmpty();
+    assertThat(sent.getValue().unwrapMessageData().getKey()).isEqualTo(BigInteger.ONE);
+  }
+
+  @Test
+  void respondsEmptyWhenGlobalCapReached() throws PeerConnection.PeerNotConnected {
+    when(snapConfig.getMaxConcurrentSnapRequestsGlobal()).thenReturn(1);
+    snapProtocolManager = createSnapProtocolManager();
+    stubPendingServiceTasks();
+
+    final MockPeerConnection peerConnectionA = snapPeerConnection();
+    stubPeer(ethPeer, peerConnectionA);
+    final EthPeer ethPeerB = mock(EthPeer.class);
+    final MockPeerConnection peerConnectionB = snapPeerConnection();
+    stubPeer(ethPeerB, peerConnectionB);
+
+    snapProtocolManager.processMessage(SnapProtocol.SNAP1, getTrieNodesMessage(peerConnectionA, 0));
+    snapProtocolManager.processMessage(SnapProtocol.SNAP1, getTrieNodesMessage(peerConnectionB, 7));
+
+    // The global cap is already spent on peer A's request, so peer B's is rejected but answered.
+    verify(ethScheduler, times(1)).scheduleServiceTask(any(Runnable.class));
+    final ArgumentCaptor<MessageData> sent = ArgumentCaptor.forClass(MessageData.class);
+    verify(ethPeerB).send(sent.capture(), eq(SnapProtocol.NAME));
+    assertThat(sent.getValue().unwrapMessageData().getKey()).isEqualTo(BigInteger.valueOf(7));
+    verify(ethPeer, never()).send(any(), any());
+  }
+
+  @Test
+  void disconnectsPeerWhenRejectedRequestIsMalformed() throws PeerConnection.PeerNotConnected {
+    when(snapConfig.getMaxConcurrentSnapRequestsPerPeer()).thenReturn(1);
+    snapProtocolManager = createSnapProtocolManager();
+
+    final MockPeerConnection peerConnection = snapPeerConnection();
+    stubPeer(ethPeer, peerConnection);
+    stubPendingServiceTasks();
+
+    // First request holds the peer's only slot.
+    snapProtocolManager.processMessage(SnapProtocol.SNAP1, getTrieNodesMessage(peerConnection, 0));
+
+    // Second request is over cap, and its body isn't a valid RLP list, so decoding a request id
+    // for the empty reply fails.
+    final MessageData malformed = new RawMessage(SnapV1.GET_TRIE_NODES, Bytes.of(0x01));
+    snapProtocolManager.processMessage(
+        SnapProtocol.SNAP1, new DefaultMessage(peerConnection, malformed));
+
+    verify(ethPeer).disconnect(DisconnectReason.BREACH_OF_PROTOCOL_MALFORMED_MESSAGE_RECEIVED);
+    verify(ethPeer, never()).send(any(), any());
+  }
+
+  private void stubPeer(final EthPeer peer, final PeerConnection connection) {
+    when(ethPeers.peer(connection)).thenReturn(peer);
+    when(peer.getConnection()).thenReturn(connection);
+    when(peer.validateReceivedMessage(any(), any())).thenReturn(true);
+  }
+
+  private void stubPendingServiceTasks() {
+    when(ethScheduler.scheduleServiceTask(any(Runnable.class)))
+        .thenAnswer(invocation -> new CompletableFuture<Void>());
+  }
+
+  private MockPeerConnection snapPeerConnection() {
+    return new MockPeerConnection(
+        new HashSet<>(Collections.singletonList(SnapProtocol.SNAP1)), (cap, msg, conn) -> {});
+  }
+
+  private Message getTrieNodesMessage(final PeerConnection peerConnection, final int requestId) {
+    final MessageData data =
+        GetTrieNodesMessage.create(Hash.ZERO, List.of(List.of(Bytes.EMPTY)))
+            .wrapMessageData(BigInteger.valueOf(requestId));
+    return new DefaultMessage(peerConnection, data);
   }
 
   private SnapProtocolManager createSnapProtocolManager() {
@@ -110,6 +360,7 @@ private SnapProtocolManager createSnapProtocolManager() {
         snapMessages,
         ethScheduler,
         protocolContext,
-        synchronizer);
+        synchronizer,
+        metricsSystem);
   }
 }
```
