# [?] fix: reuse best clsig to avoid potential race condition

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2025-11-04
Source: https://github.com/dashpay/dash/commit/c0faae0ff5f6784ad9acf2f7b3a8b20a7b3bd425
Type: security-commit

## Details
fix: reuse best clsig to avoid potential race condition

## Patch
### src/node/miner.cpp
```diff
@@ -173,7 +173,7 @@ static bool CalcCbTxBestChainlock(const llmq::CChainLocksHandler& chainlock_hand
 
         // Inserting our best CL
         bestCLHeightDiff = pindexPrev->nHeight - best_clsig.getHeight();
-        bestCLSignature = chainlock_handler.GetBestChainLock().getSig();
+        bestCLSignature = best_clsig.getSig();
 
         return true;
     }
```

### src/rpc/rawtransaction.cpp
```diff
@@ -667,8 +667,9 @@ static RPCHelpMan getassetunlockstatuses()
     }
     else {
         const auto pBlockIndexBestCL = [&]() -> const CBlockIndex* {
-            if (!llmq_ctx.clhandler->GetBestChainLock().IsNull()) {
-                return pTipBlockIndex->GetAncestor(llmq_ctx.clhandler->GetBestChainLock().getHeight());
+            const auto best_clsig = llmq_ctx.clhandler->GetBestChainLock();
+            if (!best_clsig.IsNull()) {
+                return pTipBlockIndex->GetAncestor(best_clsig.getHeight());
             }
             // If no CL info is available, try to use CbTx CL information
             if (const auto cbtx_best_cl = GetNonNullCoinbaseChainlock(pTipBlockIndex)) {
```
