# [?] Merge bitcoin/bitcoin#31376: Miner: never create a template which exploits the timewarp bug

## Summary
Severity: Unknown
Chain: Liquid
Component: ElementsProject/elements
Published: 2025-01-23
Source: https://github.com/ElementsProject/elements/commit/59876b3ad71c4746737f2899c24679d4034de373
Type: security-commit

## Details
Merge bitcoin/bitcoin#31376: Miner: never create a template which exploits the timewarp bug

733fa0b0a140fc1e40c644a29953db090baa2890 miner: never create a template which exploits the timewarp bug (Antoine Poinsot)

Pull request description:

  This check was introduced in #30681 but only enabled for testnet4. To avoid potentially creating an invalid block template if a soft fork to fix the timewarp attack were to activate in the future, we should have this check on all networks. It also seems wise for our miner to not support it whether or not a soft fork activates to fix it at the consensus level.

ACKs for top commit:
  Sjors:
    ACK 733fa0b0a140fc1e40c644a29953db090baa2890
  fjahr:
    utACK 733fa0b0a140fc1e40c644a29953db090baa2890
  TheCharlatan:
    ACK 733fa0b0a140fc1e40c644a29953db090baa2890

Tree-SHA512: 9b3bc8b26a57f93425b17dda80bcfac4ecb750a3d26bc3eb8df619135634e369ac15982fac0c9770b1df207bd2e418ffe02a98f37968f024e55262d97715a4f5

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
