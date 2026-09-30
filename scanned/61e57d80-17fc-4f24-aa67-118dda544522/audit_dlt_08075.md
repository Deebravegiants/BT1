# [?] Fix `ChainstateManager::AddChainstate()` assertion crash

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin/bitcoin
Published: 2025-12-17
Source: https://github.com/bitcoin/bitcoin/commit/2bc32656498517fe58bd41dcbd0afd306d51d4b0
Type: security-commit

## Details
Fix `ChainstateManager::AddChainstate()` assertion crash

Check mempool exists before accessing size when prev_chainstate doesn't have initialized mempool.

## Patch
### src/validation.cpp
```diff
@@ -6248,7 +6248,7 @@ Chainstate& ChainstateManager::AddChainstate(std::unique_ptr<Chainstate> chainst
 
     // Transfer possession of the mempool to the chainstate.
     // Mempool is empty at this point because we're still in IBD.
-    assert(prev_chainstate.m_mempool->size() == 0);
+    assert(!prev_chainstate.m_mempool || prev_chainstate.m_mempool->size() == 0);
     assert(!curr_chainstate.m_mempool);
     std::swap(curr_chainstate.m_mempool, prev_chainstate.m_mempool);
     return curr_chainstate;
```
