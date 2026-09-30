# [?] Fix crash when do DS node rejoin

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2018-11-14
Source: https://github.com/Zilliqa/zq1/commit/377898b553aa019ee8d7795314d193827a63c823
Type: security-commit

## Details
Fix crash when do DS node rejoin

## Patch
### src/libLookup/Lookup.cpp
```diff
@@ -1698,7 +1698,8 @@ void Lookup::CommitTxBlocks(const vector<TxBlock>& txBlocks) {
 
   if ((m_mediator.m_currentEpochNum % NUM_FINAL_BLOCK_PER_POW == 0) &&
       !ARCHIVAL_NODE) {
-    LOG_GENERAL(INFO, "At new DS epoch now, try getting state from lookup");
+    LOG_EPOCH(INFO, to_string(m_mediator.m_currentEpochNum).c_str(),
+              "At new DS epoch now, try getting state from lookup");
     GetStateFromLookupNodes();
   }
 
```

### src/libNode/Node.cpp
```diff
@@ -79,16 +79,17 @@ Node::Node(Mediator& mediator, [[gnu::unused]] unsigned int syncType,
 
 Node::~Node() {}
 
-bool Node::Install(unsigned int syncType, bool toRetrieveHistory) {
+bool Node::Install(SyncType syncType, bool toRetrieveHistory) {
   LOG_MARKER();
 
   // m_state = IDLE;
   bool runInitializeGenesisBlocks = true;
 
   if (toRetrieveHistory) {
     bool wakeupForUpgrade = false;
+    bool retrieveSuccessButTooLate = false;
 
-    if (StartRetrieveHistory(wakeupForUpgrade)) {
+    if (StartRetrieveHistory(wakeupForUpgrade, retrieveSuccessButTooLate)) {
       m_mediator.m_currentEpochNum =
           m_mediator.m_txBlockChain.GetLastBlock().GetHeader().GetBlockNum() +
           1;
@@ -164,6 +165,13 @@ bool Node::Install(unsigned int syncType, bool toRetrieveHistory) {
         return true;
       }
     }
+
+    // When do node recovery, if retrieve the history success, then shouldn't
+    // continue to run add genesis account, but let the node to synchronize with
+    // lookup node.
+    if (retrieveSuccessButTooLate) {
+      return true;
+    }
   }
 
   if (runInitializeGenesisBlocks) {
@@ -232,7 +240,8 @@ void Node::Prepare(bool runInitializeGenesisBlocks) {
       m_mediator.m_dsBlockChain.GetLastBlock().GetHeader().GetBlockNum() + 1);
 }
 
-bool Node::StartRetrieveHistory(bool& wakeupForUpgrade) {
+bool Node::StartRetrieveHistory(bool& wakeupForUpgrade,
+                                bool& retrieveSuccessButTooLate) {
   LOG_MARKER();
 
   m_mediator.m_txBlockChain.Reset();
@@ -312,6 +321,7 @@ bool Node::StartRetrieveHistory(bool& wakeupForUpgrade) {
     }
 
     if (m_mediator.m_txBlockChain.GetBlockCount() > oldTxNum + 1) {
+      retrieveSuccessButTooLate = true;
       LOG_GENERAL(INFO,
                   "Node recovery too late, apply re-join process instead");
       return false;
@@ -1118,7 +1128,7 @@ void Node::RejoinAsNormal() {
     auto func = [this]() mutable -> void {
       m_mediator.m_lookup->m_syncType = SyncType::NORMAL_SYNC;
       this->CleanVariables();
-      this->Install(true);
+      this->Install(SyncType::NORMAL_SYNC);
       this->StartSynchronization();
       this->ResetRejoinFlags();
     };
```

### src/libNode/Node.h
```diff
@@ -429,7 +429,7 @@ class Node : public Executable, public Broadcastable {
   ~Node();
 
   /// Install the Node
-  bool Install(unsigned int syncType, bool toRetrieveHistory = true);
+  bool Install(SyncType syncType, bool toRetrieveHistory = true);
 
   /// Set initial state, variables, and clean-up storage
   void Init();
@@ -460,7 +460,8 @@ class Node : public Executable, public Broadcastable {
   Mediator& GetMediator() { return m_mediator; }
 
   /// Recover the previous state by retrieving persistence data
-  bool StartRetrieveHistory(bool& wakeupForUpgrade);
+  bool StartRetrieveHistory(bool& wakeupForUpgrade,
+                            bool& retrieveSuccessButTooLate);
 
   // Erase m_committedTransactions for given epoch number
   // void EraseCommittedTransactions(uint64_t epochNum)
```

### src/libZilliqa/Zilliqa.cpp
```diff
@@ -141,7 +141,7 @@ Zilliqa::Zilliqa(const std::pair<PrivKey, PubKey>& key, const Peer& peer,
   P2PComm::GetInstance().SetSelfPeer(peer);
 
   auto func = [this, toRetrieveHistory, syncType, key, peer]() mutable -> void {
-    if (!m_n.Install(syncType, toRetrieveHistory)) {
+    if (!m_n.Install((SyncType)syncType, toRetrieveHistory)) {
       if (LOOKUP_NODE_MODE) {
         syncType = SyncType::LOOKUP_SYNC;
       } else {
```
