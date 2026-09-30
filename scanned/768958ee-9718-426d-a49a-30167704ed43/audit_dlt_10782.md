# [?] Merge pull request #663 from radixdlt/feature/nt312-fix-deadlock

## Summary
Severity: Unknown
Chain: Radix
Component: radixdlt/babylon-node
Published: 2022-04-04
Source: https://github.com/radixdlt/babylon-node/commit/637a757436f01aba8677f8768a361fd28b360d83
Type: security-commit

## Details
Merge pull request #663 from radixdlt/feature/nt312-fix-deadlock

Fix deadlock related to how the PendingChannelsManager completes the futures

## Patch
### radixdlt-core/radixdlt/src/main/java/com/radixdlt/network/p2p/PendingOutboundChannelsManager.java
```diff
@@ -73,20 +73,20 @@
 import com.radixdlt.network.p2p.transport.PeerChannel;
 import com.radixdlt.network.p2p.transport.PeerOutboundBootstrap;
 import java.io.IOException;
-import java.util.HashMap;
 import java.util.Map;
 import java.util.Objects;
 import java.util.Optional;
 import java.util.concurrent.CompletableFuture;
+import java.util.concurrent.ConcurrentHashMap;
 import javax.inject.Inject;
 
 public final class PendingOutboundChannelsManager {
   private final P2PConfig config;
   private final PeerOutboundBootstrap peerOutboundBootstrap;
   private final ScheduledEventDispatcher<PeerOutboundConnectionTimeout> timeoutEventDispatcher;
   private final EventDispatcher<PeerEvent> peerEventDispatcher;
-  private final Object lock = new Object();
-  private final Map<NodeId, CompletableFuture<PeerChannel>> pendingChannels = new HashMap<>();
+  private final Map<NodeId, CompletableFuture<PeerChannel>> pendingChannels =
+      new ConcurrentHashMap<>() {};
 
   @Inject
   public PendingOutboundChannelsManager(
@@ -101,20 +101,21 @@ public PendingOutboundChannelsManager(
   }
 
   public CompletableFuture<PeerChannel> connectTo(RadixNodeUri uri) {
-    synchronized (lock) {
-      final var remoteNodeId = uri.getNodeId();
+    final var remoteNodeId = uri.getNodeId();
+    final CompletableFuture<PeerChannel> newChannelFuture = new CompletableFuture<>();
 
-      if (this.pendingChannels.containsKey(remoteNodeId)) {
-        return this.pendingChannels.get(remoteNodeId);
-      } else {
-        final var channelFuture = new CompletableFuture<PeerChannel>();
-        this.pendingChannels.put(remoteNodeId, channelFuture);
-        this.peerOutboundBootstrap.initOutboundConnection(uri);
-        this.timeoutEventDispatcher.dispatch(
-            new PeerOutboundConnectionTimeout(uri), config.peerConnectionTimeout());
-        return channelFuture;
-      }
+    var existingChannelFutureOpt =
+        Optional.ofNullable(this.pendingChannels.putIfAbsent(remoteNodeId, newChannelFuture));
+
+    // There was no existing channel future that has already been initialized for this node ID
+    //   so we init a new outbound connection
+    if (existingChannelFutureOpt.isEmpty()) {
+      this.peerOutboundBootstrap.initOutboundConnection(uri);
+      this.timeoutEventDispatcher.dispatch(
+          new PeerOutboundConnectionTimeout(uri), config.peerConnectionTimeout());
     }
+
+    return existingChannelFutureOpt.orElse(newChannelFuture);
   }
 
   public EventProcessor<PeerEvent> peerEventProcessor() {
@@ -128,37 +129,36 @@ public EventProcessor<PeerEvent> peerEventProcessor() {
   }
 
   private void handlePeerConnected(PeerConnected peerConnected) {
-    synchronized (lock) {
-      final var channel = peerConnected.channel();
-      final var maybeFuture = this.pendingChannels.remove(channel.getRemoteNodeId());
-      if (maybeFuture != null) {
-        maybeFuture.complete(channel);
-      }
-    }
+    final var channel = peerConnected.channel();
+    final Optional<CompletableFuture<PeerChannel>> channelFutureOpt;
+    channelFutureOpt = Optional.ofNullable(this.pendingChannels.remove(channel.getRemoteNodeId()));
+    channelFutureOpt.ifPresent(channelFuture -> channelFuture.complete(channel));
   }
 
   private void handlePeerHandshakeFailed(PeerHandshakeFailed peerHandshakeFailed) {
-    synchronized (lock) {
-      peerHandshakeFailed
-          .channel()
-          .getUri()
-          .map(RadixNodeUri::getNodeId)
-          .flatMap(nodeId -> Optional.ofNullable(this.pendingChannels.remove(nodeId)))
-          .ifPresent(
-              future -> future.completeExceptionally(new IOException("Peer connection failed")));
-    }
+    final Optional<CompletableFuture<PeerChannel>> channelFutureOpt;
+    channelFutureOpt =
+        peerHandshakeFailed
+            .channel()
+            .getUri()
+            .map(RadixNodeUri::getNodeId)
+            .flatMap(nodeId -> Optional.ofNullable(this.pendingChannels.remove(nodeId)));
+    channelFutureOpt.ifPresent(
+        channelFuture ->
+            channelFuture.completeExceptionally(new IOException("Peer connection failed")));
   }
 
   public EventProcessor<PeerOutboundConnectionTimeout>
       peerOutboundConnectionTimeoutEventProcessor() {
     return timeout -> {
-      synchronized (lock) {
-        final var maybeFuture = this.pendingChannels.remove(timeout.uri().getNodeId());
-        if (maybeFuture != null) {
-          maybeFuture.completeExceptionally(new IOException("Peer connection timeout"));
-          peerEventDispatcher.dispatch(new PeerConnectionTimeout(timeout.uri()));
-        }
-      }
+      final Optional<CompletableFuture<PeerChannel>> channelFutureOpt;
+      channelFutureOpt =
+          Optional.ofNullable(this.pendingChannels.remove(timeout.uri().getNodeId()));
+      channelFutureOpt.ifPresent(
+          channelFuture -> {
+            channelFuture.completeExceptionally(new IOException("Peer connection timeout"));
+            peerEventDispatcher.dispatch(new PeerConnectionTimeout(timeout.uri()));
+          });
     };
   }
 
```
