# [?] Merge pull request #3732 from zhang0125/HotFix/fix-network-deadlock

## Summary
Severity: Unknown
Chain: Tron
Component: tronprotocol/java-tron
Published: 2021-04-08
Source: https://github.com/tronprotocol/java-tron/commit/93e5af426f7f2a66fa4aae96c740450f23631b9e
Type: security-commit

## Details
Merge pull request #3732 from zhang0125/HotFix/fix-network-deadlock

Hot fix/fix network deadlock

## Patch
### framework/src/main/java/org/tron/core/net/service/AdvService.java
```diff
@@ -106,29 +106,26 @@ public synchronized void addInvToCache(Item item) {
     invToFetch.remove(item);
   }
 
-  public synchronized boolean addInv(Item item) {
-
+  public boolean addInv(Item item) {
     if (fastForward && item.getType().equals(InventoryType.TRX)) {
       return false;
     }
 
-    if (invToFetchCache.getIfPresent(item) != null) {
+    if (item.getType().equals(InventoryType.TRX) && trxCache.getIfPresent(item) != null) {
+      return false;
+    }
+    if (item.getType().equals(InventoryType.BLOCK) && blockCache.getIfPresent(item) != null) {
       return false;
     }
 
-    if (item.getType().equals(InventoryType.TRX)) {
-      if (trxCache.getIfPresent(item) != null) {
-        return false;
-      }
-    } else {
-      if (blockCache.getIfPresent(item) != null) {
+    synchronized (this) {
+      if (invToFetchCache.getIfPresent(item) != null) {
         return false;
       }
+      invToFetchCache.put(item, System.currentTimeMillis());
+      invToFetch.put(item, System.currentTimeMillis());
     }
 
-    invToFetchCache.put(item, System.currentTimeMillis());
-    invToFetch.put(item, System.currentTimeMillis());
-
     if (InventoryType.BLOCK.equals(item.getType())) {
       consumerInvToFetch();
     }
@@ -221,34 +218,35 @@ public void onDisconnect(PeerConnection peer) {
     }
   }
 
-  private synchronized void consumerInvToFetch() {
+  private void consumerInvToFetch() {
     Collection<PeerConnection> peers = tronNetDelegate.getActivePeer().stream()
         .filter(peer -> peer.isIdle())
         .collect(Collectors.toList());
 
-    if (invToFetch.isEmpty() || peers.isEmpty()) {
-      return;
-    }
-
     InvSender invSender = new InvSender();
     long now = System.currentTimeMillis();
-    invToFetch.forEach((item, time) -> {
-      if (time < now - MSG_CACHE_DURATION_IN_BLOCKS * BLOCK_PRODUCED_INTERVAL) {
-        logger.info("This obj is too late to fetch, type: {} hash: {}.", item.getType(),
-            item.getHash());
-        invToFetch.remove(item);
-        invToFetchCache.invalidate(item);
+    synchronized (this) {
+      if (invToFetch.isEmpty() || peers.isEmpty()) {
         return;
       }
-      peers.stream().filter(peer -> peer.getAdvInvReceive().getIfPresent(item) != null
-          && invSender.getSize(peer) < MAX_TRX_FETCH_PER_PEER)
-          .sorted(Comparator.comparingInt(peer -> invSender.getSize(peer)))
-          .findFirst().ifPresent(peer -> {
-            invSender.add(item, peer);
-            peer.getAdvInvRequest().put(item, now);
-            invToFetch.remove(item);
-          });
-    });
+      invToFetch.forEach((item, time) -> {
+        if (time < now - MSG_CACHE_DURATION_IN_BLOCKS * BLOCK_PRODUCED_INTERVAL) {
+          logger.info("This obj is too late to fetch, type: {} hash: {}.", item.getType(),
+                  item.getHash());
+          invToFetch.remove(item);
+          invToFetchCache.invalidate(item);
+          return;
+        }
+        peers.stream().filter(peer -> peer.getAdvInvReceive().getIfPresent(item) != null
+                && invSender.getSize(peer) < MAX_TRX_FETCH_PER_PEER)
+                .sorted(Comparator.comparingInt(peer -> invSender.getSize(peer)))
+                .findFirst().ifPresent(peer -> {
+                  invSender.add(item, peer);
+                  peer.getAdvInvRequest().put(item, now);
+                  invToFetch.remove(item);
+                });
+      });
+    }
 
     invSender.sendFetch();
   }
```
