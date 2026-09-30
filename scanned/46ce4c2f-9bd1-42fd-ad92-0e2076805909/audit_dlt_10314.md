# [?] Fixed race condition on MessageCounter

## Summary
Severity: Unknown
Chain: Rootstock
Component: rsksmart/rskj
Published: 2022-05-27
Source: https://github.com/rsksmart/rskj/commit/de8a0669567568573052e113a0f213589713def8
Type: security-commit

## Details
Fixed race condition on MessageCounter

## Patch
### rskj-core/src/main/java/co/rsk/net/MessageCounter.java
```diff
@@ -36,14 +36,14 @@ public class MessageCounter {
 
     private static final String COUNTER_ERROR = "Counter for {} is null or negative: {}.";
 
-    private Map<NodeID, AtomicInteger> messagesPerNode = new ConcurrentHashMap<>();
+    private final Map<NodeID, AtomicInteger> messagesPerNode = new ConcurrentHashMap<>();
 
 
-    public int getValue(Peer sender) {
+    int getValue(Peer sender) {
         return Optional.ofNullable(messagesPerNode.get(sender.getPeerNodeID())).orElse(ZERO).intValue();
     }
 
-    public void increment(Peer sender) {
+    void increment(Peer sender) {
         messagesPerNode
             .computeIfAbsent(sender.getPeerNodeID(), this::createAtomicInteger)
             .incrementAndGet();
@@ -53,7 +53,7 @@ private AtomicInteger createAtomicInteger(NodeID nodeId) {
         return new AtomicInteger();
     }
 
-    public void decrement(Peer sender) {
+    void decrement(Peer sender) {
 
         NodeID peerNodeID = sender.getPeerNodeID();
         AtomicInteger cnt = messagesPerNode.get(peerNodeID);
@@ -72,7 +72,7 @@ public void decrement(Peer sender) {
 
     }
 
-    public boolean hasCounter(Peer sender) {
+    boolean hasCounter(Peer sender) {
         return messagesPerNode.containsKey(sender.getPeerNodeID());
     }
 
```

### rskj-core/src/main/java/co/rsk/net/NodeMessageHandler.java
```diff
@@ -27,6 +27,7 @@
 import javax.annotation.Nonnull;
 import javax.annotation.Nullable;
 
+import com.google.common.annotations.VisibleForTesting;
 import org.ethereum.crypto.HashUtil;
 import org.ethereum.net.server.ChannelManager;
 import org.slf4j.Logger;
@@ -227,11 +228,14 @@ private boolean allowByMessageUniqueness(Peer sender, Message message) {
     }
 
     private void addMessage(Peer sender, Message message, double score) {
-        boolean messageAdded = this.queue.offer(new MessageTask(sender, message, score));
+        // optimistic increment() to ensure it is called before decrement() on processMessage()
+        // there was a race condition on which queue got the new item and decrement() was called before increment() for the same sender
+        // also, while queue implementation stays unbounded, offer() will never return false
+        messageCounter.increment(sender);
 
-        if (messageAdded) {
-            messageCounter.increment(sender);
-        } else {
+        boolean messageAdded = this.queue.offer(new MessageTask(sender, message, score));
+        if (!messageAdded) {
+            messageCounter.decrement(sender);
             logger.warn("Unexpected path. Is message queue bounded now?");
         }
     }
@@ -274,7 +278,8 @@ public long getMessageQueueSize() {
         return this.queue.size();
     }
 
-    public int getMessageQueueSize(Peer peer) {
+    @VisibleForTesting
+    int getMessageQueueSize(Peer peer) {
         return messageCounter.getValue(peer);
     }
 
```
