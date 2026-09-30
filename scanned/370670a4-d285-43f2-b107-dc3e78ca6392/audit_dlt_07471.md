# [?] Merge #6940: fix: reuse best clsig to avoid potential race condition

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2025-11-04
Source: https://github.com/dashpay/dash/commit/00368fbece5e1217a1caf42bee770b3d8adc6131
Type: security-commit

## Details
Merge #6940: fix: reuse best clsig to avoid potential race condition

c0faae0ff5f6784ad9acf2f7b3a8b20a7b3bd425 fix: reuse best clsig to avoid potential race condition (Kittywhiskers Van Gogh)
98dc874791c62344760f8401a4b5ccddbb7f17c2 trivial: use `GetBestChainLockHeight()` (Kittywhiskers Van Gogh)

Pull request description:

  ## Additional Information

  Fix for potential race condition identified by CodeRabbit in [dash#6933](https://github.com/dashpay/dash/pull/6933) ([comment](https://github.com/dashpay/dash/pull/6933#discussion_r2489816537))

  ## Breaking Changes

  None expected.

  ## Checklist

  - [x] I have performed a self-review of my own code
  - [x] I have commented my code, particularly in hard-to-understand areas **(note: N/A)**
  - [x] I have added or updated relevant unit/integration/functional/e2e tests **(note: N/A)**
  - [x] I have made corresponding changes to the documentation **(note: N/A)**
  - [x] I have assigned this pull request to a milestone _(for repository code-owners and collaborators only)_

ACKs for top commit:
  UdjinM6:
    utACK c0faae0ff5f6784ad9acf2f7b3a8b20a7b3bd425

Tree-SHA512: 74762c5d715405a32af4a58553c05dc2fd98cdb7f038a519cf244a7c84a6a536ff341d8e8f534dbb6a0df952730314f85c52738c4d5b2e72fa74a4f02a6b2237

## Patch
### src/evo/chainhelper.cpp
```diff
@@ -38,7 +38,7 @@ bool CChainstateHelper::HasChainLock(int nHeight, const uint256& blockHash) cons
     return clhandler.HasChainLock(nHeight, blockHash);
 }
 
-int32_t CChainstateHelper::GetBestChainLockHeight() const { return clhandler.GetBestChainLock().getHeight(); }
+int32_t CChainstateHelper::GetBestChainLockHeight() const { return clhandler.GetBestChainLockHeight(); }
 
 /** Passthrough functions to CInstantSendManager */
 std::optional<std::pair</*islock_hash=*/uint256, /*txid=*/uint256>> CChainstateHelper::ConflictingISLockIfAny(
```

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
@@ -656,8 +656,9 @@ static RPCHelpMan getassetunlockstatuses()
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
