# [?] Merge bitcoin/bitcoin#17860: fuzz: BIP 30, CVE-2018-17144

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2026-03-20
Source: https://github.com/dashpay/dash/commit/e8ff59da6aba60ec1d5c1a79163d2a9bb4dd1677
Type: security-commit

## Details
Merge bitcoin/bitcoin#17860: fuzz: BIP 30, CVE-2018-17144

## Patch
### src/Makefile.test.include
```diff
@@ -376,6 +376,7 @@ test_fuzz_fuzz_SOURCES = \
  test/fuzz/tx_pool.cpp \
  test/fuzz/txorphan.cpp \
  test/fuzz/utxo_snapshot.cpp \
+ test/fuzz/utxo_total_supply.cpp \
  test/fuzz/validation_load_mempool.cpp \
  test/fuzz/versionbits.cpp
 endif # ENABLE_FUZZ_BINARY
```

### src/bench/block_assemble.cpp
```diff
@@ -32,7 +32,7 @@ static void AssembleBlock(benchmark::Bench& bench)
     std::array<CTransactionRef, NUM_BLOCKS - COINBASE_MATURITY + 1> txs;
     for (size_t b{0}; b < NUM_BLOCKS; ++b) {
         CMutableTransaction tx;
-        tx.vin.push_back(MineBlock(test_setup->m_node, SCRIPT_PUB));
+        tx.vin.emplace_back(MineBlock(test_setup->m_node, SCRIPT_PUB));
         tx.vin.back().scriptSig = scriptSig;
         tx.vout.emplace_back(1337, SCRIPT_PUB);
         if (NUM_BLOCKS - b >= COINBASE_MATURITY)
```

### src/kernel/coinstats.cpp
```diff
@@ -107,7 +107,7 @@ static bool ComputeUTXOStats(CCoinsView* view, CCoinsStats& stats, T hash_obj, c
     uint256 prevkey;
     std::map<uint32_t, Coin> outputs;
     while (pcursor->Valid()) {
-        interruption_point();
+        if (interruption_point) interruption_point();
         COutPoint key;
         Coin coin;
         if (pcursor->GetKey(key) && pcursor->GetValue(coin)) {
```

### src/test/fuzz/tx_pool.cpp
```diff
@@ -47,12 +47,12 @@ void initialize_tx_pool()
     g_setup = testing_setup.get();
 
     for (int i = 0; i < 2 * COINBASE_MATURITY; ++i) {
-        CTxIn in = MineBlock(g_setup->m_node, CScript() << OP_TRUE);
+        COutPoint prevout{MineBlock(g_setup->m_node, CScript() << OP_TRUE)};
         // Remember the txids to avoid expensive disk access later on
         auto& outpoints = i < COINBASE_MATURITY ?
                               g_outpoints_coinbase_init_mature :
                               g_outpoints_coinbase_init_immature;
-        outpoints.push_back(in.prevout);
+        outpoints.push_back(prevout);
     }
     SyncWithValidationInterfaceQueue();
 }
```

### src/test/fuzz/utxo_total_supply.cpp
```diff
@@ -0,0 +1,165 @@
+// Copyright (c) 2020 The Bitcoin Core developers
+// Distributed under the MIT software license, see the accompanying
+// file COPYING or http://www.opensource.org/licenses/mit-license.php.
+
+#include <chainparams.h>
+#include <consensus/consensus.h>
+#include <consensus/merkle.h>
+#include <kernel/coinstats.h>
+#include <node/miner.h>
+#include <script/interpreter.h>
+#include <streams.h>
+#include <test/fuzz/FuzzedDataProvider.h>
+#include <test/fuzz/fuzz.h>
+#include <test/fuzz/util.h>
+#include <test/util/mining.h>
+#include <test/util/setup_common.h>
+#include <validation.h>
+#include <version.h>
+
+FUZZ_TARGET(utxo_total_supply)
+{
+    /** The testing setup that creates a chainman only (no chainstate) */
+    ChainTestingSetup test_setup{
+        CBaseChainParams::REGTEST,
+        {
+            "-testactivationheight=bip34@2",
+        },
+    };
+    // Create chainstate
+    test_setup.LoadVerifyActivateChainstate();
+    auto& node{test_setup.m_node};
+    auto& chainman{*Assert(test_setup.m_node.chainman)};
+    FuzzedDataProvider fuzzed_data_provider(buffer.data(), buffer.size());
+
+    const auto ActiveHeight = [&]() {
+        LOCK(::cs_main);
+        return chainman.ActiveHeight();
+    };
+    const auto PrepareNextBlock = [&]() {
+        // Use OP_FALSE to avoid BIP30 check from hitting early
+        auto block = PrepareBlock(node, CScript{} << OP_FALSE);
+        // Replace OP_FALSE with OP_TRUE
+        {
+            CMutableTransaction tx{*block->vtx.back()};
+            tx.vout.at(0).scriptPubKey = CScript{} << OP_TRUE;
+            block->vtx.back() = MakeTransactionRef(tx);
+        }
+        return block;
+    };
+
+    /** The block template this fuzzer is working on */
+    auto current_block = PrepareNextBlock();
+    /** Append-only set of tx outpoints, entries are not removed when spent */
+    std::vector<std::pair<COutPoint, CTxOut>> txos;
+    /** The utxo stats at the chain tip */
+    kernel::CCoinsStats utxo_stats;
+    /** The total amount of coins in the utxo set */
+    CAmount circulation{0};
+
+
+    // Store the tx out in the txo map
+    const auto StoreLastTxo = [&]() {
+        // get last tx
+        const CTransaction& tx = *current_block->vtx.back();
+        // get last out
+        const uint32_t i = tx.vout.size() - 1;
+        // store it
+        txos.emplace_back(COutPoint{tx.GetHash(), i}, tx.vout.at(i));
+        if (current_block->vtx.size() == 1 && tx.vout.at(i).scriptPubKey[0] == OP_RETURN) {
+            // also store coinbase
+            const uint32_t i = tx.vout.size() - 2;
+            txos.emplace_back(COutPoint{tx.GetHash(), i}, tx.vout.at(i));
+        }
+    };
+    const auto AppendRandomTxo = [&](CMutableTransaction& tx) {
+        const auto& txo = txos.at(fuzzed_data_provider.ConsumeIntegralInRange<size_t>(0, txos.size() - 1));
+        tx.vin.emplace_back(txo.first);
+        tx.vout.emplace_back(txo.second.nValue, txo.second.scriptPubKey); // "Forward" coin with no fee
+    };
+    const auto UpdateUtxoStats = [&]() {
+        LOCK(::cs_main);
+        chainman.ActiveChainstate().ForceFlushStateToDisk();
+        utxo_stats = std::move(
+            *Assert(kernel::ComputeUTXOStats(kernel::CoinStatsHashType::NONE, &chainman.ActiveChainstate().CoinsDB(), chainman.m_blockman, {})));
+        // Check that miner can't print more money than they are allowed to
+        assert(circulation == utxo_stats.total_amount);
+    };
+
+
+    // Update internal state to chain tip
+    StoreLastTxo();
+    UpdateUtxoStats();
+    assert(ActiveHeight() == 0);
+    // Get at which height we duplicate the coinbase
+    // Assuming that the fuzzer will mine relatively short chains (less than 200 blocks), we want the duplicate coinbase to be not too high.
+    // Up to 2000 seems reasonable.
+    int64_t duplicate_coinbase_height = fuzzed_data_provider.ConsumeIntegralInRange(0, 20 * COINBASE_MATURITY);
+    // Always pad with OP_0 at the end to avoid bad-cb-length error
+    const CScript duplicate_coinbase_script = CScript() << duplicate_coinbase_height << OP_0;
+    // Mine the first block with this duplicate
+    current_block = PrepareNextBlock();
+    StoreLastTxo();
+
+    {
+        // Create duplicate (CScript should match exact format as in CreateNewBlock)
+        CMutableTransaction tx{*current_block->vtx.front()};
+        tx.vin.at(0).scriptSig = duplicate_coinbase_script;
+
+        // Mine block and create next block template
+        current_block->vtx.front() = MakeTransactionRef(tx);
+    }
+    current_block->hashMerkleRoot = BlockMerkleRoot(*current_block);
+    assert(!MineBlock(node, current_block).IsNull());
+    circulation += GetBlockSubsidy(chainman.ActiveTip(), Params().GetConsensus());
+
+    assert(ActiveHeight() == 1);
+    UpdateUtxoStats();
+    current_block = PrepareNextBlock();
+    StoreLastTxo();
+
+    LIMITED_WHILE(fuzzed_data_provider.remaining_bytes(), 100'000)
+    {
+        CallOneOf(
+            fuzzed_data_provider,
+            [&] {
+                // Append an input-output pair to the last tx in the current block
+                CMutableTransaction tx{*current_block->vtx.back()};
+                AppendRandomTxo(tx);
+                current_block->vtx.back() = MakeTransactionRef(tx);
+                StoreLastTxo();
+            },
+            [&] {
+                // Append a tx to the list of txs in the current block
+                CMutableTransaction tx{};
+                AppendRandomTxo(tx);
+                current_block->vtx.push_back(MakeTransactionRef(tx));
+                StoreLastTxo();
+            },
+            [&] {
+                // Append the current block to the active chain
+                current_block->hashMerkleRoot = BlockMerkleRoot(*current_block);
+                const bool was_valid = !MineBlock(node, current_block).IsNull();
+
+                const auto prev_utxo_stats = utxo_stats;
+                if (was_valid) {
+                    circulation += GetBlockSubsidy(chainman.ActiveTip(), Params().GetConsensus());
+
+                    if (duplicate_coinbase_height == ActiveHeight()) {
+                        // we mined the duplicate coinbase
+                        assert(current_block->vtx.at(0)->vin.at(0).scriptSig == duplicate_coinbase_script);
+                    }
+                }
+
+                UpdateUtxoStats();
+
+                if (!was_valid) {
+                    // utxo stats must not change
+                    assert(prev_utxo_stats.hashSerialized == utxo_stats.hashSerialized);
+                }
+
+                current_block = PrepareNextBlock();
+                StoreLastTxo();
+            });
+    }
+}
```

### src/test/util/mining.cpp
```diff
@@ -6,21 +6,24 @@
 
 #include <chainparams.h>
 #include <consensus/merkle.h>
+#include <consensus/validation.h>
 #include <evo/evodb.h>
 #include <key_io.h>
 #include <node/context.h>
 #include <node/miner.h>
 #include <pow.h>
+#include <primitives/transaction.h>
 #include <script/standard.h>
 #include <test/util/script.h>
 #include <util/check.h>
 #include <validation.h>
+#include <validationinterface.h>
 #include <versionbits.h>
 
 using node::BlockAssembler;
 using node::NodeContext;
 
-CTxIn generatetoaddress(const NodeContext& node, const std::string& address)
+COutPoint generatetoaddress(const NodeContext& node, const std::string& address)
 {
     const auto dest = DecodeDestination(address);
     assert(IsValidDestination(dest));
@@ -60,7 +63,7 @@ std::vector<std::shared_ptr<CBlock>> CreateBlockChain(size_t total_height, const
     return ret;
 }
 
-CTxIn MineBlock(const NodeContext& node, const CScript& coinbase_scriptPubKey)
+COutPoint MineBlock(const NodeContext& node, const CScript& coinbase_scriptPubKey)
 {
     auto block = PrepareBlock(node, coinbase_scriptPubKey);
 
@@ -72,7 +75,7 @@ CTxIn MineBlock(const NodeContext& node, const CScript& coinbase_scriptPubKey)
     bool processed{Assert(node.chainman)->ProcessNewBlock(block, true, nullptr)};
     assert(processed);
 
-    return CTxIn{block->vtx[0]->GetHash(), 0};
+    return {block->vtx[0]->GetHash(), 0};
 }
 
 std::shared_ptr<CBlock> PrepareBlock(const NodeContext& node, const CScript& coinbase_scriptPubKey)
@@ -88,3 +91,43 @@ std::shared_ptr<CBlock> PrepareBlock(const NodeContext& node, const CScript& coi
 
     return block;
 }
+
+struct BlockValidationStateCatcher : public CValidationInterface {
+    const uint256 m_hash;
+    std::optional<BlockValidationState> m_state;
+
+    BlockValidationStateCatcher(const uint256& hash)
+        : m_hash{hash},
+          m_state{} {}
+
+protected:
+    void BlockChecked(const CBlock& block, const BlockValidationState& state) override
+    {
+        if (block.GetHash() != m_hash) return;
+        m_state = state;
+    }
+};
+
+COutPoint MineBlock(const NodeContext& node, std::shared_ptr<CBlock>& block)
+{
+    while (!CheckProofOfWork(block->GetHash(), block->nBits, Params().GetConsensus())) {
+        ++block->nNonce;
+        assert(block->nNonce);
+    }
+
+    auto& chainman{*Assert(node.chainman)};
+    const auto old_height = WITH_LOCK(::cs_main, return chainman.ActiveHeight());
+    bool new_block;
+    BlockValidationStateCatcher bvsc{block->GetHash()};
+    RegisterValidationInterface(&bvsc);
+    const bool processed{chainman.ProcessNewBlock(block, true, &new_block)};
+    const bool duplicate{!new_block && processed};
+    assert(!duplicate);
+    UnregisterValidationInterface(&bvsc);
+    SyncWithValidationInterfaceQueue();
+    const bool was_valid{bvsc.m_state && bvsc.m_state->IsValid()};
+    assert(old_height + was_valid == WITH_LOCK(::cs_main, return chainman.ActiveHeight()));
+
+    if (was_valid) return {block->vtx[0]->GetHash(), 0};
+    return {};
+}
```

### src/test/util/mining.h
```diff
@@ -11,8 +11,8 @@
 
 class CBlock;
 class CChainParams;
+class COutPoint;
 class CScript;
-class CTxIn;
 namespace node {
 struct NodeContext;
 } // namespace node
@@ -21,12 +21,18 @@ struct NodeContext;
 std::vector<std::shared_ptr<CBlock>> CreateBlockChain(size_t total_height, const CChainParams& params);
 
 /** Returns the generated coin */
-CTxIn MineBlock(const node::NodeContext&, const CScript& coinbase_scriptPubKey);
+COutPoint MineBlock(const node::NodeContext&, const CScript& coinbase_scriptPubKey);
+
+/**
+ * Returns the generated coin (or Null if the block was invalid).
+ * It is recommended to call RegenerateCommitments before mining the block to avoid merkle tree mismatches.
+ **/
+COutPoint MineBlock(const node::NodeContext&, std::shared_ptr<CBlock>& block);
 
 /** Prepare a block to be mined */
 std::shared_ptr<CBlock> PrepareBlock(const node::NodeContext&, const CScript& coinbase_scriptPubKey);
 
 /** RPC-like helper function, returns the generated coin */
-CTxIn generatetoaddress(const node::NodeContext&, const std::string& address);
+COutPoint generatetoaddress(const node::NodeContext&, const std::string& address);
 
 #endif // BITCOIN_TEST_UTIL_MINING_H
```

### src/test/util/setup_common.cpp
```diff
@@ -312,16 +312,12 @@ ChainTestingSetup::~ChainTestingSetup()
     m_node.scheduler.reset();
 }
 
-TestingSetup::TestingSetup(const std::string& chainName, const std::vector<const char*>& extra_args)
-    : ChainTestingSetup(chainName, extra_args)
+void ChainTestingSetup::LoadVerifyActivateChainstate()
 {
     const CChainParams& chainparams = Params();
-    // Ideally we'd move all the RPC tests to the functional testing framework
-    // instead of unit tests, but for now we need these here.
-    RegisterAllCoreRPCCommands(tableRPC);
-
+    auto& chainman{*Assert(m_node.chainman)};
     auto maybe_load_error = LoadChainstate(fReindex.load(),
-                                           *Assert(m_node.chainman.get()),
+                                           chainman,
                                            *Assert(m_node.govman.get()),
                                            *Assert(m_node.mn_metaman.get()),
                                            *Assert(m_node.mn_sync.get()),
@@ -342,16 +338,16 @@ TestingSetup::TestingSetup(const std::string& chainName, const std::vector<const
                                            m_cache_sizes.block_tree_db,
                                            m_cache_sizes.coins_db,
                                            m_cache_sizes.coins,
-                                           /*block_tree_db_in_memory=*/true,
-                                           /*coins_db_in_memory=*/true,
+                                           m_block_tree_db_in_memory,
+                                           m_coins_db_in_memory,
                                            /*dash_dbs_in_memory=*/true,
                                            llmq::DEFAULT_BLSCHECK_THREADS,
                                            llmq::DEFAULT_WORKER_COUNT,
                                            llmq::DEFAULT_MAX_RECOVERED_SIGS_AGE);
     assert(!maybe_load_error.has_value());
 
     auto maybe_verify_error = VerifyLoadedChainstate(
-        *Assert(m_node.chainman),
+        chainman,
         *Assert(m_node.evodb.get()),
         fReindex.load(),
         m_args.GetBoolArg("-reindex-chainstate", false),
@@ -364,6 +360,27 @@ TestingSetup::TestingSetup(const std::string& chainName, const std::vector<const
         });
     assert(!maybe_verify_error.has_value());
 
+    BlockValidationState state;
+    if (!chainman.ActiveChainstate().ActivateBestChain(state)) {
+        throw std::runtime_error(strprintf("ActivateBestChain failed. (%s)", state.ToString()));
+    }
+}
+
+TestingSetup::TestingSetup(
+    const std::string& chainName,
+    const std::vector<const char*>& extra_args,
+    const bool coins_db_in_memory,
+    const bool block_tree_db_in_memory)
+    : ChainTestingSetup(chainName, extra_args)
+{
+    m_coins_db_in_memory = coins_db_in_memory;
+    m_block_tree_db_in_memory = block_tree_db_in_memory;
+    const CChainParams& chainparams = Params();
+    // Ideally we'd move all the RPC tests to the functional testing framework
+    // instead of unit tests, but for now we need these here.
+    RegisterAllCoreRPCCommands(tableRPC);
+    LoadVerifyActivateChainstate();
+
     m_node.dstxman = std::make_unique<CDSTXManager>(*Assert(m_node.chainlocks));
 #ifdef ENABLE_WALLET
     // The test suite doesn't use masternode mode, so we may initialize it
@@ -391,10 +408,6 @@ TestingSetup::TestingSetup(const std::string& chainName, const std::vector<const
         m_node.connman->Init(options);
     }
 
-    BlockValidationState state;
-    if (!m_node.chainman->ActiveChainstate().ActivateBestChain(state)) {
-        throw std::runtime_error(strprintf("ActivateBestChain failed. (%s)", state.ToString()));
-    }
 }
 
 TestingSetup::~TestingSetup()
```

### src/test/util/setup_common.h
```diff
@@ -118,15 +118,24 @@ struct BasicTestingSetup {
  */
 struct ChainTestingSetup : public BasicTestingSetup {
     node::CacheSizes m_cache_sizes{};
+    bool m_coins_db_in_memory{true};
+    bool m_block_tree_db_in_memory{true};
 
     explicit ChainTestingSetup(const std::string& chainName = CBaseChainParams::MAIN, const std::vector<const char*>& extra_args = {});
     ~ChainTestingSetup();
+
+    // Supplies a chainstate, if one is needed
+    void LoadVerifyActivateChainstate();
 };
 
 /** Testing setup that configures a complete environment.
  */
 struct TestingSetup : public ChainTestingSetup {
-    explicit TestingSetup(const std::string& chainName = CBaseChainParams::MAIN, const std::vector<const char*>& extra_args = {});
+    explicit TestingSetup(
+        const std::string& chainName = CBaseChainParams::MAIN,
+        const std::vector<const char*>& extra_args = {},
+        const bool coins_db_in_memory = true,
+        const bool block_tree_db_in_memory = true);
     ~TestingSetup();
 };
 
```
