# [?] Fixing miner crashes by adding support for spending unconfirmed outputs

## Summary
Severity: Unknown
Chain: Litecoin
Component: litecoin-project/litecoin
Published: 2022-04-04
Source: https://github.com/litecoin-project/litecoin/commit/e07a311aeb87cc9b86c90be9e3355305a9d7da3f
Type: security-commit

## Details
Fixing miner crashes by adding support for spending unconfirmed outputs

## Patch
### src/libmw/include/mw/node/BlockBuilder.h
```diff
@@ -20,7 +20,7 @@ class BlockBuilder
     /// <param name="view">The CoinsView representing the latest state of the active chain. Must not be null.</param>
     /// <returns>A non-null BlockBuilder</returns>
     BlockBuilder(const uint64_t height, const mw::ICoinsView::Ptr& pCoinsView)
-        : m_height(height), m_weight(0), m_pCoinsView(std::make_shared<mw::CoinsViewCache>(pCoinsView)), m_pAggregated(nullptr){ }
+        : m_height(height), m_weight(0), m_pCoinsView(std::make_shared<mw::CoinsViewCache>(pCoinsView)) { }
 
     bool AddTransaction(const Transaction::CPtr& pTransaction, const std::vector<PegInCoin>& pegins);
 
@@ -30,7 +30,9 @@ class BlockBuilder
     uint64_t m_height;
     uint64_t m_weight;
     mw::CoinsViewCache::Ptr m_pCoinsView;
-    Transaction::CPtr m_pAggregated;
+
+    std::vector<Transaction::CPtr> m_stagedTxs;
+    std::set<Hash> m_stagedOutputs;
 };
 
 END_NAMESPACE // mw
\ No newline at end of file
```

### src/libmw/src/node/BlockBuilder.cpp
```diff
@@ -1,5 +1,4 @@
 #include <mw/node/BlockBuilder.h>
-#include <mw/consensus/Aggregation.h>
 #include <mw/consensus/KernelSumValidator.h>
 #include <mw/consensus/Params.h>
 #include <mw/consensus/Weight.h>
@@ -62,7 +61,12 @@ bool BlockBuilder::AddTransaction(const Transaction::CPtr& pTransaction, const s
 
     // Make sure all inputs are available.
     for (const Input& input : pTransaction->GetInputs()) {
-        if (!m_pCoinsView->HasCoin(input.GetOutputID())) {
+        //if (m_stagedInputs.count(input.GetOutputID()) > 0) { // MW: TODO - Is this necessary, or are duplicate output checks enough?
+        //    LOG_ERROR_F("Input {} already staged", input.GetOutputID());
+        //    return false;
+        //}
+
+        if (!m_pCoinsView->HasCoin(input.GetOutputID()) && m_stagedOutputs.count(input.GetOutputID()) == 0) {
             LOG_ERROR_F("Input {} not found on chain", input.GetOutputID());
             return false;
         }
@@ -74,35 +78,27 @@ bool BlockBuilder::AddTransaction(const Transaction::CPtr& pTransaction, const s
             LOG_ERROR_F("Output {} already on chain", output.GetOutputID());
             return false;
         }
-    }
 
-    // Aggregate transactions
-    auto pAggregated = pTransaction;
-    if (m_pAggregated != nullptr) {
-        pAggregated = Aggregation::Aggregate({ m_pAggregated, pTransaction });
+        if (m_stagedOutputs.count(output.GetOutputID()) > 0) {
+            LOG_ERROR_F("Output {} already staged", output.GetOutputID());
+            return false;
+        }
     }
 
-    if (pAggregated == nullptr) {
-        LOG_ERROR("Failed to aggregate transaction");
-        return false;
-    }
+    m_stagedTxs.push_back(pTransaction);
+    m_weight += weight;
 
-    m_pAggregated = pAggregated;
-    m_weight = Weight::Calculate(pAggregated->GetBody());
+    for (const Output& output : pTransaction->GetOutputs()) {
+        auto inserted = m_stagedOutputs.insert(output.GetOutputID());
+        assert(inserted.second);
+    }
 
     return true;
 }
 
 mw::Block::Ptr BlockBuilder::BuildBlock() const
 {
-    mw::CoinsViewCache cache(m_pCoinsView);
-
-    std::vector<mw::Transaction::CPtr> txs;
-    if (m_pAggregated != nullptr) {
-        txs.push_back(m_pAggregated);
-    }
-
-    return cache.BuildNextBlock(m_height, txs);
+    return mw::CoinsViewCache(m_pCoinsView).BuildNextBlock(m_height, m_stagedTxs);
 }
 
 END_NAMESPACE
\ No newline at end of file
```

### src/libmw/src/node/CoinsViewCache.cpp
```diff
@@ -78,16 +78,16 @@ static const uint32_t MEMPOOL_HEIGHT = 0x7FFFFFFF;
 void CoinsViewCache::AddTx(const mw::Transaction::CPtr& pTx)
 {
     std::for_each(
-        pTx->GetInputs().cbegin(), pTx->GetInputs().cend(),
-        [this](const Input& input) {
-            SpendUTXO(input.GetOutputID());
+        pTx->GetOutputs().cbegin(), pTx->GetOutputs().cend(),
+        [this](const Output& output) {
+            AddUTXO(MEMPOOL_HEIGHT, output);
         }
     );
 
     std::for_each(
-        pTx->GetOutputs().cbegin(), pTx->GetOutputs().cend(),
-        [this](const Output& output) {
-            AddUTXO(MEMPOOL_HEIGHT, output);
+        pTx->GetInputs().cbegin(), pTx->GetInputs().cend(),
+        [this](const Input& input) {
+            SpendUTXO(input.GetOutputID());
         }
     );
 }
```

### src/miner.cpp
```diff
@@ -229,7 +229,7 @@ bool BlockAssembler::TestPackage(uint64_t packageSize, int64_t packageSigOpsCost
 // - transaction finality (locktime)
 // - premature witness (in case segwit transactions are added to mempool before
 //   segwit activation)
-bool BlockAssembler::TestPackageTransactions(const CTxMemPool::setEntries& package)
+bool BlockAssembler::TestPackageTransactions(const CTxMemPool::setEntries& package, const CTxMemPool::setEntries& failedTxs)
 {
     for (CTxMemPool::txiter it : package) {
         if (!IsFinalTx(it->GetTx(), nHeight, nLockTimeCutoff))
@@ -239,14 +239,17 @@ bool BlockAssembler::TestPackageTransactions(const CTxMemPool::setEntries& packa
         if (!fIncludeMWEB && it->GetTx().HasMWEBTx()) {
             return false;
         }
+        if (failedTxs.count(it) > 0) {
+            return false;
+        }
     }
     return true;
 }
 
-void BlockAssembler::AddToBlock(CTxMemPool::txiter iter)
+bool BlockAssembler::AddToBlock(CTxMemPool::txiter iter)
 {
     if (iter->GetTx().HasMWEBTx() && !mweb_miner.AddMWEBTransaction(iter)) {
-        return;
+        return false;
     }
 
     CTransactionRef pTx = iter->GetSharedTx();
@@ -277,6 +280,8 @@ void BlockAssembler::AddToBlock(CTxMemPool::txiter iter)
                   CFeeRate(iter->GetModifiedFee(), iter->GetTxSize(), iter->GetMWEBWeight()).ToString(),
                   iter->GetTx().GetHash().ToString());
     }
+
+    return true;
 }
 
 int BlockAssembler::UpdatePackagesForAdded(const CTxMemPool::setEntries& alreadyAdded,
@@ -445,8 +450,8 @@ void BlockAssembler::addPackageTxs(int &nPackagesSelected, int &nDescendantsUpda
         onlyUnconfirmed(ancestors);
         ancestors.insert(iter);
 
-        // Test if all tx's are Final
-        if (!TestPackageTransactions(ancestors)) {
+        // Test if all tx's are Final, and none have failed
+        if (!TestPackageTransactions(ancestors, failedTx)) {
             if (fUsingModified) {
                 mapModifiedTx.get<ancestor_score>().erase(modit);
                 failedTx.insert(iter);
@@ -461,16 +466,28 @@ void BlockAssembler::addPackageTxs(int &nPackagesSelected, int &nDescendantsUpda
         std::vector<CTxMemPool::txiter> sortedEntries;
         SortForBlock(ancestors, sortedEntries);
 
+        bool failed = false;
         for (size_t i=0; i<sortedEntries.size(); ++i) {
-            AddToBlock(sortedEntries[i]);
+            failed = !AddToBlock(sortedEntries[i]);
+            if (failed) {
+                for (size_t j = i; j < sortedEntries.size(); j++) {
+                    failedTx.insert(sortedEntries[j]);
+                    mapModifiedTx.erase(sortedEntries[j]);
+                }
+
+                break;
+            }
+
             // Erase from the modified set, if present
             mapModifiedTx.erase(sortedEntries[i]);
         }
 
         ++nPackagesSelected;
 
-        // Update transactions that depend on each of these
-        nDescendantsUpdated += UpdatePackagesForAdded(ancestors, mapModifiedTx);
+        if (!failed) {
+            // Update transactions that depend on each of these
+            nDescendantsUpdated += UpdatePackagesForAdded(ancestors, mapModifiedTx);
+        }
     }
 }
 
```

### src/miner.h
```diff
@@ -180,7 +180,7 @@ class BlockAssembler
     /** Clear the block's state and prepare for assembling a new block */
     void resetBlock();
     /** Add a tx to the block */
-    void AddToBlock(CTxMemPool::txiter iter);
+    bool AddToBlock(CTxMemPool::txiter iter);
 
     // Methods for how to add transactions to a block.
     /** Add transactions based on feerate including unconfirmed ancestors
@@ -197,7 +197,7 @@ class BlockAssembler
       * locktime, premature-witness, serialized size (if necessary)
       * These checks should always succeed, and they're here
       * only as an extra check in case of suboptimal node configuration */
-    bool TestPackageTransactions(const CTxMemPool::setEntries& package);
+    bool TestPackageTransactions(const CTxMemPool::setEntries& package, const CTxMemPool::setEntries& failedTxs);
     /** Return true if given transaction from mapTx has already been evaluated,
       * or if the transaction's cached data in mapTx is incorrect. */
     bool SkipMapTxEntry(CTxMemPool::txiter it, indexed_modified_transaction_set& mapModifiedTx, CTxMemPool::setEntries& failedTx) EXCLUSIVE_LOCKS_REQUIRED(m_mempool.cs);
```

### src/wallet/rpcwallet.cpp
```diff
@@ -1096,8 +1096,10 @@ static UniValue ListReceived(const CWallet* const pwallet, const UniValue& param
         if (nDepth < nMinDepth)
             continue;
 
-        for (const CTxOutput& txout : wtx.tx->GetOutputs())
+        std::vector<CTxOutput> outputs = wtx.tx->GetOutputs();
+        for (size_t i = 0; i < outputs.size(); i++)
         {
+            const CTxOutput& txout = outputs[i];
             CTxDestination address;
             if (!pwallet->ExtractOutputDestination(txout, address))
                 continue;
@@ -1110,13 +1112,45 @@ static UniValue ListReceived(const CWallet* const pwallet, const UniValue& param
             if(!(mine & filter))
                 continue;
 
+            
+            // Skip displaying hog-ex outputs when we have the MWEB transaction that contains the pegout.
+            // The original MWEB transaction will be displayed instead.
+            if (wtx.IsHogEx() && wtx.pegout_indices.size() > i) {
+                mw::Hash kernel_id = wtx.pegout_indices[i].first;
+                if (pwallet->FindWalletTxByKernelId(kernel_id) != nullptr) {
+                    continue;
+                }
+            }
+
             tallyitem& item = mapTally[address];
             item.nAmount += pwallet->GetValue(txout);
             item.nConf = std::min(item.nConf, nDepth);
             item.txids.push_back(wtx.GetHash());
             if (mine & ISMINE_WATCH_ONLY)
                 item.fIsWatchonly = true;
         }
+
+        for (const PegOutCoin& pegout : wtx.tx->mweb_tx.GetPegOuts())
+        {
+            CTxDestination address;
+            if (!::ExtractDestination(pegout.GetScriptPubKey(), address))
+                continue;
+
+            if (has_filtered_address && !(filtered_address == address)) {
+                continue;
+            }
+
+            isminefilter mine = pwallet->IsMine(address);
+            if(!(mine & filter))
+                continue;
+
+            tallyitem& item = mapTally[address];
+            item.nAmount += pegout.GetAmount();
+            item.nConf = std::min(item.nConf, nDepth);
+            item.txids.push_back(wtx.GetHash());
+            if (mine & ISMINE_WATCH_ONLY)
+                item.fIsWatchonly = true;
+        }
     }
 
     // Reply
```

### test/functional/mweb_wallet_basic.py
```diff
@@ -74,7 +74,7 @@ def run_test(self):
         tx2_id = node1.sendtoaddress(n2_addr, 15)
         self.sync_mempools()
 
-        self.log.info("Verify node1's wallet lists the transaction as spent")
+        self.log.info("Verify node1's wallet lists the transactions as spent")
         n1_tx2 = node1.gettransaction(txid=tx2_id)
         assert_equal(n1_tx2['confirmations'], 0)
         assert_equal(n1_tx2['amount'], -15)
@@ -86,45 +86,37 @@ def run_test(self):
         assert_equal(n2_tx2['confirmations'], 0)
         assert tx2_id in node1.getrawmempool()
 
-        self.log.info("Mine next block to make sure the transaction confirms successfully")
-        node0.generate(1)
-        self.sync_all()
-        assert tx2_id not in node1.getrawmempool()
-
-        self.log.info("Verify node2's wallet receives the first pegout transaction")
-        n2_addr_coins = node2.listreceivedbyaddress(minconf=0, address_filter=n2_addr)
-        assert_equal(len(n2_addr_coins), 1)
-        assert_equal(n2_addr_coins[0]['amount'], 15)
-        assert_equal(n2_addr_coins[0]['confirmations'], 1)
-        
         #
         # Pegout to node2 using subtract fee from amount
         #
         self.log.info("Send (pegout) to node2 bech32 address")
         n2_addr2 = node2.getnewaddress(address_type='bech32')
         tx3_id = node1.sendtoaddress(address=n2_addr2, amount=5, subtractfeefromamount=True)
         self.sync_mempools()
-
-        self.log.info("Verify node1's wallet lists the transaction as spent")
+        
         n1_tx3 = node1.gettransaction(txid=tx3_id)
         assert_equal(n1_tx3['confirmations'], 0)
         assert n1_tx3['amount'] > -5 and n1_tx3['amount'] < -4.9
         assert n1_tx3['fee'] < 0 and n1_tx3['fee'] > -0.1
 
+        self.log.info("Verify node2's wallet receives the second pegout transaction")
+        n2_addr2_coins = node2.listreceivedbyaddress(minconf=0, address_filter=n2_addr2)
+        assert_equal(len(n2_addr2_coins), 1)
+        assert n2_addr2_coins[0]['amount'] < 5 and n2_addr2_coins[0]['amount'] > 4.9
+        assert_equal(n2_addr2_coins[0]['confirmations'], 0)
         assert tx3_id in node1.getrawmempool()
 
-        self.log.info("Mine next block so node2 sees the transaction")
+        self.log.info("Mine next block to make sure the transactions confirm successfully")
         node0.generate(1)
         self.sync_all()
-        
-        assert tx3_id not in node1.getrawmempool()
-        
-        self.log.info("Verify node2's wallet receives the second pegout transaction")
+        assert tx2_id not in node1.getrawmempool()
+        assert tx3_id not in node1.getrawmempool()        
+
         n2_addr2_coins = node2.listreceivedbyaddress(minconf=0, address_filter=n2_addr2)
         assert_equal(len(n2_addr2_coins), 1)
         assert n2_addr2_coins[0]['amount'] < 5 and n2_addr2_coins[0]['amount'] > 4.9
         assert_equal(n2_addr2_coins[0]['confirmations'], 1)
-        
+
         n2_balances = node2.getbalances()['mine']
         assert n2_balances['immature'] > 19.9 and n2_balances['immature'] < 20
         assert_equal(n2_balances['untrusted_pending'], 0)
```
