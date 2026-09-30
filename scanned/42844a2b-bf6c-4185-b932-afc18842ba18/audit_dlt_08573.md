# [?] fix: captive core crashes with all invariants enabled

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/stellar-core
Published: 2021-10-09
Source: https://github.com/stellar/stellar-core/commit/14a86866267fb314a0d66eff2e02b127cf5d2775
Type: security-commit

## Details
fix: captive core crashes with all invariants enabled

disable bucketlist check invariant that relies on SQL

## Patch
### src/main/ApplicationImpl.cpp
```diff
@@ -274,9 +274,10 @@ ApplicationImpl::initialize(bool createNewDB, bool forceRebuild)
             mConfig.BEST_OFFER_DEBUGGING_ENABLED
 #endif
         );
+
+        BucketListIsConsistentWithDatabase::registerInvariant(*this);
     }
 
-    BucketListIsConsistentWithDatabase::registerInvariant(*this);
     AccountSubEntriesCountIsValid::registerInvariant(*this);
     ConservationOfLumens::registerInvariant(*this);
     LedgerEntryIsValid::registerInvariant(*this);
```
