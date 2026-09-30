# [?] fix: Remove RpcOverloadMonitor race condition (#26827)

## Summary
Severity: Unknown
Chain: Hedera
Component: hiero-ledger/hiero-consensus-node
Published: 2026-08-17
Source: https://github.com/hiero-ledger/hiero-consensus-node/commit/e7c1b0d4f8a7455e092c4eb5792a24ab35faa46c
Type: security-commit

## Details
fix: Remove RpcOverloadMonitor race condition (#26827)

Signed-off-by: Artur Biesiadowski <artur.biesiadowski@swirldslabs.com>

## Patch
### platform-sdk/consensus-gossip-impl/src/main/java/org/hiero/consensus/gossip/impl/network/protocol/rpc/RpcOverloadMonitor.java
```diff
@@ -14,6 +14,7 @@
  * callback about being 'overloaded' Please see {@link BroadcastConfig#throttleOutputQueueThreshold()},
  * {@link BroadcastConfig#disablePingThreshold()} and {@link BroadcastConfig#pauseOnLag()} for configuration
  * options
+ * This class is not thread safe, all methods should be called from the same thread.
  */
 public class RpcOverloadMonitor {
 
@@ -24,8 +25,8 @@ public class RpcOverloadMonitor {
     private final Time time;
     private final Consumer<Boolean> communicationOverloadHandler;
 
-    private volatile long disabledBroadcastDueToQueueSizeTime = ENABLED;
-    private volatile long disabledBroadcastDueToLagTime = ENABLED;
+    private long disabledBroadcastDueToQueueSizeTime = ENABLED;
+    private long disabledBroadcastDueToLagTime = ENABLED;
 
     public RpcOverloadMonitor(
             @NonNull final BroadcastConfig syncConfig,
```

### platform-sdk/consensus-gossip-impl/src/main/java/org/hiero/consensus/gossip/impl/network/protocol/rpc/RpcPeerProtocol.java
```diff
@@ -481,7 +481,10 @@ private void readMessages(@NonNull final Connection connection) throws IOExcepti
                             final long correlationId = input.readLong();
                             final long pingMillis =
                                     TimeUnit.NANOSECONDS.toMillis(pingHandler.handleIncomingPingReply(correlationId));
-                            overloadMonitor.reportPing(pingMillis);
+                            // we are still reporting delay to receive, not to handle
+                            // we want to measure the network ping, rather than dispatch thread ping
+                            // it is still handled over there, to make overloadMonitor managed from same thread
+                            inputQueue.add(() -> overloadMonitor.reportPing(pingMillis));
                             break;
                     }
                 }
```

### platform-sdk/consensus-gossip-impl/src/test/java/org/hiero/consensus/gossip/impl/gossip/RpcOverloadMonitorTest.java
```diff
@@ -1,5 +1,5 @@
 // SPDX-License-Identifier: Apache-2.0
-package com.swirlds.platform.gossip;
+package org.hiero.consensus.gossip.impl.gossip;
 
 // this class should be moved to a different package, but modules are WIP as of now and it is not possible to do that
 // without breaking build
```
