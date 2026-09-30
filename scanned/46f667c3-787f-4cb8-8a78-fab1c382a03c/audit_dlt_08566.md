# [?] Fix overflow in incomplete eviction scan check

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/stellar-core
Published: 2024-03-02
Source: https://github.com/stellar/stellar-core/commit/452f4f5a3a13b27a11525ea7cd51ecb620773bc1
Type: security-commit

## Details
Fix overflow in incomplete eviction scan check

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
