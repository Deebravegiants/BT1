# [?] Merge pull request #4227 from SirTyson/fix-metric-overflow

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/stellar-core
Published: 2024-03-04
Source: https://github.com/stellar/stellar-core/commit/2a1c4564d6b6ae7b8c3f94a2719b9fd0b05fc869
Type: security-commit

## Details
Merge pull request #4227 from SirTyson/fix-metric-overflow

Fix overflow in incomplete eviction scan check

Reviewed-by: anupsdf

## Patch
### src/bucket/BucketList.cpp
```diff
@@ -893,8 +893,8 @@ BucketList::scanForEviction(Application& app, AbstractLedgerTxn& ltx,
         // Check to see if we can finish scanning the bucket before it receives
         // an update. To prevent noisy warnings, we assume we have the entire
         // period to scan the bucket.
-        auto period = bucketUpdatePeriod(evictionIter.bucketListLevel,
-                                         evictionIter.isCurrBucket);
+        uint64_t period = bucketUpdatePeriod(evictionIter.bucketListLevel,
+                                             evictionIter.isCurrBucket);
         if (period * scanSize < b->getSize())
         {
             CLOG_WARNING(Bucket,
```
