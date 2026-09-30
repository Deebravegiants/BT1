# [?] Fix crash on exit in ~InboundLedger

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2014-02-08
Source: https://github.com/XRPLF/rippled/commit/9c5b0715560c82f3753f4f27405e7a04ec56be87
Type: security-commit

## Details
Fix crash on exit in ~InboundLedger

## Patch
### src/ripple_app/main/Application.cpp
```diff
@@ -127,13 +127,13 @@ class ApplicationImp
     OrderBookDB m_orderBookDB;
     std::unique_ptr <PathRequests> m_pathRequests;
     std::unique_ptr <LedgerMaster> m_ledgerMaster;
+    std::unique_ptr <InboundLedgers> m_inboundLedgers;
     std::unique_ptr <NetworkOPs> m_networkOPs;
     std::unique_ptr <UniqueNodeList> m_deprecatedUNL;
     std::unique_ptr <RPCHTTPServer> m_rpcHTTPServer;
     RPCServerHandler m_rpcServerHandler;
     std::unique_ptr <NodeStore::Database> m_nodeStore;
     std::unique_ptr <SNTPClient> m_sntpClient;
-    std::unique_ptr <InboundLedgers> m_inboundLedgers;
     std::unique_ptr <TxQueue> m_txQueue;
     std::unique_ptr <Validators::Manager> m_validators;
     std::unique_ptr <IFeatures> mFeatures;
@@ -261,6 +261,11 @@ class ApplicationImp
         , m_ledgerMaster (LedgerMaster::New (
             *m_jobQueue, LogPartition::getJournal <LedgerMaster> ()))
 
+        // VFALCO NOTE must come before NetworkOPs to prevent a crash due
+        //             to dependencies in the destructor.
+        //
+        , m_inboundLedgers (InboundLedgers::New (get_seconds_clock (), *m_jobQueue))
+
         // VFALCO NOTE Does NetworkOPs depend on LedgerMaster?
         , m_networkOPs (NetworkOPs::New (get_seconds_clock (), *m_ledgerMaster,
             *m_jobQueue, LogPartition::getJournal <NetworkOPsLog> ()))
@@ -279,8 +284,6 @@ class ApplicationImp
 
         , m_sntpClient (SNTPClient::New (*this))
 
-        , m_inboundLedgers (InboundLedgers::New (get_seconds_clock (), *m_jobQueue))
-
         , m_txQueue (TxQueue::New ())
 
         , m_validators (add (Validators::Manager::New (
```
