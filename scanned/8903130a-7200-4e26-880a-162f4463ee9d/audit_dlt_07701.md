# [?] Fixes: GHSA-6r9q-wjp4-34gh fix(p2p): bound pre-STATUS RLPx connections and close them on eviction (#11096)

## Summary
Severity: Unknown
Chain: Ethereum
Component: besu-eth/besu
Published: 2026-08-20
Source: https://github.com/besu-eth/besu/commit/e540ae23949525696c43420caffb864ed8c2b577
Type: security-commit

## Details
Fixes: GHSA-6r9q-wjp4-34gh fix(p2p): bound pre-STATUS RLPx connections and close them on eviction (#11096)

Signed-off-by: Sally MacFarlane <macfarla.github@gmail.com>

## Patch
### CHANGELOG.md
```diff
@@ -68,6 +68,7 @@
 - Removed the legacy `PANTHEON_` environment variable prefix for configuration options, everyone should already use the `BESU_` prefix at this time.
 
 ### Bug fixes
+- Cap pre-STATUS RLPx connections and close them on eviction to prevent resource exhaustion.
 - Improve logging for malformed discv4 UDP packets.
 - Bound the snap sync storage sub-range split count to prevent unbounded memory growth under a malformed snap response.
 - Added a configurable range cap (--graphql-max-blocks-range, default 5000) for GraphQL blocks(from, to) range queries; queries exceeding the cap are cancelled.
```

### ethereum/eth/src/main/java/org/hyperledger/besu/ethereum/eth/manager/EthPeers.java
```diff
@@ -91,12 +91,20 @@ public class EthPeers implements PeerSelector {
 
   private final Map<Bytes, EthPeer> activeConnections = new ConcurrentHashMap<>();
 
-  private final Cache<PeerConnection, EthPeer> incompleteConnections =
-      CacheBuilder.newBuilder()
-          .expireAfterWrite(Duration.ofSeconds(20L))
-          .concurrencyLevel(1)
-          .removalListener(this::onCacheRemoval)
-          .build();
+  /**
+   * Lower bound for the pre-STATUS (incomplete) connection cap, so that even very small {@code
+   * --max-peers} values still tolerate a reasonable number of concurrent inbound handshakes.
+   */
+  private static final int INCOMPLETE_CONNECTIONS_CAP_FLOOR = 10;
+
+  /**
+   * Maximum number of connections that have completed the devp2p HELLO but not yet the eth STATUS
+   * handshake that we retain. Bounds file-descriptor and heap growth from peers that connect and
+   * never send STATUS, which are otherwise invisible to {@code --max-peers} accounting.
+   */
+  private final int maxIncompleteConnections;
+
+  private final Cache<PeerConnection, EthPeer> incompleteConnections;
   private final Clock clock;
   private final List<NodeMessagePermissioningProvider> permissioningProviders;
   private final int maxMessageSize;
@@ -151,6 +159,14 @@ public EthPeers(
     this.snapServerTargetNumber =
         peerUpperBound / 2; // 50% of peers should be snap servers while snap syncing
     this.shouldLimitRemoteConnections = maxRemotelyInitiatedConnections < peerUpperBound;
+    this.maxIncompleteConnections = Math.max(peerUpperBound * 2, INCOMPLETE_CONNECTIONS_CAP_FLOOR);
+    this.incompleteConnections =
+        CacheBuilder.newBuilder()
+            .maximumSize(maxIncompleteConnections)
+            .expireAfterWrite(Duration.ofSeconds(20L))
+            .concurrencyLevel(1)
+            .removalListener(this::onCacheRemoval)
+            .build();
 
     metricsSystem.createIntegerGauge(
         BesuMetricCategory.ETHEREUM,
@@ -173,6 +189,11 @@ public EthPeers(
         "peer_limit",
         "The maximum number of peers this node allows to connect",
         () -> peerUpperBound);
+    metricsSystem.createIntegerGauge(
+        BesuMetricCategory.ETHEREUM,
+        "peer_count_incomplete",
+        "The current number of connections that have not yet completed the eth STATUS handshake",
+        () -> (int) incompleteConnections.size());
 
     connectedPeersCounter =
         metricsSystem.createCounter(
@@ -775,22 +796,55 @@ private long countUntrustedRemotelyInitiatedConnections() {
         .count();
   }
 
-  private void onCacheRemoval(
-      final RemovalNotification<PeerConnection, EthPeer> removalNotification) {
-    if (removalNotification.wasEvicted()) {
-      final PeerConnection peerConnectionRemoved = removalNotification.getKey();
-      final EthPeer peer = removalNotification.getValue();
-      if (peer == null) {
-        return;
-      }
-      final PeerConnection peerConnectionOfEthPeer = peer.getConnection();
-      if (peerConnectionRemoved != null) {
-        if (!peerConnectionRemoved.equals(peerConnectionOfEthPeer)) {
-          // If this connection is not the connection of the EthPeer by now we can disconnect
-          peerConnectionRemoved.disconnect(DisconnectMessage.DisconnectReason.ALREADY_CONNECTED);
-        }
-      }
+  @VisibleForTesting
+  void onCacheRemoval(final RemovalNotification<PeerConnection, EthPeer> removalNotification) {
+    // Only react to evictions (size cap or expiry). Explicit invalidations (e.g. on a normal
+    // disconnect) already close the connection through their own path.
+    if (!removalNotification.wasEvicted()) {
+      return;
     }
+    final PeerConnection evictedConnection = removalNotification.getKey();
+    final EthPeer peer = removalNotification.getValue();
+    if (evictedConnection == null || evictedConnection.isDisconnected()) {
+      return;
+    }
+
+    final boolean isCurrentConnectionOfPeer =
+        peer != null && evictedConnection.equals(peer.getConnection());
+    if (isCurrentConnectionOfPeer && peer.statusHasBeenReceived()) {
+      // The peer completed (or is completing) the eth STATUS handshake and is being promoted to an
+      // active connection; its incomplete-cache entry is expiring naturally. Leave the live
+      // connection alone - it is (or will be) tracked in activeConnections.
+      return;
+    }
+
+    // Either a superseded connection (the peer reconnected with a different connection), or a
+    // connection that completed the devp2p HELLO but never sent eth STATUS and has now been evicted
+    // (20s expiry, or pushed out of the bounded cache). Close the socket so evicted pre-STATUS
+    // connections cannot leak file descriptors or heap while remaining invisible to --max-peers.
+    DisconnectReason reason =
+        isCurrentConnectionOfPeer
+            ? DisconnectMessage.DisconnectReason.TIMEOUT
+            : DisconnectMessage.DisconnectReason.ALREADY_CONNECTED;
+
+    LOG.atTrace()
+        .setMessage(
+            "Closing pre-STATUS connection {} evicted from incomplete-connection cache, reason {}")
+        .addArgument(evictedConnection::getPeerInfo)
+        .addArgument(reason)
+        .log();
+
+    evictedConnection.disconnect(reason);
+  }
+
+  @VisibleForTesting
+  int incompleteConnectionCount() {
+    return (int) incompleteConnections.size();
+  }
+
+  @VisibleForTesting
+  int getMaxIncompleteConnections() {
+    return maxIncompleteConnections;
   }
 
   boolean addPeerToEthPeers(final EthPeer peer) {
```

### ethereum/eth/src/test/java/org/hyperledger/besu/ethereum/eth/manager/EthPeersTest.java
```diff
@@ -20,6 +20,7 @@
 import static org.assertj.core.api.Assertions.fail;
 import static org.mockito.ArgumentMatchers.any;
 import static org.mockito.Mockito.mock;
+import static org.mockito.Mockito.never;
 import static org.mockito.Mockito.spy;
 import static org.mockito.Mockito.times;
 import static org.mockito.Mockito.verify;
@@ -33,6 +34,7 @@
 import org.hyperledger.besu.ethereum.eth.manager.exceptions.PeerDisconnectedException;
 import org.hyperledger.besu.ethereum.eth.messages.BlockBodiesMessage;
 import org.hyperledger.besu.ethereum.eth.sync.ChainHeadTracker;
+import org.hyperledger.besu.ethereum.p2p.peers.Peer;
 import org.hyperledger.besu.ethereum.p2p.rlpx.connections.PeerConnection;
 import org.hyperledger.besu.ethereum.p2p.rlpx.connections.PeerConnection.PeerNotConnected;
 import org.hyperledger.besu.ethereum.p2p.rlpx.wire.MessageData;
@@ -47,6 +49,9 @@
 import java.util.concurrent.TimeUnit;
 import java.util.function.Consumer;
 
+import com.google.common.cache.RemovalCause;
+import com.google.common.cache.RemovalNotification;
+import org.apache.tuweni.bytes.Bytes;
 import org.junit.jupiter.api.BeforeEach;
 import org.junit.jupiter.api.Test;
 import org.mockito.Mockito;
@@ -504,4 +509,75 @@ private void assertNotDone(final PendingPeerRequest pendingRequest) {
     verifyNoInteractions(onSuccess);
     verifyNoInteractions(onError);
   }
+
+  // The pre-STATUS (incomplete) connection cache is bounded, so a peer that completes the devp2p
+  // HELLO but never sends eth STATUS cannot accumulate unbounded connections outside --max-peers
+  // accounting.
+  @Test
+  public void incompleteConnectionsAreBounded() {
+    final int limit = ethPeers.getMaxIncompleteConnections();
+    for (int i = 0; i < limit + 10; i++) {
+      ethPeers.registerNewConnection(mockIncompleteConnection(i), emptyList());
+    }
+    assertThat(ethPeers.incompleteConnectionCount()).isLessThanOrEqualTo(limit);
+    assertThat(ethPeers.incompleteConnectionCount()).isPositive();
+  }
+
+  // An evicted connection that never completed eth STATUS must be disconnected so its socket / file
+  // descriptor is released rather than leaked (the previous removal listener left a lone pre-STATUS
+  // connection open on eviction).
+  @Test
+  public void evictedPreStatusConnectionIsDisconnected() {
+    final PeerConnection connection = mock(PeerConnection.class);
+    when(connection.isDisconnected()).thenReturn(false);
+    final EthPeer peer = mock(EthPeer.class);
+    when(peer.getConnection()).thenReturn(connection);
+    when(peer.statusHasBeenReceived()).thenReturn(false);
+
+    ethPeers.onCacheRemoval(RemovalNotification.create(connection, peer, RemovalCause.SIZE));
+
+    verify(connection).disconnect(DisconnectReason.TIMEOUT);
+  }
+
+  // A connection that completed eth STATUS and is being promoted to an active connection must NOT
+  // be
+  // disconnected when its incomplete-cache entry expires.
+  @Test
+  public void evictedPromotedConnectionIsNotDisconnected() {
+    final PeerConnection connection = mock(PeerConnection.class);
+    when(connection.isDisconnected()).thenReturn(false);
+    final EthPeer peer = mock(EthPeer.class);
+    when(peer.getConnection()).thenReturn(connection);
+    when(peer.statusHasBeenReceived()).thenReturn(true);
+
+    ethPeers.onCacheRemoval(RemovalNotification.create(connection, peer, RemovalCause.SIZE));
+
+    verify(connection, never()).disconnect(any());
+  }
+
+  // Explicit cache invalidation (e.g. a normal disconnect path) must not trigger a second
+  // disconnect from the removal listener.
+  @Test
+  public void explicitCacheInvalidationDoesNotDisconnect() {
+    final PeerConnection connection = mock(PeerConnection.class);
+    when(connection.isDisconnected()).thenReturn(false);
+    final EthPeer peer = mock(EthPeer.class);
+    when(peer.getConnection()).thenReturn(connection);
+
+    ethPeers.onCacheRemoval(RemovalNotification.create(connection, peer, RemovalCause.EXPLICIT));
+
+    verify(connection, never()).disconnect(any());
+  }
+
+  private PeerConnection mockIncompleteConnection(final int index) {
+    final byte[] idBytes = new byte[64];
+    idBytes[0] = (byte) (index >> 8);
+    idBytes[1] = (byte) index;
+    final Peer remotePeer = mock(Peer.class);
+    when(remotePeer.getId()).thenReturn(Bytes.wrap(idBytes));
+    final PeerConnection connection = mock(PeerConnection.class);
+    when(connection.getPeer()).thenReturn(remotePeer);
+    when(connection.isDisconnected()).thenReturn(false);
+    return connection;
+  }
 }
```
