# [?] miner: never create a template which exploits the timewarp bug

## Summary
Severity: Unknown
Chain: Liquid
Component: ElementsProject/elements
Published: 2024-11-26
Source: https://github.com/ElementsProject/elements/commit/733fa0b0a140fc1e40c644a29953db090baa2890
Type: security-commit

## Details
miner: never create a template which exploits the timewarp bug

## Patch
### src/node/miner.cpp
```diff
@@ -33,12 +33,10 @@ int64_t UpdateTime(CBlockHeader* pblock, const Consensus::Params& consensusParam
     int64_t nOldTime = pblock->nTime;
     int64_t nNewTime{std::max<int64_t>(pindexPrev->GetMedianTimePast() + 1, TicksSinceEpoch<std::chrono::seconds>(NodeClock::now()))};
 
-    if (consensusParams.enforce_BIP94) {
-        // Height of block to be mined.
-        const int height{pindexPrev->nHeight + 1};
-        if (height % consensusParams.DifficultyAdjustmentInterval() == 0) {
-            nNewTime = std::max<int64_t>(nNewTime, pindexPrev->GetBlockTime() - MAX_TIMEWARP);
-        }
+    // Height of block to be mined.
+    const int height{pindexPrev->nHeight + 1};
+    if (height % consensusParams.DifficultyAdjustmentInterval() == 0) {
+        nNewTime = std::max<int64_t>(nNewTime, pindexPrev->GetBlockTime() - MAX_TIMEWARP);
     }
 
     if (nOldTime < nNewTime) {
```
