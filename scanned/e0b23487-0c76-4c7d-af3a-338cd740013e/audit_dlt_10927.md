# [?] Fix VC after race condition fix

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2019-02-27
Source: https://github.com/Zilliqa/zq1/commit/c65664ff3bc61f26131e79f27978ac7578f1a5da
Type: security-commit

## Details
Fix VC after race condition fix

## Patch
### src/libDirectoryService/FinalBlockPreProcessing.cpp
```diff
@@ -1132,7 +1132,8 @@ void DirectoryService::RunConsensusOnFinalBlock() {
     lock_guard<mutex> g(m_mutexRunConsensusOnFinalBlock);
 
     if (!(m_state == VIEWCHANGE_CONSENSUS ||
-          m_state == MICROBLOCK_SUBMISSION)) {
+          m_state == MICROBLOCK_SUBMISSION || 
+          m_state == FINALBLOCK_CONSENSUS_PREP)) {
       LOG_GENERAL(WARNING,
                   "DirectoryService::RunConsensusOnFinalBlock "
                   "is not allowed in current state "
@@ -1152,7 +1153,9 @@ void DirectoryService::RunConsensusOnFinalBlock() {
       RejoinAsDS();
     }
 
-    SetState(FINALBLOCK_CONSENSUS_PREP);
+    if (m_state != FINALBLOCK_CONSENSUS_PREP) {
+      SetState(FINALBLOCK_CONSENSUS_PREP);
+    }
 
     m_mediator.m_node->PrepareGoodStateForFinalBlock();
 
```
