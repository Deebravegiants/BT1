# [?] Fix possible deadlock

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2019-02-19
Source: https://github.com/Zilliqa/zq1/commit/ec1b5499e5087f483ed90c6855a349966f6759aa
Type: security-commit

## Details
Fix possible deadlock

## Patch
### src/libNode/FinalBlockProcessing.cpp
```diff
@@ -532,6 +532,7 @@ void Node::PrepareGoodStateForFinalBlock() {
 
 bool Node::ProcessFinalBlock(const bytes& message, unsigned int offset,
                              [[gnu::unused]] const Peer& from) {
+  LOG_MARKER();
   return ProcessFinalBlockCore(message, offset, from);
 }
 
@@ -552,24 +553,29 @@ bool Node::ProcessFinalBlockCore(const bytes& message, unsigned int offset,
     return false;
   }
 
-  lock_guard<mutex> g(m_mutexFinalBlock);
-
-  if (m_mediator.m_lookup->GetSyncType() != SyncType::NO_SYNC &&
-      LOOKUP_NODE_MODE && ARCHIVAL_LOOKUP) {
-    // Buffer the Final Block
-    m_seedTxnBlksBuffer.push_back(message);
-    return false;
-  } else if (!m_seedTxnBlksBuffer.empty() && !buffered) {
-    if (LOOKUP_NODE_MODE && ARCHIVAL_LOOKUP) {
-      // If seed node is synced and have buffer txn blocks
-      for (auto& txnblk : m_seedTxnBlksBuffer) {
-        ProcessFinalBlockCore(txnblk, offset, Peer(), true);
+  if (LOOKUP_NODE_MODE && ARCHIVAL_LOOKUP && !buffered) {
+    if (m_mediator.m_lookup->GetSyncType() != SyncType::NO_SYNC) {
+      // Buffer the Final Block
+      lock_guard<mutex> g(m_mutexSeedTxnBlksBuffer);
+      m_seedTxnBlksBuffer.push_back(message);
+      LOG_GENERAL(INFO, "Seed not yet synced, so buffered this final block");
+      return false;
+    } else {
+      // If seed node is synced and have buffered txn blocks
+      lock_guard<mutex> g(m_mutexSeedTxnBlksBuffer);
+      if (!m_seedTxnBlksBuffer.empty()) {
+        LOG_GENERAL(INFO,
+                    "Seed is synced, so processing buffered final blocks");
+        for (auto& txnblk : m_seedTxnBlksBuffer) {
+          ProcessFinalBlockCore(txnblk, offset, Peer(), true);
+        }
+        // clear the buffer since all buffered ones are checked and processed
+        m_seedTxnBlksBuffer.clear();
       }
     }
-    // clear the buffer anyways
-    m_seedTxnBlksBuffer.clear();
   }
 
+  lock_guard<mutex> g(m_mutexFinalBlock);
   if (txBlock.GetHeader().GetVersion() != TXBLOCK_VERSION) {
     LOG_CHECK_FAIL("TxBlock version", txBlock.GetHeader().GetVersion(),
                    TXBLOCK_VERSION);
```

### src/libNode/Node.h
```diff
@@ -102,6 +102,7 @@ class Node : public Executable {
 
   // Final Block Buffer for seed node
   std::vector<bytes> m_seedTxnBlksBuffer;
+  std::mutex m_mutexSeedTxnBlksBuffer;
 
   // Persistence Retriever
   std::shared_ptr<Retriever> m_retriever;
```
