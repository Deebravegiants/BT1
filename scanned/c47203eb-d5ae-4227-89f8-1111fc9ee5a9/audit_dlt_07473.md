# [?] Merge #6787: fix: resolve race condition in quorum data recovery thread management

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2025-07-30
Source: https://github.com/dashpay/dash/commit/b13797967a22e7db4e78b632db4e55965047cd84
Type: security-commit

## Details
Merge #6787: fix: resolve race condition in quorum data recovery thread management

0e2811f22a85da6cdc12952303d49a3ce5a24831 fix: resolve race condition in quorum data recovery thread management (pasta)

Pull request description:

  ## Summary

  This PR fixes a thread safety issue in the quorum data recovery system where multiple threads could be started for the same quorum due to a race condition.

  ### Problem

  The original code used a check-then-set pattern:
  ```cpp
  if (pQuorum->fQuorumDataRecoveryThreadRunning) {  // Check
      return;
  }
  pQuorum->fQuorumDataRecoveryThreadRunning = true;  // Set
  ```

  Even though `fQuorumDataRecoveryThreadRunning` is declared as `std::atomic<bool>`, this pattern creates a race condition window where multiple threads can pass the check before any of them sets the flag.

  ### Solution

  Replace the check-then-set pattern with an atomic `compare_exchange_strong` operation:
  ```cpp
  bool expected = false;
  if (\!pQuorum->fQuorumDataRecoveryThreadRunning.compare_exchange_strong(expected, true)) {
      return;
  }
  ```

  This ensures thread-safe access by atomically checking the current value and setting it to `true` only if it was previously `false`.

  ### Impact

  - Prevents multiple data recovery threads from being started for the same quorum
  - Eliminates potential resource conflicts and duplicate operations
  - Maintains the same functional behavior while ensuring thread safety

  ## Test plan

  - [x] Code compiles successfully
  - [x] Change maintains existing API and functionality
  - [x] Race condition eliminated through atomic operation

  Generated with [Claude Code](https://claude.ai/code)

ACKs for top commit:
  UdjinM6:
    utACK 0e2811f22a85da6cdc12952303d49a3ce5a24831

Tree-SHA512: eff2798d535ba10d3baacb4b8aab731b6b0090d5f05c77c98beee07d116221184684d27bcacdbbf3cd8f63af952464dff2e7e2737c9c4c19f9fadef92424be81

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
