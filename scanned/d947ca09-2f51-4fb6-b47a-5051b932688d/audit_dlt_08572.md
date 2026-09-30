# [?] Avoid crashing when TxMeta checks fail.

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/stellar-core
Published: 2021-08-09
Source: https://github.com/stellar/stellar-core/commit/5d62266da05c784513d70be9e71cff217801a582
Type: security-commit

## Details
Avoid crashing when TxMeta checks fail.

## Patch
### src/test/test.cpp
```diff
@@ -581,8 +581,16 @@ recordOrCheckGlobalTestTxMetadata(TransactionMeta const& txMeta)
         releaseAssert(gTestTxMetaMode == TestTxMetaMode::META_TEST_CHECK);
         auto i = gTestTxMetadata.find(ctx);
         CHECK(i != gTestTxMetadata.end());
+        if (i == gTestTxMetadata.end())
+        {
+            return;
+        }
         std::vector<Hash>& vec = i->second;
         CHECK(!vec.empty());
+        if (vec.empty())
+        {
+            return;
+        }
         Hash& expectedTxMetaHash = vec.back();
         CHECK(expectedTxMetaHash == gotTxMetaHash);
         vec.pop_back();
```
