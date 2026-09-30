# [?] Fix overflow error handling in ConservationOfLumens

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/stellar-core
Published: 2025-12-19
Source: https://github.com/stellar/stellar-core/commit/3647e1e1bd8975e142e8e7dadc24fd6f6767cd4d
Type: security-commit

## Details
Fix overflow error handling in ConservationOfLumens

Previously, processEntryIfNew would log overflow errors but allow the
invariant to continue, causing it to pass despite data corruption. Now
passes error string by reference and returns it from the invariant,
causing proper failure on overflow.

Changes:
- Add errorMsg parameter to processEntryIfNew
- Remove CLOG_ERROR calls, use fmt::format to set errorMsg
- Update scanLiveBucket and scanHotArchiveBucket to accept and pass errorMsg
- Check errorMsg after scan phases and return immediately if set

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

## Patch
### src/invariant/ConservationOfLumens.cpp
```diff
@@ -176,13 +176,13 @@ ConservationOfLumens::checkOnOperationApply(
 }
 
 // Helper function that processes an entry if it hasn't been seen before.
-// Returns true on success, false on error (with error logged).
+// Returns true on success, false on error (with error set in errorMsg).
 static bool
 processEntryIfNew(LedgerEntry const& entry, LedgerKey const& key,
                   std::unordered_set<LedgerKey>& countedKeys,
                   Asset const& asset,
                   AssetContractInfo const& assetContractInfo,
-                  int64_t& sumBalance)
+                  int64_t& sumBalance, std::string& errorMsg)
 {
     if (countedKeys.count(key) != 0)
     {
@@ -193,9 +193,10 @@ processEntryIfNew(LedgerEntry const& entry, LedgerKey const& key,
 
     if (result.overflowed)
     {
-        CLOG_ERROR(Tx,
-                   "ConservationOfLumens: getAssetBalance overflow for key: {}",
-                   xdrToCerealString(key, "ledger_key"));
+        errorMsg = fmt::format(
+            FMT_STRING(
+                "ConservationOfLumens: getAssetBalance overflow for key: {}"),
+            xdrToCerealString(key, "ledger_key"));
         return false;
     }
 
@@ -206,9 +207,10 @@ processEntryIfNew(LedgerEntry const& entry, LedgerKey const& key,
 
     if (!result.balance || !addBalance(sumBalance, *result.balance))
     {
-        CLOG_ERROR(Tx,
-                   "ConservationOfLumens: Overflow adding balance for key: {}",
-                   xdrToCerealString(key, "ledger_key"));
+        errorMsg = fmt::format(
+            FMT_STRING(
+                "ConservationOfLumens: Overflow adding balance for key: {}"),
+            xdrToCerealString(key, "ledger_key"));
         return false;
     }
 
@@ -221,7 +223,7 @@ static Loop
 scanLiveBucket(LiveBucketSnapshot const& bucket,
                std::unordered_set<LedgerKey>& countedKeys, Asset const& asset,
                AssetContractInfo const& assetContractInfo, int64_t& sumBalance,
-               std::function<bool()> const& isStopping)
+               std::string& errorMsg, std::function<bool()> const& isStopping)
 {
     for (LiveBucketInputIterator iter(bucket.getRawBucket()); iter; ++iter)
     {
@@ -238,9 +240,9 @@ scanLiveBucket(LiveBucketSnapshot const& bucket,
             {
                 continue;
             }
-            if (!processEntryIfNew(be.liveEntry(),
-                                   LedgerEntryKey(be.liveEntry()), countedKeys,
-                                   asset, assetContractInfo, sumBalance))
+            if (!processEntryIfNew(
+                    be.liveEntry(), LedgerEntryKey(be.liveEntry()), countedKeys,
+                    asset, assetContractInfo, sumBalance, errorMsg))
             {
                 return Loop::COMPLETE;
             }
@@ -259,7 +261,7 @@ scanHotArchiveBucket(HotArchiveBucketSnapshot const& bucket,
                      std::unordered_set<LedgerKey>& countedKeys,
                      Asset const& asset,
                      AssetContractInfo const& assetContractInfo,
-                     int64_t& sumBalance,
+                     int64_t& sumBalance, std::string& errorMsg,
                      std::function<bool()> const& isStopping)
 {
     for (HotArchiveBucketInputIterator iter(bucket.getRawBucket()); iter;
@@ -278,9 +280,10 @@ scanHotArchiveBucket(HotArchiveBucketSnapshot const& bucket,
             {
                 continue;
             }
-            if (!processEntryIfNew(
-                    be.archivedEntry(), LedgerEntryKey(be.archivedEntry()),
-                    countedKeys, asset, assetContractInfo, sumBalance))
+            if (!processEntryIfNew(be.archivedEntry(),
+                                   LedgerEntryKey(be.archivedEntry()),
+                                   countedKeys, asset, assetContractInfo,
+                                   sumBalance, errorMsg))
             {
                 return Loop::COMPLETE;
             }
@@ -319,6 +322,7 @@ ConservationOfLumens::checkSnapshot(
     Asset nativeAsset(ASSET_TYPE_NATIVE);
 
     int64_t sumBalance = 0;
+    std::string errorMsg;
 
     // Start with the fee pool from the ledger header
     if (!addBalance(sumBalance, header.feePool))
@@ -334,11 +338,17 @@ ConservationOfLumens::checkSnapshot(
     {
         std::unordered_set<LedgerKey> countedKeys;
         liveSnapshot->loopAllBuckets([&countedKeys, &nativeAsset, &sumBalance,
-                                      &isStopping,
+                                      &errorMsg, &isStopping,
                                       this](LiveBucketSnapshot const& bucket) {
             return scanLiveBucket(bucket, countedKeys, nativeAsset,
-                                  mLumenContractInfo, sumBalance, isStopping);
+                                  mLumenContractInfo, sumBalance, errorMsg,
+                                  isStopping);
         });
+
+        if (!errorMsg.empty())
+        {
+            return errorMsg;
+        }
     }
 
     // Check if we should stop before scanning hot archive
@@ -351,12 +361,17 @@ ConservationOfLumens::checkSnapshot(
     {
         std::unordered_set<LedgerKey> countedKeys;
         hotArchiveSnapshot->loopAllBuckets(
-            [&countedKeys, &nativeAsset, &sumBalance, &isStopping,
+            [&countedKeys, &nativeAsset, &sumBalance, &errorMsg, &isStopping,
              this](HotArchiveBucketSnapshot const& bucket) {
                 return scanHotArchiveBucket(bucket, countedKeys, nativeAsset,
                                             mLumenContractInfo, sumBalance,
-                                            isStopping);
+                                            errorMsg, isStopping);
             });
+
+        if (!errorMsg.empty())
+        {
+            return errorMsg;
+        }
     }
 
     // We stopped early, so it's likely we didn't finish scanning everything
```
