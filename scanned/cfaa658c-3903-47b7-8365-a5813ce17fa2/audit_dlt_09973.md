# [?] CVE-2024-35202: Fix assertions in PartiallyDownloadedBlock

## Summary
Severity: Unknown
Chain: Litecoin
Component: litecoin-project/litecoin
Published: 2024-10-10
Source: https://github.com/litecoin-project/litecoin/commit/5d4a2e5b9383c530d061b516f9a9fb4465855939
Type: security-commit

## Details
CVE-2024-35202: Fix assertions in PartiallyDownloadedBlock

## Patch
### src/Makefile.test.include
```diff
@@ -84,6 +84,7 @@ FUZZ_TARGETS = \
   test/fuzz/parse_script \
   test/fuzz/parse_univalue \
   test/fuzz/partial_merkle_tree_deserialize \
+  test/fuzz/partially_downloaded_block.cpp \
   test/fuzz/partially_signed_transaction_deserialize \
   test/fuzz/policy_estimator \
   test/fuzz/policy_estimator_io \
```

### src/blockencodings.cpp
```diff
@@ -60,7 +60,8 @@ ReadStatus PartiallyDownloadedBlock::InitData(const CBlockHeaderAndShortTxIDs& c
     if (cmpctblock.shorttxids.size() + cmpctblock.prefilledtxn.size() > MAX_BLOCK_WEIGHT / MIN_SERIALIZABLE_TRANSACTION_WEIGHT)
         return READ_STATUS_INVALID;
 
-    assert(header.IsNull() && txn_available.empty());
+    if (!header.IsNull() || !txn_available.empty()) return READ_STATUS_INVALID;
+
     header = cmpctblock.header;
     mweb_block = cmpctblock.mweb_block;
     txn_available.resize(cmpctblock.BlockTxCount());
@@ -176,14 +177,18 @@ ReadStatus PartiallyDownloadedBlock::InitData(const CBlockHeaderAndShortTxIDs& c
     return READ_STATUS_OK;
 }
 
-bool PartiallyDownloadedBlock::IsTxAvailable(size_t index) const {
-    assert(!header.IsNull());
+bool PartiallyDownloadedBlock::IsTxAvailable(size_t index) const
+{
+    if (header.IsNull()) return false;
+
     assert(index < txn_available.size());
     return txn_available[index] != nullptr;
 }
 
-ReadStatus PartiallyDownloadedBlock::FillBlock(CBlock& block, const std::vector<CTransactionRef>& vtx_missing) {
-    assert(!header.IsNull());
+ReadStatus PartiallyDownloadedBlock::FillBlock(CBlock& block, const std::vector<CTransactionRef>& vtx_missing)
+{
+    if (header.IsNull()) return READ_STATUS_INVALID;
+
     uint256 hash = header.GetHash();
     block = header;
     block.mweb_block = mweb_block;
@@ -207,7 +212,8 @@ ReadStatus PartiallyDownloadedBlock::FillBlock(CBlock& block, const std::vector<
         return READ_STATUS_INVALID;
 
     BlockValidationState state;
-    if (!CheckBlock(block, state, Params().GetConsensus())) {
+    CheckBlockFn check_block = m_check_block_mock ? m_check_block_mock : CheckBlock;
+    if (!check_block(block, state, Params().GetConsensus(), /*fCheckPoW=*/true, /*fCheckMerkleRoot=*/true)) {
         // TODO: We really want to just check merkle tree manually here,
         // but that is expensive, and CheckBlock caches a block's
         // "checked-status" (in the CBlock?). CBlock should be able to
```

### src/blockencodings.h
```diff
@@ -7,8 +7,14 @@
 
 #include <primitives/block.h>
 
+#include <functional>
+
 
 class CTxMemPool;
+class BlockValidationState;
+namespace Consensus {
+struct Params;
+};
 
 // Transaction compression schemes for compact block relay can be introduced by writing
 // an actual formatter here.
@@ -137,6 +143,11 @@ class PartiallyDownloadedBlock {
 public:
     CBlockHeader header;
     MWEB::Block mweb_block;
+
+    // Can be overriden for testing
+    using CheckBlockFn = std::function<bool(const CBlock&, BlockValidationState&, const Consensus::Params&, bool, bool)>;
+    CheckBlockFn m_check_block_mock{nullptr};
+
     explicit PartiallyDownloadedBlock(CTxMemPool* poolIn, const MWEB::Block& mweb_blockIn) : pool(poolIn), mweb_block(mweb_blockIn) {}
 
     // extra_txn is a list of extra transactions to look at, in <witness hash, reference> form
```

### src/test/fuzz/partially_downloaded_block.cpp
```diff
@@ -0,0 +1,142 @@
+#include <blockencodings.h>
+#include <consensus/merkle.h>
+#include <consensus/validation.h>
+#include <primitives/block.h>
+#include <primitives/transaction.h>
+#include <test/fuzz/FuzzedDataProvider.h>
+#include <test/fuzz/fuzz.h>
+#include <test/fuzz/util.h>
+#include <test/fuzz/util/mempool.h>
+#include <test/util/setup_common.h>
+#include <test/util/txmempool.h>
+#include <txmempool.h>
+
+#include <cstddef>
+#include <cstdint>
+#include <limits>
+#include <memory>
+#include <optional>
+#include <set>
+#include <vector>
+
+namespace {
+const TestingSetup* g_setup;
+} // namespace
+
+void initialize_pdb()
+{
+    static const auto testing_setup = MakeNoLogFileContext<const TestingSetup>();
+    g_setup = testing_setup.get();
+}
+
+PartiallyDownloadedBlock::CheckBlockFn FuzzedCheckBlock(std::optional<BlockValidationResult> result)
+{
+    return [result](const CBlock&, BlockValidationState& state, const Consensus::Params&, bool, bool) {
+        if (result) {
+            return state.Invalid(*result);
+        }
+
+        return true;
+    };
+}
+
+FUZZ_TARGET_INIT(partially_downloaded_block, initialize_pdb)
+{
+    FuzzedDataProvider fuzzed_data_provider{buffer.data(), buffer.size()};
+
+    auto block{ConsumeDeserializable<CBlock>(fuzzed_data_provider)};
+    if (!block || block->vtx.size() == 0 ||
+        block->vtx.size() >= std::numeric_limits<uint16_t>::max()) {
+        return;
+    }
+
+    CBlockHeaderAndShortTxIDs cmpctblock{*block};
+
+    CTxMemPool pool{MemPoolOptionsForTest(g_setup->m_node)};
+    PartiallyDownloadedBlock pdb{&pool};
+
+    // Set of available transactions (mempool or extra_txn)
+    std::set<uint16_t> available;
+    // The coinbase is always available
+    available.insert(0);
+
+    std::vector<std::pair<uint256, CTransactionRef>> extra_txn;
+    for (size_t i = 1; i < block->vtx.size(); ++i) {
+        auto tx{block->vtx[i]};
+
+        bool add_to_extra_txn{fuzzed_data_provider.ConsumeBool()};
+        bool add_to_mempool{fuzzed_data_provider.ConsumeBool()};
+
+        if (add_to_extra_txn) {
+            extra_txn.emplace_back(tx->GetWitnessHash(), tx);
+            available.insert(i);
+        }
+
+        if (add_to_mempool) {
+            LOCK2(cs_main, pool.cs);
+            pool.addUnchecked(ConsumeTxMemPoolEntry(fuzzed_data_provider, *tx));
+            available.insert(i);
+        }
+    }
+
+    auto init_status{pdb.InitData(cmpctblock, extra_txn)};
+
+    std::vector<CTransactionRef> missing;
+    // Whether we skipped a transaction that should be included in `missing`.
+    // FillBlock should never return READ_STATUS_OK if that is the case.
+    bool skipped_missing{false};
+    for (size_t i = 0; i < cmpctblock.BlockTxCount(); i++) {
+        // If init_status == READ_STATUS_OK then a available transaction in the
+        // compact block (i.e. IsTxAvailable(i) == true) implies that we marked
+        // that transaction as available above (i.e. available.count(i) > 0).
+        // The reverse is not true, due to possible compact block short id
+        // collisions (i.e. available.count(i) > 0 does not imply
+        // IsTxAvailable(i) == true).
+        if (init_status == READ_STATUS_OK) {
+            assert(!pdb.IsTxAvailable(i) || available.count(i) > 0);
+        }
+
+        bool skip{fuzzed_data_provider.ConsumeBool()};
+        if (!pdb.IsTxAvailable(i) && !skip) {
+            missing.push_back(block->vtx[i]);
+        }
+
+        skipped_missing |= (!pdb.IsTxAvailable(i) && skip);
+    }
+
+    // Mock CheckBlock
+    bool fail_check_block{fuzzed_data_provider.ConsumeBool()};
+    auto validation_result =
+        fuzzed_data_provider.PickValueInArray(
+            {BlockValidationResult::BLOCK_RESULT_UNSET,
+             BlockValidationResult::BLOCK_CONSENSUS,
+             BlockValidationResult::BLOCK_RECENT_CONSENSUS_CHANGE,
+             BlockValidationResult::BLOCK_CACHED_INVALID,
+             BlockValidationResult::BLOCK_INVALID_HEADER,
+             BlockValidationResult::BLOCK_MUTATED,
+             BlockValidationResult::BLOCK_MISSING_PREV,
+             BlockValidationResult::BLOCK_INVALID_PREV,
+             BlockValidationResult::BLOCK_TIME_FUTURE,
+             BlockValidationResult::BLOCK_CHECKPOINT,
+             BlockValidationResult::BLOCK_HEADER_LOW_WORK});
+    pdb.m_check_block_mock = FuzzedCheckBlock(
+        fail_check_block ?
+            std::optional<BlockValidationResult>{validation_result} :
+            std::nullopt);
+
+    CBlock reconstructed_block;
+    auto fill_status{pdb.FillBlock(reconstructed_block, missing)};
+    switch (fill_status) {
+    case READ_STATUS_OK:
+        assert(!skipped_missing);
+        assert(!fail_check_block);
+        assert(block->GetHash() == reconstructed_block.GetHash());
+        break;
+    case READ_STATUS_CHECKBLOCK_FAILED: [[fallthrough]];
+    case READ_STATUS_FAILED:
+        assert(fail_check_block);
+        break;
+    case READ_STATUS_INVALID:
+        break;
+    }
+}
\ No newline at end of file
```
