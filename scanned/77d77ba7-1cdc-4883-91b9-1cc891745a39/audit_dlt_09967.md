# [?] Fix signed integer overflow in prioritisetransaction RPC

## Summary
Severity: Unknown
Chain: Liquid
Component: ElementsProject/elements
Published: 2021-11-02
Source: https://github.com/ElementsProject/elements/commit/56eec70de45a1437d360b47cfa316a05dd715929
Type: security-commit

## Details
Fix signed integer overflow in prioritisetransaction RPC

Cherry-pick of fa52cf8e11b3af6e0a302d5d17aab6cea78899d5
https://github.com/bitcoin/bitcoin/pull/23418 (2/2)

## Patch
### src/txmempool.cpp
```diff
@@ -20,6 +20,7 @@
 #include <reverse_iterator.h>
 #include <util/check.h>
 #include <util/moneystr.h>
+#include <util/overflow.h>
 #include <util/system.h>
 #include <util/time.h>
 #include <validationinterface.h>
@@ -102,9 +103,9 @@ CTxMemPoolEntry::CTxMemPoolEntry(const CTransactionRef& tx, CAmount fee,
 
 void CTxMemPoolEntry::UpdateModifiedFee(CAmount fee_diff)
 {
-    nModFeesWithDescendants += fee_diff;
-    nModFeesWithAncestors += fee_diff;
-    m_modified_fee += fee_diff;
+    nModFeesWithDescendants = SaturatingAdd(nModFeesWithDescendants, fee_diff);
+    nModFeesWithAncestors = SaturatingAdd(nModFeesWithAncestors, fee_diff);
+    m_modified_fee = SaturatingAdd(m_modified_fee, fee_diff);
 }
 
 void CTxMemPoolEntry::UpdateLockPoints(const LockPoints& lp)
@@ -459,7 +460,7 @@ void CTxMemPoolEntry::UpdateDescendantState(int64_t modifySize, CAmount modifyFe
 {
     nSizeWithDescendants += modifySize;
     assert(int64_t(nSizeWithDescendants) > 0);
-    nModFeesWithDescendants += modifyFee;
+    nModFeesWithDescendants = SaturatingAdd(nModFeesWithDescendants, modifyFee);
     nCountWithDescendants += modifyCount;
     assert(int64_t(nCountWithDescendants) > 0);
 }
@@ -468,7 +469,7 @@ void CTxMemPoolEntry::UpdateAncestorState(int64_t modifySize, CAmount modifyFee,
 {
     nSizeWithAncestors += modifySize;
     assert(int64_t(nSizeWithAncestors) > 0);
-    nModFeesWithAncestors += modifyFee;
+    nModFeesWithAncestors = SaturatingAdd(nModFeesWithAncestors, modifyFee);
     nCountWithAncestors += modifyCount;
     assert(int64_t(nCountWithAncestors) > 0);
     nSigOpCostWithAncestors += modifySigOps;
@@ -1018,7 +1019,7 @@ void CTxMemPool::PrioritiseTransaction(const uint256& hash, const CAmount& nFeeD
     {
         LOCK(cs);
         CAmount &delta = mapDeltas[hash];
-        delta += nFeeDelta;
+        delta = SaturatingAdd(delta, nFeeDelta);
         txiter it = mapTx.find(hash);
         if (it != mapTx.end()) {
             mapTx.modify(it, [&nFeeDelta](CTxMemPoolEntry& e) { e.UpdateModifiedFee(nFeeDelta); });
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
