# [?] Fix recovered lookup start to listening crash

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2019-09-11
Source: https://github.com/Zilliqa/zq1/commit/38a1bc6d29b8ea664e220c10dd08a9c8fdfc763c
Type: security-commit

## Details
Fix recovered lookup start to listening crash

## Patch
### src/libLookup/Lookup.cpp
```diff
@@ -2108,10 +2108,12 @@ void Lookup::CommitTxBlocks(const vector<TxBlock>& txBlocks) {
         if (FinishRejoinAsLookup()) {
           SetSyncType(SyncType::NO_SYNC);
 
-          if (m_lookupServer->StartListening()) {
-            LOG_GENERAL(INFO, "API Server started to listen again");
-          } else {
-            LOG_GENERAL(WARNING, "API Server couldn't start");
+          if (m_lookupServer) {
+            if (m_lookupServer->StartListening()) {
+              LOG_GENERAL(INFO, "API Server started to listen again");
+            } else {
+              LOG_GENERAL(WARNING, "API Server couldn't start");
+            }
           }
         }
       }
@@ -2139,10 +2141,12 @@ void Lookup::CommitTxBlocks(const vector<TxBlock>& txBlocks) {
         SetSyncType(SyncType::NO_SYNC);
         m_isFirstLoop = true;
 
-        if (m_lookupServer->StartListening()) {
-          LOG_GENERAL(INFO, "API Server started to listen again");
-        } else {
-          LOG_GENERAL(WARNING, "API Server couldn't start");
+        if (m_lookupServer) {
+          if (m_lookupServer->StartListening()) {
+            LOG_GENERAL(INFO, "API Server started to listen again");
+          } else {
+            LOG_GENERAL(WARNING, "API Server couldn't start");
+          }
         }
       }
       m_currDSExpired = false;
@@ -2389,10 +2393,12 @@ bool Lookup::ProcessSetStateFromSeed(const bytes& message, unsigned int offset,
       if (FinishRejoinAsLookup()) {
         SetSyncType(SyncType::NO_SYNC);
 
-        if (m_lookupServer->StartListening()) {
-          LOG_GENERAL(INFO, "API Server started to listen again");
-        } else {
-          LOG_GENERAL(WARNING, "API Server couldn't start");
+        if (m_lookupServer) {
+          if (m_lookupServer->StartListening()) {
+            LOG_GENERAL(INFO, "API Server started to listen again");
+          } else {
+            LOG_GENERAL(WARNING, "API Server couldn't start");
+          }
         }
       }
     }
@@ -2427,10 +2433,12 @@ bool Lookup::ProcessSetStateFromSeed(const bytes& message, unsigned int offset,
       SetSyncType(SyncType::NO_SYNC);
       m_isFirstLoop = true;
 
-      if (m_lookupServer->StartListening()) {
-        LOG_GENERAL(INFO, "API Server started to listen again");
-      } else {
-        LOG_GENERAL(WARNING, "API Server couldn't start");
+      if (m_lookupServer) {
+        if (m_lookupServer->StartListening()) {
+          LOG_GENERAL(INFO, "API Server started to listen again");
+        } else {
+          LOG_GENERAL(WARNING, "API Server couldn't start");
+        }
       }
     }
     m_currDSExpired = false;
```
