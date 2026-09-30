# [?] index: Fix coinstatsindex overflow issue

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin/bitcoin
Published: 2025-08-04
Source: https://github.com/bitcoin/bitcoin/commit/431a076ae6e3cc32a8725d4a01483d27c5081a34
Type: security-commit

## Details
index: Fix coinstatsindex overflow issue

The index originally stored cumulative values in a CAmount type but this allowed for
potential overflow issues which were observed on Signet. Fix this by
storing the values that are in danger of overflowing in a arith_uint256.

Also turns an unnecessary copy into a reference in RevertBlock and
CustomAppend and gets
rid of the explicit total unspendable tracking which can be calculated
by adding the four categories of unspendables together.

## Patch
### doc/files.md
```diff
@@ -57,7 +57,7 @@ Subdirectory       | File(s)               | Description
 `indexes/txindex/` | LevelDB database      | Transaction index; *optional*, used if `-txindex=1`
 `indexes/blockfilter/basic/db/` | LevelDB database      | Blockfilter index LevelDB database for the basic filtertype; *optional*, used if `-blockfilterindex=basic`
 `indexes/blockfilter/basic/`    | `fltrNNNNN.dat`<sup>[\[2\]](#note2)</sup> | Blockfilter index filters for the basic filtertype; *optional*, used if `-blockfilterindex=basic`
-`indexes/coinstats/db/` | LevelDB database | Coinstats index; *optional*, used if `-coinstatsindex=1`
+`indexes/coinstatsindex/db/` | LevelDB database | Coinstats index; *optional*, used if `-coinstatsindex=1`
 `wallets/`         |                       | [Contains wallets](#multi-wallet-environment); can be specified by `-walletdir` option; if `wallets/` subdirectory does not exist, wallets reside in the [data directory](#data-directory-location)
 `./`               | `anchors.dat`         | Anchor IP address database, created on shutdown and deleted at startup. Anchors are last known outgoing block-relay-only peers that are tried to re-connect to on startup
 `./`               | `banlist.json`        | Stores the addresses/subnets of banned nodes.
```

### src/index/coinstatsindex.cpp
```diff
@@ -2,6 +2,7 @@
 // Distributed under the MIT software license, see the accompanying
 // file COPYING or http://www.opensource.org/licenses/mit-license.php.
 
+#include <arith_uint256.h>
 #include <chainparams.h>
 #include <coins.h>
 #include <common/args.h>
@@ -27,35 +28,42 @@ static constexpr uint8_t DB_MUHASH{'M'};
 namespace {
 
 struct DBVal {
-    uint256 muhash;
-    uint64_t transaction_output_count;
-    uint64_t bogo_size;
-    CAmount total_amount;
-    CAmount total_subsidy;
-    CAmount total_unspendable_amount;
-    CAmount total_prevout_spent_amount;
-    CAmount total_new_outputs_ex_coinbase_amount;
-    CAmount total_coinbase_amount;
-    CAmount total_unspendables_genesis_block;
-    CAmount total_unspendables_bip30;
-    CAmount total_unspendables_scripts;
-    CAmount total_unspendables_unclaimed_rewards;
+    uint256 muhash{uint256::ZERO};
+    uint64_t transaction_output_count{0};
+    uint64_t bogo_size{0};
+    CAmount total_amount{0};
+    CAmount total_subsidy{0};
+    arith_uint256 total_prevout_spent_amount{0};
+    arith_uint256 total_new_outputs_ex_coinbase_amount{0};
+    arith_uint256 total_coinbase_amount{0};
+    CAmount total_unspendables_genesis_block{0};
+    CAmount total_unspendables_bip30{0};
+    CAmount total_unspendables_scripts{0};
+    CAmount total_unspendables_unclaimed_rewards{0};
 
     SERIALIZE_METHODS(DBVal, obj)
     {
+        uint256 prevout_spent, new_outputs, coinbase;
+        SER_WRITE(obj, prevout_spent = ArithToUint256(obj.total_prevout_spent_amount));
+        SER_WRITE(obj, new_outputs = ArithToUint256(obj.total_new_outputs_ex_coinbase_amount));
+        SER_WRITE(obj, coinbase = ArithToUint256(obj.total_coinbase_amount));
+
         READWRITE(obj.muhash);
         READWRITE(obj.transaction_output_count);
         READWRITE(obj.bogo_size);
         READWRITE(obj.total_amount);
         READWRITE(obj.total_subsidy);
-        READWRITE(obj.total_unspendable_amount);
-        READWRITE(obj.total_prevout_spent_amount);
-        READWRITE(obj.total_new_outputs_ex_coinbase_amount);
-        READWRITE(obj.total_coinbase_amount);
+        READWRITE(prevout_spent);
+        READWRITE(new_outputs);
+        READWRITE(coinbase);
         READWRITE(obj.total_unspendables_genesis_block);
         READWRITE(obj.total_unspendables_bip30);
         READWRITE(obj.total_unspendables_scripts);
         READWRITE(obj.total_unspendables_unclaimed_rewards);
+
+        SER_READ(obj, obj.total_prevout_spent_amount = UintToArith256(prevout_spent));
+        SER_READ(obj, obj.total_new_outputs_ex_coinbase_amount = UintToArith256(new_outputs));
+        SER_READ(obj, obj.total_coinbase_amount = UintToArith256(coinbase));
     }
 };
 
@@ -106,7 +114,17 @@ std::unique_ptr<CoinStatsIndex> g_coin_stats_index;
 CoinStatsIndex::CoinStatsIndex(std::unique_ptr<interfaces::Chain> chain, size_t n_cache_size, bool f_memory, bool f_wipe)
     : BaseIndex(std::move(chain), "coinstatsindex")
 {
-    fs::path path{gArgs.GetDataDirNet() / "indexes" / "coinstats"};
+    // An earlier version of the index used "indexes/coinstats" but it contained
+    // a bug and is superseded by a fixed version at "indexes/coinstatsindex".
+    // The original index is kept around until the next release in case users
+    // decide to downgrade their node.
+    auto old_path = gArgs.GetDataDirNet() / "indexes" / "coinstats";
+    if (fs::exists(old_path)) {
+        // TODO: Change this to deleting the old index with v31.
+        LogWarning("Old version of coinstatsindex found at %s. This folder can be safely deleted unless you " \
+            "plan to downgrade your node to version 29 or lower.", fs::PathToString(old_path));
+    }
+    fs::path path{gArgs.GetDataDirNet() / "indexes" / "coinstatsindex"};
     fs::create_directories(path);
 
     m_db = std::make_unique<CoinStatsIndex::DB>(path / "db", n_cache_size, f_memory, f_wipe);
@@ -144,7 +162,6 @@ bool CoinStatsIndex::CustomAppend(const interfaces::BlockInfo& block)
 
             // Skip duplicate txid coinbase transactions (BIP30).
             if (is_coinbase && IsBIP30Unspendable(block.hash, block.height)) {
-                m_total_unspendable_amount += block_subsidy;
                 m_total_unspendables_bip30 += block_subsidy;
                 continue;
             }
@@ -156,7 +173,6 @@ bool CoinStatsIndex::CustomAppend(const interfaces::BlockInfo& block)
 
                 // Skip unspendable coins
                 if (coin.out.scriptPubKey.IsUnspendable()) {
-                    m_total_unspendable_amount += coin.out.nValue;
                     m_total_unspendables_scripts += coin.out.nValue;
                     continue;
                 }
@@ -179,7 +195,7 @@ bool CoinStatsIndex::CustomAppend(const interfaces::BlockInfo& block)
                 const auto& tx_undo{Assert(block.undo_data)->vtxundo.at(i - 1)};
 
                 for (size_t j = 0; j < tx_undo.vprevout.size(); ++j) {
-                    const Coin coin{tx_undo.vprevout[j]};
+                    const Coin& coin{tx_undo.vprevout[j]};
                     const COutPoint outpoint{tx->vin[j].prevout.hash, tx->vin[j].prevout.n};
 
                     RemoveCoinHash(m_muhash, outpoint, coin);
@@ -194,25 +210,24 @@ bool CoinStatsIndex::CustomAppend(const interfaces::BlockInfo& block)
         }
     } else {
         // genesis block
-        m_total_unspendable_amount += block_subsidy;
         m_total_unspendables_genesis_block += block_subsidy;
     }
 
     // If spent prevouts + block subsidy are still a higher amount than
     // new outputs + coinbase + current unspendable amount this means
     // the miner did not claim the full block reward. Unclaimed block
     // rewards are also unspendable.
-    const CAmount unclaimed_rewards{(m_total_prevout_spent_amount + m_total_subsidy) - (m_total_new_outputs_ex_coinbase_amount + m_total_coinbase_amount + m_total_unspendable_amount)};
-    m_total_unspendable_amount += unclaimed_rewards;
-    m_total_unspendables_unclaimed_rewards += unclaimed_rewards;
+    const CAmount temp_total_unspendable_amount{m_total_unspendables_genesis_block + m_total_unspendables_bip30 + m_total_unspendables_scripts + m_total_unspendables_unclaimed_rewards};
+    const arith_uint256 unclaimed_rewards{(m_total_prevout_spent_amount + m_total_subsidy) - (m_total_new_outputs_ex_coinbase_amount + m_total_coinbase_amount + temp_total_unspendable_amount)};
+    assert(unclaimed_rewards <= arith_uint256(std::numeric_limits<CAmount>::max()));
+    m_total_unspendables_unclaimed_rewards += static_cast<CAmount>(unclaimed_rewards.GetLow64());
 
     std::pair<uint256, DBVal> value;
     value.first = block.hash;
     value.second.transaction_output_count = m_transaction_output_count;
     value.second.bogo_size = m_bogo_size;
     value.second.total_amount = m_total_amount;
     value.second.total_subsidy = m_total_subsidy;
-    value.second.total_unspendable_amount = m_total_unspendable_amount;
     value.second.total_prevout_spent_amount = m_total_prevout_spent_amount;
     value.second.total_new_outputs_ex_coinbase_amount = m_total_new_outputs_ex_coinbase_amount;
     value.second.total_coinbase_amount = m_total_coinbase_amount;
@@ -307,7 +322,6 @@ std::optional<CCoinsStats> CoinStatsIndex::LookUpStats(const CBlockIndex& block_
     stats.nBogoSize = entry.bogo_size;
     stats.total_amount = entry.total_amount;
     stats.total_subsidy = entry.total_subsidy;
-    stats.total_unspendable_amount = entry.total_unspendable_amount;
     stats.total_prevout_spent_amount = entry.total_prevout_spent_amount;
     stats.total_new_outputs_ex_coinbase_amount = entry.total_new_outputs_ex_coinbase_amount;
     stats.total_coinbase_amount = entry.total_coinbase_amount;
@@ -352,7 +366,6 @@ bool CoinStatsIndex::CustomInit(const std::optional<interfaces::BlockRef>& block
         m_bogo_size = entry.bogo_size;
         m_total_amount = entry.total_amount;
         m_total_subsidy = entry.total_subsidy;
-        m_total_unspendable_amount = entry.total_unspendable_amount;
         m_total_prevout_spent_amount = entry.total_prevout_spent_amount;
         m_total_new_outputs_ex_coinbase_amount = entry.total_new_outputs_ex_coinbase_amount;
         m_total_coinbase_amount = entry.total_coinbase_amount;
@@ -387,9 +400,6 @@ bool CoinStatsIndex::RevertBlock(const interfaces::BlockInfo& block)
 {
     std::pair<uint256, DBVal> read_out;
 
-    const CAmount block_subsidy{GetBlockSubsidy(block.height, Params().GetConsensus())};
-    m_total_subsidy -= block_subsidy;
-
     // Ignore genesis block
     if (block.height > 0) {
         if (!m_db->Read(DBHeightKey(block.height - 1), read_out)) {
@@ -409,7 +419,8 @@ bool CoinStatsIndex::RevertBlock(const interfaces::BlockInfo& block)
         }
     }
 
-    // Remove the new UTXOs that were created from the block
+    // Roll back muhash by removing the new UTXOs that were created by the
+    // block and reapplying the old UTXOs that were spent by the block
     assert(block.data);
     assert(block.undo_data);
     for (size_t i = 0; i < block.data->vtx.size(); ++i) {
@@ -421,65 +432,40 @@ bool CoinStatsIndex::RevertBlock(const interfaces::BlockInfo& block)
             const COutPoint outpoint{tx->GetHash(), j};
             const Coin coin{out, block.height, is_coinbase};
 
-            // Skip unspendable coins
-            if (coin.out.scriptPubKey.IsUnspendable()) {
-                m_total_unspendable_amount -= coin.out.nValue;
-                m_total_unspendables_scripts -= coin.out.nValue;
-                continue;
+            if (!coin.out.scriptPubKey.IsUnspendable()) {
+                RemoveCoinHash(m_muhash, outpoint, coin);
             }
-
-            RemoveCoinHash(m_muhash, outpoint, coin);
-
-            if (tx->IsCoinBase()) {
-                m_total_coinbase_amount -= coin.out.nValue;
-            } else {
-                m_total_new_outputs_ex_coinbase_amount -= coin.out.nValue;
-            }
-
-            --m_transaction_output_count;
-            m_total_amount -= coin.out.nValue;
-            m_bogo_size -= GetBogoSize(coin.out.scriptPubKey);
         }
 
         // The coinbase tx has no undo data since no former output is spent
         if (!is_coinbase) {
             const auto& tx_undo{block.undo_data->vtxundo.at(i - 1)};
 
             for (size_t j = 0; j < tx_undo.vprevout.size(); ++j) {
-                const Coin coin{tx_undo.vprevout[j]};
+                const Coin& coin{tx_undo.vprevout[j]};
                 const COutPoint outpoint{tx->vin[j].prevout.hash, tx->vin[j].prevout.n};
                 ApplyCoinHash(m_muhash, outpoint, coin);
-
-                m_total_prevout_spent_amount -= coin.out.nValue;
-
-                m_transaction_output_count++;
-                m_total_amount += coin.out.nValue;
-                m_bogo_size += GetBogoSize(coin.out.scriptPubKey);
             }
         }
     }
 
-    const CAmount unclaimed_rewards{(m_total_new_outputs_ex_coinbase_amount + m_total_coinbase_amount + m_total_unspendable_amount) - (m_total_prevout_spent_amount + m_total_subsidy)};
-    m_total_unspendable_amount -= unclaimed_rewards;
-    m_total_unspendables_unclaimed_rewards -= unclaimed_rewards;
-
-    // Check that the rolled back internal values are consistent with the DB read out
+    // Check that the rolled back muhash is consistent with the DB read out
     uint256 out;
     m_muhash.Finalize(out);
     Assert(read_out.second.muhash == out);
 
-    Assert(m_transaction_output_count == read_out.second.transaction_output_count);
-    Assert(m_total_amount == read_out.second.total_amount);
-    Assert(m_bogo_size == read_out.second.bogo_size);
-    Assert(m_total_subsidy == read_out.second.total_subsidy);
-    Assert(m_total_unspendable_amount == read_out.second.total_unspendable_amount);
-    Assert(m_total_prevout_spent_amount == read_out.second.total_prevout_spent_amount);
-    Assert(m_total_new_outputs_ex_coinbase_amount == read_out.second.total_new_outputs_ex_coinbase_amount);
-    Assert(m_total_coinbase_amount == read_out.second.total_coinbase_amount);
-    Assert(m_total_unspendables_genesis_block == read_out.second.total_unspendables_genesis_block);
-    Assert(m_total_unspendables_bip30 == read_out.second.total_unspendables_bip30);
-    Assert(m_total_unspendables_scripts == read_out.second.total_unspendables_scripts);
-    Assert(m_total_unspendables_unclaimed_rewards == read_out.second.total_unspendables_unclaimed_rewards);
+    // Apply the other values from the DB to the member variables
+    m_transaction_output_count = read_out.second.transaction_output_count;
+    m_total_amount = read_out.second.total_amount;
+    m_bogo_size = read_out.second.bogo_size;
+    m_total_subsidy = read_out.second.total_subsidy;
+    m_total_prevout_spent_amount = read_out.second.total_prevout_spent_amount;
+    m_total_new_outputs_ex_coinbase_amount = read_out.second.total_new_outputs_ex_coinbase_amount;
+    m_total_coinbase_amount = read_out.second.total_coinbase_amount;
+    m_total_unspendables_genesis_block = read_out.second.total_unspendables_genesis_block;
+    m_total_unspendables_bip30 = read_out.second.total_unspendables_bip30;
+    m_total_unspendables_scripts = read_out.second.total_unspendables_scripts;
+    m_total_unspendables_unclaimed_rewards = read_out.second.total_unspendables_unclaimed_rewards;
 
     return true;
 }
```

### src/index/coinstatsindex.h
```diff
@@ -5,6 +5,7 @@
 #ifndef BITCOIN_INDEX_COINSTATSINDEX_H
 #define BITCOIN_INDEX_COINSTATSINDEX_H
 
+#include <arith_uint256.h>
 #include <crypto/muhash.h>
 #include <index/base.h>
 
@@ -29,10 +30,9 @@ class CoinStatsIndex final : public BaseIndex
     uint64_t m_bogo_size{0};
     CAmount m_total_amount{0};
     CAmount m_total_subsidy{0};
-    CAmount m_total_unspendable_amount{0};
-    CAmount m_total_prevout_spent_amount{0};
-    CAmount m_total_new_outputs_ex_coinbase_amount{0};
-    CAmount m_total_coinbase_amount{0};
+    arith_uint256 m_total_prevout_spent_amount{0};
+    arith_uint256 m_total_new_outputs_ex_coinbase_amount{0};
+    arith_uint256 m_total_coinbase_amount{0};
     CAmount m_total_unspendables_genesis_block{0};
     CAmount m_total_unspendables_bip30{0};
     CAmount m_total_unspendables_scripts{0};
```

### src/kernel/coinstats.h
```diff
@@ -5,6 +5,7 @@
 #ifndef BITCOIN_KERNEL_COINSTATS_H
 #define BITCOIN_KERNEL_COINSTATS_H
 
+#include <arith_uint256.h>
 #include <consensus/amount.h>
 #include <crypto/muhash.h>
 #include <streams.h>
@@ -50,14 +51,6 @@ struct CCoinsStats {
 
     //! Total cumulative amount of block subsidies up to and including this block
     CAmount total_subsidy{0};
-    //! Total cumulative amount of unspendable coins up to and including this block
-    CAmount total_unspendable_amount{0};
-    //! Total cumulative amount of prevouts spent up to and including this block
-    CAmount total_prevout_spent_amount{0};
-    //! Total cumulative amount of outputs created up to and including this block
-    CAmount total_new_outputs_ex_coinbase_amount{0};
-    //! Total cumulative amount of coinbase outputs up to and including this block
-    CAmount total_coinbase_amount{0};
     //! The unspendable coinbase amount from the genesis block
     CAmount total_unspendables_genesis_block{0};
     //! The two unspendable coinbase outputs total amount caused by BIP30
@@ -67,6 +60,15 @@ struct CCoinsStats {
     //! Total cumulative amount of coins lost due to unclaimed miner rewards up to and including this block
     CAmount total_unspendables_unclaimed_rewards{0};
 
+    // Despite containing amounts the following values use a uint256 type to prevent overflowing
+
+    //! Total cumulative amount of prevouts spent up to and including this block
+    arith_uint256 total_prevout_spent_amount{0};
+    //! Total cumulative amount of outputs created up to and including this block
+    arith_uint256 total_new_outputs_ex_coinbase_amount{0};
+    //! Total cumulative amount of coinbase outputs up to and including this block
+    arith_uint256 total_coinbase_amount{0};
+
     CCoinsStats() = default;
     CCoinsStats(int block_height, const uint256& block_hash);
 };
```

### src/rpc/blockchain.cpp
```diff
@@ -1101,8 +1101,6 @@ static RPCHelpMan gettxoutsetinfo()
             ret.pushKV("transactions", static_cast<int64_t>(stats.nTransactions));
             ret.pushKV("disk_size", stats.nDiskSize);
         } else {
-            ret.pushKV("total_unspendable_amount", ValueFromAmount(stats.total_unspendable_amount));
-
             CCoinsStats prev_stats{};
             if (pindex->nHeight > 0) {
                 const std::optional<CCoinsStats> maybe_prev_stats = GetUTXOStats(coins_view, *blockman, hash_type, node.rpc_interruption_point, pindex->pprev, index_requested);
@@ -1112,11 +1110,29 @@ static RPCHelpMan gettxoutsetinfo()
                 prev_stats = maybe_prev_stats.value();
             }
 
+            CAmount block_total_unspendable_amount = stats.total_unspendables_genesis_block +
+                                                     stats.total_unspendables_bip30 +
+                                                     stats.total_unspendables_scripts +
+                                                     stats.total_unspendables_unclaimed_rewards;
+            CAmount prev_block_total_unspendable_amount = prev_stats.total_unspendables_genesis_block +
+                                                          prev_stats.total_unspendables_bip30 +
+                                                          prev_stats.total_unspendables_scripts +
+                                                          prev_stats.total_unspendables_unclaimed_rewards;
+
+            ret.pushKV("total_unspendable_amount", ValueFromAmount(block_total_unspendable_amount));
+
             UniValue block_info(UniValue::VOBJ);
-            block_info.pushKV("prevout_spent", ValueFromAmount(stats.total_prevout_spent_amount - prev_stats.total_prevout_spent_amount));
-            block_info.pushKV("coinbase", ValueFromAmount(stats.total_coinbase_amount - prev_stats.total_coinbase_amount));
-            block_info.pushKV("new_outputs_ex_coinbase", ValueFromAmount(stats.total_new_outputs_ex_coinbase_amount - prev_stats.total_new_outputs_ex_coinbase_amount));
-            block_info.pushKV("unspendable", ValueFromAmount(stats.total_unspendable_amount - prev_stats.total_unspendable_amount));
+            // These per-block values should fit uint64 under normal circumstances
+            arith_uint256 diff_prevout = stats.total_prevout_spent_amount - prev_stats.total_prevout_spent_amount;
+            arith_uint256 diff_coinbase = stats.total_coinbase_amount - prev_stats.total_coinbase_amount;
+            arith_uint256 diff_outputs = stats.total_new_outputs_ex_coinbase_amount - prev_stats.total_new_outputs_ex_coinbase_amount;
+            CAmount prevout_amount = static_cast<CAmount>(diff_prevout.GetLow64());
+            CAmount coinbase_amount = static_cast<CAmount>(diff_coinbase.GetLow64());
+            CAmount outputs_amount = static_cast<CAmount>(diff_outputs.GetLow64());
+            block_info.pushKV("prevout_spent", ValueFromAmount(prevout_amount));
+            block_info.pushKV("coinbase", ValueFromAmount(coinbase_amount));
+            block_info.pushKV("new_outputs_ex_coinbase", ValueFromAmount(outputs_amount));
+            block_info.pushKV("unspendable", ValueFromAmount(block_total_unspendable_amount - prev_block_total_unspendable_amount));
 
             UniValue unspendables(UniValue::VOBJ);
             unspendables.pushKV("genesis_block", ValueFromAmount(stats.total_unspendables_genesis_block - prev_stats.total_unspendables_genesis_block));
```

### test/functional/feature_init.py
```diff
@@ -128,7 +128,7 @@ def check_clean_start(extra_args):
                 'startup_args': ['-txindex=1'],
             },
             # Removing these files does not result in a startup error:
-            # 'indexes/blockfilter/basic/*.dat', 'indexes/blockfilter/basic/db/*.*', 'indexes/coinstats/db/*.*',
+            # 'indexes/blockfilter/basic/*.dat', 'indexes/blockfilter/basic/db/*.*', 'indexes/coinstatsindex/db/*.*',
             # 'indexes/txindex/*.log', 'indexes/txindex/CURRENT', 'indexes/txindex/LOCK'
         ]
 
@@ -154,7 +154,7 @@ def check_clean_start(extra_args):
                 'startup_args': ['-blockfilterindex=1'],
             },
             {
-                'filepath_glob': 'indexes/coinstats/db/*.*',
+                'filepath_glob': 'indexes/coinstatsindex/db/*.*',
                 'error_message': 'LevelDB error: Corruption',
                 'startup_args': ['-coinstatsindex=1'],
             },
```
