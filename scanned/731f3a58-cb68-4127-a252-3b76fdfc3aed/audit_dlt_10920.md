# [?] Fix possible race condition

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2019-10-24
Source: https://github.com/Zilliqa/zq1/commit/90312891ad5c137fd71840bfffe220d900d5df4b
Type: security-commit

## Details
Fix possible race condition

## Patch
### src/libDirectoryService/MicroBlockProcessing.cpp
```diff
@@ -205,16 +205,20 @@ bool DirectoryService::ProcessMicroblockSubmissionFromShardCore(
   }
 
   uint32_t shardId = microBlock.GetHeader().GetShardId();
-  auto& microBlocksAtEpoch = m_microBlocks[m_mediator.m_currentEpochNum];
-
-  // Check if we already received a validated microblock with the same shard id.
-  // Save on unnecessary-validation.
-  if (find_if(microBlocksAtEpoch.begin(), microBlocksAtEpoch.end(),
-              [shardId](const MicroBlock& mb) -> bool {
-                return mb.GetHeader().GetShardId() == shardId;
-              }) != microBlocksAtEpoch.end()) {
-    LOG_GENERAL(WARNING, "Duplicate microblock received for shard " << shardId);
-    return false;
+  {
+    lock_guard<mutex> g(m_mutexMicroBlocks);
+    auto& microBlocksAtEpoch = m_microBlocks[m_mediator.m_currentEpochNum];
+
+    // Check if we already received a validated microblock with the same shard
+    // id. Save on unnecessary-validation.
+    if (find_if(microBlocksAtEpoch.begin(), microBlocksAtEpoch.end(),
+                [shardId](const MicroBlock& mb) -> bool {
+                  return mb.GetHeader().GetShardId() == shardId;
+                }) != microBlocksAtEpoch.end()) {
+      LOG_GENERAL(WARNING,
+                  "Duplicate microblock received for shard " << shardId);
+      return false;
+    }
   }
 
   // Verify the Block Hash
@@ -325,6 +329,7 @@ bool DirectoryService::ProcessMicroblockSubmissionFromShardCore(
     }
   }
 
+  auto& microBlocksAtEpoch = m_microBlocks[m_mediator.m_currentEpochNum];
   microBlocksAtEpoch.emplace(microBlock);
 
   LOG_EPOCH(INFO, m_mediator.m_currentEpochNum,
```
