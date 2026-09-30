# [?] Merge bitcoin/bitcoin#23418: Fix signed integer overflow in prioritisetransaction RPC

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2022-06-27
Source: https://github.com/dashpay/dash/commit/e8da48bd418b5783b527e9b64685fbbf10bf8fdf
Type: security-commit

## Details
Merge bitcoin/bitcoin#23418: Fix signed integer overflow in prioritisetransaction RPC

fa07f84e316171d60dd9941fb8db37e0a0de6654 Fix signed integer overflow in prioritisetransaction RPC (MarcoFalke)
fa52cf8e11b3af6e0a302d5d17aab6cea78899d5 refactor: Replace feeDelta by m_modified_fee (MarcoFalke)

Pull request description:

  Signed integer overflow is UB in theory, but not in practice. Still,
  it would be nice to avoid this UB to allow Bitcoin Core to be
  compiled with sanitizers such as `-ftrapv` or ubsan.

  It is impossible to predict when and if an overflow occurs, since
  the overflow caused by a prioritisetransaction RPC might only be
  later hit when descendant txs are added to the mempool.
  Since it is impossible to predict reliably, leave it up to the user
  to use the RPC endpoint responsibly, considering their mempool
  limits and usage patterns.

  Fixes: #20626
  Fixes: #20383
  Fixes: #19278
  Fixes: https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=34146 / https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=47132

  ## Steps to reproduce

  Build the code without the changes in this pull.

  Make sure to pass the sanitizer flag:

  ```
  ./autogen.sh && ./configure --with-sanitizers=signed-integer-overflow && make clean && make -j $(nproc)
  ```

  ### Reproduce on RPC

  ```
  ./src/bitcoind -chain=regtest -noprinttoconsole &
  ./src/bitcoin-cli -chain=regtest prioritisetransaction 00000000deadbeef00000000deadbeef00000000deadbeef00000000deadbeef 0 9123456789123456789
  ./src/bitcoin-cli -chain=regtest prioritisetransaction 00000000deadbeef00000000deadbeef00000000deadbeef00000000deadbeef 0 9123456789123456789
  |> txmempool.cpp:920:15: runtime error: signed integer overflow: 9123456789123456789 + 9123456789123456789 cannot be represented in type 'long int'

  ./src/bitcoin-cli -chain=regtest stop
  ```

  ### By fuzzing

  ```
  wget https://github.com/bitcoin/bitcoin/files/8921302/clusterfuzz-testcase-minimized-validation_load_mempool-5599531390074880.bin.txt
  FUZZ=validation_load_mempool ./src/test/fuzz/fuzz ./clusterfuzz-testcase-minimized-validation_load_mempool-5599531390074880.bin.txt
  |> txmempool.cpp:920:15: runtime error: signed integer overflow: 7214801925397553184 + 2314885530818453536 cannot be represented in type 'long int'
  |> validation_load_mempool: succeeded against 1 files in 0s.

ACKs for top commit:
  vasild:
    ACK fa07f84e316171d60dd9941fb8db37e0a0de6654
  dunxen:
    ACK fa07f84
  LarryRuane:
    ACK fa07f84e316171d60dd9941fb8db37e0a0de6654

Tree-SHA512: 4a357950af55a49c9113da0a50c2e743c5b752f0514dd8d16cd92bfde2f77dd0ef56aa98452626df6f7f7a5b51d1227021f6bc94091201a179f0d488ee32a0df

## Patch
### src/txmempool.cpp
```diff
@@ -17,6 +17,7 @@
 #include <reverse_iterator.h>
 #include <util/check.h>
 #include <util/moneystr.h>
+#include <util/overflow.h>
 #include <util/system.h>
 #include <util/time.h>
 #include <validationinterface.h>
@@ -66,7 +67,7 @@ struct update_fee_delta
 {
     explicit update_fee_delta(int64_t _feeDelta) : feeDelta(_feeDelta) { }
 
-    void operator() (CTxMemPoolEntry &e) { e.UpdateFeeDelta(feeDelta); }
+    void operator() (CTxMemPoolEntry &e) { e.UpdateModifiedFee(feeDelta); }
 
 private:
     int64_t feeDelta;
@@ -100,18 +101,19 @@ CTxMemPoolEntry::CTxMemPoolEntry(const CTransactionRef& tx, CAmount fee,
       entryHeight{entry_height},
       spendsCoinbase{spends_coinbase},
       sigOpCount{sigops_count},
+      m_modified_fee{nFee},
       lockPoints{lp},
       nSizeWithDescendants{GetTxSize()},
       nModFeesWithDescendants{nFee},
       nSizeWithAncestors{GetTxSize()},
       nModFeesWithAncestors{nFee},
       nSigOpCountWithAncestors{sigOpCount} {}
 
-void CTxMemPoolEntry::UpdateFeeDelta(int64_t newFeeDelta)
+void CTxMemPoolEntry::UpdateModifiedFee(int64_t fee_diff)
 {
-    nModFeesWithDescendants += newFeeDelta - feeDelta;
-    nModFeesWithAncestors += newFeeDelta - feeDelta;
-    feeDelta = newFeeDelta;
+    nModFeesWithDescendants = SaturatingAdd(nModFeesWithDescendants, fee_diff);
+    nModFeesWithAncestors = SaturatingAdd(nModFeesWithAncestors, fee_diff);
+    m_modified_fee = SaturatingAdd(m_modified_fee, fee_diff);
 }
 
 void CTxMemPoolEntry::UpdateLockPoints(const LockPoints& lp)
@@ -453,7 +455,7 @@ void CTxMemPoolEntry::UpdateDescendantState(int64_t modifySize, CAmount modifyFe
 {
     nSizeWithDescendants += modifySize;
     assert(int64_t(nSizeWithDescendants) > 0);
-    nModFeesWithDescendants += modifyFee;
+    nModFeesWithDescendants = SaturatingAdd(nModFeesWithDescendants, modifyFee);
     nCountWithDescendants += modifyCount;
     assert(int64_t(nCountWithDescendants) > 0);
 }
@@ -462,7 +464,7 @@ void CTxMemPoolEntry::UpdateAncestorState(int64_t modifySize, CAmount modifyFee,
 {
     nSizeWithAncestors += modifySize;
     assert(int64_t(nSizeWithAncestors) > 0);
-    nModFeesWithAncestors += modifyFee;
+    nModFeesWithAncestors = SaturatingAdd(nModFeesWithAncestors, modifyFee);
     nCountWithAncestors += modifyCount;
     assert(int64_t(nCountWithAncestors) > 0);
     nSigOpCountWithAncestors += modifySigOps;
@@ -510,6 +512,8 @@ void CTxMemPool::addUnchecked(const CTxMemPoolEntry &entry, setEntries &setAnces
     // Update transaction for any feeDelta created by PrioritiseTransaction
     CAmount delta{0};
     ApplyDelta(entry.GetTx().GetHash(), delta);
+    // The following call to UpdateModifiedFee assumes no previous fee modifications
+    Assume(entry.GetFee() == entry.GetModifiedFee());
     if (delta) {
             mapTx.modify(newit, update_fee_delta(delta));
     }
@@ -1458,10 +1462,10 @@ void CTxMemPool::PrioritiseTransaction(const uint256& hash, const CAmount& nFeeD
     {
         LOCK(cs);
         CAmount &delta = mapDeltas[hash];
-        delta += nFeeDelta;
+        delta = SaturatingAdd(delta, nFeeDelta);
         txiter it = mapTx.find(hash);
         if (it != mapTx.end()) {
-            mapTx.modify(it, update_fee_delta(delta));
+            mapTx.modify(it, update_fee_delta(nFeeDelta));
             // Now update all ancestors' modified fees with descendants
             setEntries setAncestors;
             uint64_t nNoLimit = std::numeric_limits<uint64_t>::max();
```

### src/txmempool.h
```diff
@@ -113,7 +113,7 @@ class CTxMemPoolEntry
     const unsigned int entryHeight; //!< Chain height when entering the mempool
     const bool spendsCoinbase;      //!< keep track of transactions that spend a coinbase
     const int64_t sigOpCount;       //!< Legacy sig ops plus P2SH sig op count
-    int64_t feeDelta{0};            //!< Used for determining the priority of the transaction for mining in a block
+    int64_t m_modified_fee;         //!< Used for determining the priority of the transaction for mining in a block
     LockPoints lockPoints;          //!< Track the height and time at which tx was final
 
     // Information about descendants of this transaction that are in the
@@ -142,17 +142,16 @@ class CTxMemPoolEntry
     std::chrono::seconds GetTime() const { return std::chrono::seconds{nTime}; }
     unsigned int GetHeight() const { return entryHeight; }
     int64_t GetSigOpCount() const { return sigOpCount; }
-    int64_t GetModifiedFee() const { return nFee + feeDelta; }
+    int64_t GetModifiedFee() const { return m_modified_fee; }
     size_t DynamicMemoryUsage() const { return nUsageSize; }
     const LockPoints& GetLockPoints() const { return lockPoints; }
 
     // Adjusts the descendant state.
     void UpdateDescendantState(int64_t modifySize, CAmount modifyFee, int64_t modifyCount);
     // Adjusts the ancestor state
     void UpdateAncestorState(int64_t modifySize, CAmount modifyFee, int64_t modifyCount, int64_t modifySigOps);
-    // Updates the fee delta used for mining priority score, and the
-    // modified fees with descendants.
-    void UpdateFeeDelta(int64_t feeDelta);
+    // Updates the modified fees with descendants/ancestors.
+    void UpdateModifiedFee(int64_t fee_diff);
     // Update the LockPoints after a reorg
     void UpdateLockPoints(const LockPoints& lp);
 
```

### test/sanitizer_suppressions/ubsan
```diff
@@ -1,10 +1,10 @@
 # -fsanitize=undefined suppressions
 # =================================
-# This would be `signed-integer-overflow:CTxMemPool::PrioritiseTransaction`,
+# The suppressions would be `sanitize-type:ClassName::MethodName`,
 # however due to a bug in clang the symbolizer is disabled and thus no symbol
 # names can be used.
 # See https://github.com/google/sanitizers/issues/1364
-signed-integer-overflow:txmempool.cpp
+
 # https://github.com/bitcoin/bitcoin/pull/21798#issuecomment-829180719
 signed-integer-overflow:policy/feerate.cpp
 
```
