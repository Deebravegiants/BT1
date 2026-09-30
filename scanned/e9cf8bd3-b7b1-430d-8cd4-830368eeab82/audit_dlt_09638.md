# [?] fix: resolve race condition in quorum data recovery thread management

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2025-07-29
Source: https://github.com/dashpay/dash/commit/0e2811f22a85da6cdc12952303d49a3ce5a24831
Type: security-commit

## Details
fix: resolve race condition in quorum data recovery thread management

Replace check-then-set pattern with atomic compare-and-swap operation
in StartQuorumDataRecoveryThread to prevent multiple threads from being
started for the same quorum concurrently.

The previous implementation had a race condition where multiple threads
could pass the initial check before any of them set the flag, leading
to potential resource conflicts and duplicate operations.

This change ensures thread-safe access to fQuorumDataRecoveryThreadRunning
using compare_exchange_strong, eliminating the race condition window.

## Patch
### src/llmq/quorums.cpp
```diff
@@ -923,11 +923,11 @@ void CQuorumManager::StartQuorumDataRecoveryThread(CConnman& connman, const CQuo
 {
     assert(m_mn_activeman);
 
-    if (pQuorum->fQuorumDataRecoveryThreadRunning) {
+    bool expected = false;
+    if (!pQuorum->fQuorumDataRecoveryThreadRunning.compare_exchange_strong(expected, true)) {
         LogPrint(BCLog::LLMQ, "CQuorumManager::%s -- Already running\n", __func__);
         return;
     }
-    pQuorum->fQuorumDataRecoveryThreadRunning = true;
 
     workerPool.push([&connman, pQuorum, pIndex, nDataMaskIn, this](int threadId) {
         size_t nTries{0};
```
