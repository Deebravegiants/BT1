# [?] avoid deadlock issue

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2021-05-04
Source: https://github.com/Zilliqa/zq1/commit/ed487e47482d2d834d8d614cb0dd675731cb5eda
Type: security-commit

## Details
avoid deadlock issue

address comments

temporary commenting to repoduce issue

reverted temp commenting out

## Patch
### src/libNode/DSBlockProcessing.cpp
```diff
@@ -349,7 +349,7 @@ void Node::StartFirstTxEpoch(bool fbWaitState) {
   }
 
   // CommitTxnPacketBuffer();
-
+  m_txn_distribute_window_open = true;
   if (fbWaitState) {
     SetState(WAITING_FINALBLOCK);
     CleanMicroblockConsensusBuffer();
```

### src/libNode/Node.cpp
```diff
@@ -2351,23 +2351,36 @@ void Node::CleanCreatedTransaction() {
     std::lock_guard<mutex> g(m_mutexCreatedTransactions);
     m_createdTxns.clear();
     t_createdTxns.clear();
+    LOG_GENERAL(INFO, "Cleaned created txns!");
   }
-  {
-    std::lock_guard<mutex> g(m_mutexTxnPacketBuffer);
-    m_txnPacketBuffer.clear();
-  }
-  {
-    std::lock_guard<mutex> g(m_mutexTxnPktInProcess);
-    m_txnPktInProcess.clear();
+  // Avoid cleaning when buffer already have packets waiting to be picked up for
+  // distribution. Thus avoid deadlock.
+  if (m_txnPacketThreadOnHold == 0) {
+    {
+      // extra safety
+      std::unique_lock<std::mutex> lock(m_mutexTxnPacketBuffer,
+                                        std::try_to_lock);
+      if (lock.owns_lock()) {
+        m_txnPacketBuffer.clear();
+        LOG_GENERAL(INFO, "Cleaned txn pkt buffer!");
+      }
+    }
+    {
+      std::lock_guard<mutex> g(m_mutexTxnPktInProcess);
+      m_txnPktInProcess.clear();
+      LOG_GENERAL(INFO, "Cleaned txnPktInProcess buffer!");
+    }
   }
   {
     std::lock_guard<mutex> lock(m_mutexProcessedTransactions);
     m_processedTransactions.clear();
     t_processedTransactions.clear();
+    LOG_GENERAL(INFO, "Cleaned processed txns!");
   }
   {
     std::unique_lock<shared_timed_mutex> lock(m_unconfirmedTxnsMutex);
     m_unconfirmedTxns.clear();
+    LOG_GENERAL(INFO, "Cleaned unconfirmed txns!");
   }
   m_TxnOrder.clear();
   m_gasUsedTotal = 0;
```
