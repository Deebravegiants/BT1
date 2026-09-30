# [?] Merge branch 'fix/cve-2024-52911' into hotfix-v6.12.3

## Summary
Severity: Unknown
Chain: Zcash
Component: zcash/zcash
Published: 2026-05-07
Source: https://github.com/zcash/zcash/commit/61bcb6c2b498764c76957f05164921dc6052ed97
Type: security-commit

## Details
Merge branch 'fix/cve-2024-52911' into hotfix-v6.12.3

## Patch
### src/main.cpp
```diff
@@ -3410,6 +3410,18 @@ bool ConnectBlock(const CBlock& block, CValidationState& state, CBlockIndex* pin
 
     CBlockUndo blockundo;
 
+    // `txdata` must be declared before `control` so that, by C++ LIFO
+    // destruction of automatic objects, ~CCheckQueueControl (which calls
+    // Wait() to join the script-verify worker threads) runs while `txdata`
+    // is still alive. Workers hold non-owning `PrecomputedTransactionData *`
+    // pointers into this vector via `CScriptCheck::txdata`; if `txdata` were
+    // destroyed first, those workers would dereference freed memory.
+    // The `reserve()` is also required so that subsequent `emplace_back`
+    // calls in the loop below do not reallocate and invalidate the pointers
+    // already handed to in-flight workers. See CVE-2024-52911.
+    std::vector<PrecomputedTransactionData> txdata;
+    txdata.reserve(block.vtx.size());
+
     CCheckQueueControl<CScriptCheck> control(fExpensiveChecks && nScriptCheckThreads ? &scriptcheckqueue : NULL);
 
     int64_t nTimeStart = GetTimeMicros();
@@ -3484,8 +3496,6 @@ bool ConnectBlock(const CBlock& block, CValidationState& state, CBlockIndex* pin
     size_t total_sapling_tx = 0;
     size_t total_orchard_tx = 0;
 
-    std::vector<PrecomputedTransactionData> txdata;
-    txdata.reserve(block.vtx.size()); // Required so that pointers to individual PrecomputedTransactionData don't get invalidated
     for (unsigned int i = 0; i < block.vtx.size(); i++)
     {
         const CTransaction &tx = block.vtx[i];
```
