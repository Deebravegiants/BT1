# [?] Fix deadlock related to how the PendingChannelsManager completes the futures

## Summary
Severity: Unknown
Chain: Radix
Component: radixdlt/babylon-node
Published: 2022-03-31
Source: https://github.com/radixdlt/babylon-node/commit/b597521b13537df00299ea925009e437d7f60b26
Type: security-commit

## Details
Fix deadlock related to how the PendingChannelsManager completes the futures

## Patch
### radixdlt-core/radixdlt/src/main/java/com/radixdlt/network/p2p/PendingOutboundChannelsManager.java
```diff
@@ -128,37 +128,43 @@ public EventProcessor<PeerEvent> peerEventProcessor() {
   }
 
   private void handlePeerConnected(PeerConnected peerConnected) {
+    final var channel = peerConnected.channel();
+    final Optional<CompletableFuture<PeerChannel>> channelFutureOpt;
     synchronized (lock) {
-      final var channel = peerConnected.channel();
-      final var maybeFuture = this.pendingChannels.remove(channel.getRemoteNodeId());
-      if (maybeFuture != null) {
-        maybeFuture.complete(channel);
-      }
+      channelFutureOpt =
+          Optional.ofNullable(this.pendingChannels.remove(channel.getRemoteNodeId()));
     }
+    channelFutureOpt.ifPresent(channelFuture -> channelFuture.complete(channel));
   }
 
   private void handlePeerHandshakeFailed(PeerHandshakeFailed peerHandshakeFailed) {
+    final Optional<CompletableFuture<PeerChannel>> channelFutureOpt;
     synchronized (lock) {
-      peerHandshakeFailed
-          .channel()
-          .getUri()
-          .map(RadixNodeUri::getNodeId)
-          .flatMap(nodeId -> Optional.ofNullable(this.pendingChannels.remove(nodeId)))
-          .ifPresent(
-              future -> future.completeExceptionally(new IOException("Peer connection failed")));
+      channelFutureOpt =
+          peerHandshakeFailed
+              .channel()
+              .getUri()
+              .map(RadixNodeUri::getNodeId)
+              .flatMap(nodeId -> Optional.ofNullable(this.pendingChannels.remove(nodeId)));
     }
+    channelFutureOpt.ifPresent(
+        channelFuture ->
+            channelFuture.completeExceptionally(new IOException("Peer connection failed")));
   }
 
   public EventProcessor<PeerOutboundConnectionTimeout>
       peerOutboundConnectionTimeoutEventProcessor() {
     return timeout -> {
+      final Optional<CompletableFuture<PeerChannel>> channelFutureOpt;
       synchronized (lock) {
-        final var maybeFuture = this.pendingChannels.remove(timeout.uri().getNodeId());
-        if (maybeFuture != null) {
-          maybeFuture.completeExceptionally(new IOException("Peer connection timeout"));
-          peerEventDispatcher.dispatch(new PeerConnectionTimeout(timeout.uri()));
-        }
+        channelFutureOpt =
+            Optional.ofNullable(this.pendingChannels.remove(timeout.uri().getNodeId()));
       }
+      channelFutureOpt.ifPresent(
+          channelFuture -> {
+            channelFuture.completeExceptionally(new IOException("Peer connection timeout"));
+            peerEventDispatcher.dispatch(new PeerConnectionTimeout(timeout.uri()));
+          });
     };
   }
 
```
