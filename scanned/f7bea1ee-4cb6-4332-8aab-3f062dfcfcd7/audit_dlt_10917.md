# [?] Fixed race condition between shard txns dispatch and deletion

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2021-01-26
Source: https://github.com/Zilliqa/zq1/commit/60a6247202f0f901d64c45b2a0c4cf4039983745
Type: security-commit

## Details
Fixed race condition between shard txns dispatch and deletion

## Patch
### constants.xml
```diff
@@ -314,6 +314,7 @@
         <ENABLE_TXNS_BACKUP>false</ENABLE_TXNS_BACKUP>
         <SHARDLDR_SAVE_TXN_LOCALLY>false</SHARDLDR_SAVE_TXN_LOCALLY>
         <BLOOM_FILTER_FALSE_RATE>0.000001</BLOOM_FILTER_FALSE_RATE>
+        <TXN_DISPATCH_ATTEMPT_LIMIT>3</TXN_DISPATCH_ATTEMPT_LIMIT>
     </transactions>
     <verifier>
         <exclusion_list>
```

### constants_local.xml
```diff
@@ -313,6 +313,7 @@
         <ENABLE_TXNS_BACKUP>false</ENABLE_TXNS_BACKUP>
         <SHARDLDR_SAVE_TXN_LOCALLY>false</SHARDLDR_SAVE_TXN_LOCALLY>
         <BLOOM_FILTER_FALSE_RATE>0.000001</BLOOM_FILTER_FALSE_RATE>
+        <TXN_DISPATCH_ATTEMPT_LIMIT>3</TXN_DISPATCH_ATTEMPT_LIMIT>
     </transactions>
     <verifier>
         <exclusion_list>
```

### src/common/Constants.cpp
```diff
@@ -626,6 +626,8 @@ const bool SHARDLDR_SAVE_TXN_LOCALLY{
     "true"};
 const double BLOOM_FILTER_FALSE_RATE{
     ReadConstantDouble("BLOOM_FILTER_FALSE_RATE", "node.transactions.")};
+const unsigned int TXN_DISPATCH_ATTEMPT_LIMIT{
+    ReadConstantNumeric("TXN_DISPATCH_ATTEMPT_LIMIT", "node.transactions.")};
 
 // Viewchange constants
 const unsigned int POST_VIEWCHANGE_BUFFER{
```

### src/common/Constants.h
```diff
@@ -420,6 +420,7 @@ extern const std::string TXN_PERSISTENCE_NAME;
 extern const bool ENABLE_TXNS_BACKUP;
 extern const bool SHARDLDR_SAVE_TXN_LOCALLY;
 extern const double BLOOM_FILTER_FALSE_RATE;
+extern const unsigned int TXN_DISPATCH_ATTEMPT_LIMIT;
 
 // Viewchange constants
 extern const unsigned int POST_VIEWCHANGE_BUFFER;
```

### src/libLookup/Lookup.cpp
```diff
@@ -429,7 +429,7 @@ bool Lookup::GenTxnToSend(size_t num_txn, vector<Transaction>& shardTxn,
 }
 
 bool Lookup::GenTxnToSend(size_t num_txn,
-                          map<uint32_t, vector<Transaction>>& mp,
+                          map<uint32_t, deque<pair<Transaction, uint32_t>>>& mp,
                           uint32_t numShards) {
   LOG_MARKER();
   vector<Transaction> txns;
@@ -472,7 +472,9 @@ bool Lookup::GenTxnToSend(size_t num_txn,
       continue;
     }
 
-    copy(txns.begin(), txns.end(), back_inserter(mp[txnShard]));
+    for (const auto& txn : txns) {
+      mp[txnShard].emplace_back(make_pair(txn, 0));
+    }
 
     LOG_GENERAL(INFO, "[Batching] Last Nonce sent "
                           << nonce + num_txn << " of Addr " << addr.hex());
@@ -488,7 +490,9 @@ bool Lookup::GenTxnToSend(size_t num_txn,
       LOG_GENERAL(WARNING, "Failed to get txns for DS");
     }
 
-    copy(txns.begin(), txns.end(), back_inserter(mp[numShards]));
+    for (const auto& txn : txns) {
+      mp[numShards].emplace_back(make_pair(txn, 0));
+    }
   }
 
   return true;
@@ -3429,7 +3433,7 @@ void Lookup::FindMissingMBsForLastNTxBlks(const uint32_t& num) {
   }
 }
 
-const vector<Transaction>& Lookup::GetTxnFromShardMap(uint32_t index) {
+deque<pair<Transaction, uint32_t>>& Lookup::GetTxnFromShardMap(uint32_t index) {
   return m_txnShardMap[index];
 }
 
@@ -5287,14 +5291,14 @@ bool Lookup::AddToTxnShardMap(const Transaction& tx, uint32_t shardId,
 
   // case where txn already exist
   if (find_if(txnShardMap[shardId].begin(), txnShardMap[shardId].end(),
-              [tx](const Transaction& txn) {
-                return tx.GetTranID() == txn.GetTranID();
+              [tx](const pair<Transaction, uint32_t>& txn_and_count) {
+                return tx.GetTranID() == txn_and_count.first.GetTranID();
               }) != txnShardMap[shardId].end()) {
     LOG_GENERAL(WARNING, "Same hash present " << tx.GetTranID());
     return false;
   }
 
-  txnShardMap[shardId].push_back(tx);
+  txnShardMap[shardId].emplace_back(make_pair(tx, 0));
   LOG_GENERAL(INFO, "Added Txn " << tx.GetTranID().hex() << " to shard "
                                  << shardId << " of fromAddr "
                                  << tx.GetSenderAddr());
@@ -5366,7 +5370,7 @@ void Lookup::RectifyTxnShardMap(const uint32_t oldNumShards,
 
   auto t_start = std::chrono::high_resolution_clock::now();
 
-  map<uint, vector<Transaction>> tempTxnShardMap;
+  map<uint, deque<pair<Transaction, uint32_t>>> tempTxnShardMap;
 
   lock_guard<mutex> g(m_txnShardMapMutex);
 
@@ -5378,21 +5382,22 @@ void Lookup::RectifyTxnShardMap(const uint32_t oldNumShards,
       // ds txns
       continue;
     }
-    for (const auto& tx : shard.second) {
-      unsigned int fromShard = tx.GetShardIndex(newNumShards);
+    for (const auto& tx_and_count : shard.second) {
+      unsigned int fromShard = tx_and_count.first.GetShardIndex(newNumShards);
 
-      if (Transaction::GetTransactionType(tx) == Transaction::CONTRACT_CALL) {
+      if (Transaction::GetTransactionType(tx_and_count.first) ==
+          Transaction::CONTRACT_CALL) {
         // if shard do not match directly send to ds
-        unsigned int toShard =
-            Transaction::GetShardIndex(tx.GetToAddr(), newNumShards);
+        unsigned int toShard = Transaction::GetShardIndex(
+            tx_and_count.first.GetToAddr(), newNumShards);
         if (toShard != fromShard) {
           // later would be placed in the new ds shard
-          m_txnShardMap[oldNumShards].emplace_back(tx);
+          m_txnShardMap[oldNumShards].emplace_back(tx_and_count);
           continue;
         }
       }
 
-      tempTxnShardMap[fromShard].emplace_back(tx);
+      tempTxnShardMap[fromShard].emplace_back(tx_and_count);
     }
   }
   tempTxnShardMap[newNumShards] = move(m_txnShardMap[oldNumShards]);
@@ -5427,7 +5432,7 @@ void Lookup::SendTxnPacketToNodes(const uint32_t oldNumShards,
 
   const uint32_t numShards = newNumShards;
 
-  map<uint32_t, vector<Transaction>> mp;
+  map<uint32_t, deque<pair<Transaction, uint32_t>>> mp;
 
   if (!GenTxnToSend(NUM_TXN_TO_SEND_PER_ACCOUNT, mp, numShards)) {
     LOG_GENERAL(WARNING, "GenTxnToSend failed");
@@ -5450,6 +5455,7 @@ void Lookup::SendTxnPacketToNodes(const uint32_t oldNumShards,
 
     {
       lock_guard<mutex> g(m_txnShardMapMutex);
+
       auto transactionNumber = mp[i].size();
 
       LOG_GENERAL(INFO, "Txn number generated: " << transactionNumber);
@@ -5477,6 +5483,7 @@ void Lookup::SendTxnPacketToNodes(const uint32_t oldNumShards,
       LOG_GENERAL(WARNING, "Cannot create packet for " << i << " shard");
       continue;
     }
+
     vector<Peer> toSend;
     if (i < numShards) {
       {
@@ -5509,9 +5516,6 @@ void Lookup::SendTxnPacketToNodes(const uint32_t oldNumShards,
       }
 
       P2PComm::GetInstance().SendBroadcastMessage(toSend, msg);
-
-      lock_guard<mutex> g(m_txnShardMapMutex);
-      DeleteTxnShardMap(i);
     } else if (i == numShards) {
       // To send DS
       {
@@ -5545,9 +5549,6 @@ void Lookup::SendTxnPacketToNodes(const uint32_t oldNumShards,
 
       LOG_GENERAL(INFO, "[DSMB]"
                             << " Sent DS the txns");
-
-      lock_guard<mutex> g(m_txnShardMapMutex);
-      DeleteTxnShardMap(i);
     }
   }
 }
```

### src/libLookup/Lookup.h
```diff
@@ -54,7 +54,8 @@ class StakingServer;
 // The "first" element in the pair is a map of shard to its transactions
 // The "second" element in the pair counts the total number of transactions in
 // the whole map
-using TxnShardMap = std::map<uint32_t, std::vector<Transaction>>;
+using TxnShardMap =
+    std::map<uint32_t, std::deque<std::pair<Transaction, uint32_t>>>;
 
 // Enum used to tell send type to seed node
 enum SEND_TYPE { ARCHIVAL_SEND_SHARD = 0, ARCHIVAL_SEND_DS };
@@ -193,7 +194,7 @@ class Lookup : public Executable {
 
   std::mutex m_txnShardMapMutex;
 
-  const std::vector<Transaction>& GetTxnFromShardMap(
+  std::deque<std::pair<Transaction, uint32_t>>& GetTxnFromShardMap(
       uint32_t index);  // Use m_txnShardMapMutex with this function
 
   std::mutex m_mutexShardStruct;
@@ -206,9 +207,10 @@ class Lookup : public Executable {
   bool IsLookupNode(const Peer& peerInfo) const;
 
   // Gen n valid txns
-  bool GenTxnToSend(size_t num_txn,
-                    std::map<uint32_t, std::vector<Transaction>>& mp,
-                    uint32_t numShards);
+  bool GenTxnToSend(
+      size_t num_txn,
+      std::map<uint32_t, std::deque<std::pair<Transaction, uint32_t>>>& mp,
+      uint32_t numShards);
   bool GenTxnToSend(size_t num_txn, std::vector<Transaction>& shardTxn,
                     std::vector<Transaction>& DSTxn);
 
```

### src/libMessage/Messenger.cpp
```diff
@@ -1260,13 +1260,21 @@ void ProtobufToTransactionOffset(const ProtoTxnFileOffset& protoTxnFileOffset,
   }
 }
 
-void TransactionArrayToProtobuf(const std::vector<Transaction>& txns,
+void TransactionArrayToProtobuf(const vector<Transaction>& txns,
                                 ProtoTransactionArray& protoTransactionArray) {
   for (const auto& txn : txns) {
     TransactionToProtobuf(txn, *protoTransactionArray.add_transactions());
   }
 }
 
+void TransactionArrayToProtobuf(const deque<pair<Transaction, uint32_t>>& txns,
+                                ProtoTransactionArray& protoTransactionArray) {
+  for (const auto& txn_and_count : txns) {
+    TransactionToProtobuf(txn_and_count.first,
+                          *protoTransactionArray.add_transactions());
+  }
+}
+
 bool ProtobufToTransactionArray(
     const ProtoTransactionArray& protoTransactionArray,
     std::vector<Transaction>& txns) {
@@ -4981,8 +4989,9 @@ bool Messenger::GetNodeVCBlock(const bytes& src, const unsigned int offset,
 bool Messenger::SetNodeForwardTxnBlock(
     bytes& dst, const unsigned int offset, const uint64_t& epochNumber,
     const uint64_t& dsBlockNum, const uint32_t& shardId,
-    const PairOfKey& lookupKey, const std::vector<Transaction>& txnsCurrent,
-    const std::vector<Transaction>& txnsGenerated) {
+    const PairOfKey& lookupKey,
+    deque<std::pair<Transaction, uint32_t>>& txnsCurrent,
+    deque<std::pair<Transaction, uint32_t>>& txnsGenerated) {
   LOG_MARKER();
 
   NodeForwardTxnBlock result;
@@ -4994,38 +5003,54 @@ bool Messenger::SetNodeForwardTxnBlock(
 
   unsigned int txnsCurrentCount = 0, txnsGeneratedCount = 0, msg_size = 0;
 
-  for (const auto& txn : txnsCurrent) {
+  for (auto txn = txnsCurrent.begin(); txn != txnsCurrent.end();) {
     if (msg_size >= PACKET_BYTESIZE_LIMIT) {
       break;
     }
 
     auto protoTxn = std::make_unique<ProtoTransaction>();
-    TransactionToProtobuf(txn, *protoTxn);
+    TransactionToProtobuf(txn->first, *protoTxn);
     unsigned txn_size = protoTxn->ByteSize();
     if ((msg_size + txn_size) > PACKET_BYTESIZE_LIMIT &&
         txn_size >= SMALL_TXN_SIZE) {
+      if (++(txn->second) >= TXN_DISPATCH_ATTEMPT_LIMIT) {
+        LOG_GENERAL(WARNING,
+                    "Failed to dispatch txn " << txn->first.GetTranID());
+        txn = txnsCurrent.erase(txn);
+      } else {
+        txn++;
+      }
       continue;
     }
     *result.add_transactions() = *protoTxn;
     txnsCurrentCount++;
     msg_size += protoTxn->ByteSize();
+    txn = txnsCurrent.erase(txn);
   }
 
-  for (const auto& txn : txnsGenerated) {
+  for (auto txn = txnsGenerated.begin(); txn != txnsGenerated.end();) {
     if (msg_size >= PACKET_BYTESIZE_LIMIT) {
       break;
     }
 
     auto protoTxn = std::make_unique<ProtoTransaction>();
-    TransactionToProtobuf(txn, *protoTxn);
+    TransactionToProtobuf(txn->first, *protoTxn);
     unsigned txn_size = protoTxn->ByteSize();
     if ((msg_size + txn_size) > PACKET_BYTESIZE_LIMIT &&
         txn_size >= SMALL_TXN_SIZE) {
+      if (++(txn->second) >= TXN_DISPATCH_ATTEMPT_LIMIT) {
+        LOG_GENERAL(WARNING,
+                    "Failed to dispatch txn " << txn->first.GetTranID());
+        txn = txnsCurrent.erase(txn);
+      } else {
+        txn++;
+      }
       continue;
     }
     *result.add_transactions() = *protoTxn;
     txnsGeneratedCount++;
     msg_size += txn_size;
+    txn = txnsGenerated.erase(txn);
   }
 
   Signature signature;
@@ -7158,8 +7183,8 @@ bool Messenger::GetLookupSetStartPoWFromSeed(const bytes& src,
 
 bool Messenger::SetForwardTxnBlockFromSeed(
     bytes& dst, const unsigned int offset,
-    const vector<Transaction>& shardTransactions,
-    const vector<Transaction>& dsTransactions) {
+    const deque<pair<Transaction, uint32_t>>& shardTransactions,
+    const deque<pair<Transaction, uint32_t>>& dsTransactions) {
   LookupForwardTxnsFromSeed result;
 
   if (!shardTransactions.empty()) {
```

### src/libMessage/Messenger.h
```diff
@@ -418,8 +418,9 @@ class Messenger {
   static bool SetNodeForwardTxnBlock(
       bytes& dst, const unsigned int offset, const uint64_t& epochNumber,
       const uint64_t& dsBlockNum, const uint32_t& shardId,
-      const PairOfKey& lookupKey, const std::vector<Transaction>& txnsCurrent,
-      const std::vector<Transaction>& txnsGenerated);
+      const PairOfKey& lookupKey,
+      std::deque<std::pair<Transaction, uint32_t>>& txnsCurrent,
+      std::deque<std::pair<Transaction, uint32_t>>& txnsGenerated);
   static bool SetNodeForwardTxnBlock(bytes& dst, const unsigned int offset,
                                      const uint64_t& epochNumber,
                                      const uint64_t& dsBlockNum,
@@ -690,8 +691,8 @@ class Messenger {
 
   static bool SetForwardTxnBlockFromSeed(
       bytes& dst, const unsigned int offset,
-      const std::vector<Transaction>& shardTransactions,
-      const std::vector<Transaction>& dsTransactions);
+      const std::deque<std::pair<Transaction, uint32_t>>& shardTransactions,
+      const std::deque<std::pair<Transaction, uint32_t>>& dsTransactions);
 
   static bool GetForwardTxnBlockFromSeed(
       const bytes& src, const unsigned int offset,
```

### src/libUtils/GetTxnFromFile.h
```diff
@@ -72,7 +72,7 @@ bool getTransactionsFromFile(std::fstream& f, unsigned int startNum,
       LOG_GENERAL(WARNING, "Messenger::GetTransaction failed.");
       return false;
     }
-    txns.push_back(txn);
+    txns.emplace_back(txn);
   }
 
   return true;
```

### tests/Lookup/Test_txn_send.cpp
```diff
@@ -51,13 +51,14 @@ void test_transaction(const map<uint32_t, vector<Transaction>>& mp,
   lk.RectifyTxnShardMap(oldNumShard, newShardNum);
 
   for (uint k = 0; k <= newShardNum; k++) {
-    const auto txns = lk.GetTxnFromShardMap(k);
-    for (const auto& tx : txns) {
-      const auto& fromShard = tx.GetShardIndex(newShardNum);
+    const auto& txns = lk.GetTxnFromShardMap(k);
+    for (const auto& tx_and_count : txns) {
+      const auto& fromShard = tx_and_count.first.GetShardIndex(newShardNum);
       auto index = fromShard;
-      if (Transaction::GetTransactionType(tx) == Transaction::CONTRACT_CALL) {
-        const auto& toShard =
-            Transaction::GetShardIndex(tx.GetToAddr(), newShardNum);
+      if (Transaction::GetTransactionType(tx_and_count.first) ==
+          Transaction::CONTRACT_CALL) {
+        const auto& toShard = Transaction::GetShardIndex(
+            tx_and_count.first.GetToAddr(), newShardNum);
         if (toShard != fromShard) {
           LOG_GENERAL(INFO, "Sent to ds");
           index = newShardNum;
```
