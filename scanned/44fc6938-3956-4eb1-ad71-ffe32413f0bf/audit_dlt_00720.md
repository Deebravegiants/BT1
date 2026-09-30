# [?] ConnectBlock: fix CVE-2024-52911 use-after-free in script-verify path

## Summary
Severity: Unknown
Chain: Zcash
Component: zcash/zcash
Published: 2026-05-07
Source: https://github.com/zcash/zcash/commit/65494c01603957592f28e570a88956bbba525640
Type: security-commit

## Details
ConnectBlock: fix CVE-2024-52911 use-after-free in script-verify path

Move `txdata` declaration above `control` so that LIFO destruction
of automatic objects at function exit guarantees ~CCheckQueueControl
runs first (and Wait()s on script-verify worker threads) while
`txdata` is still alive. Workers hold non-owning
`PrecomputedTransactionData *` pointers into this vector via
`CScriptCheck::txdata`; with the prior declaration order, any
early return between `control.Add(vChecks)` and `control.Wait()` --
for example the `ContextualCheckShieldedInputs` failure path --
would destroy `txdata` first, after which ~CCheckQueueControl
would block on in-flight workers that are still dereferencing
freed memory.

Equivalent in shape to the upstream Bitcoin Core cleanup in
bitcoin/bitcoin#35209 (which fixed the root cause of CVE-2024-52911,
covertly mitigated earlier in bitcoin/bitcoin#31112). zcashd
forked from BC circa 2018 and never received either fix.

Reachable from any inbound P2P peer via a crafted invalid block.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

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
