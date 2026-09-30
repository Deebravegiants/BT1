# [?] Fix overflow in BumpSequence "large bump" test

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/stellar-core
Published: 2021-02-27
Source: https://github.com/stellar/stellar-core/commit/a64d1172ccb449c5c6986017bf532d2a19e42212
Type: security-commit

## Details
Fix overflow in BumpSequence "large bump" test

Also add an assertion to TestAccount::nextSequenceNumber()
to catch anything similar.

## Patch
### src/test/TestAccount.h
```diff
@@ -132,6 +132,11 @@ class TestAccount
     nextSequenceNumber()
     {
         updateSequenceNumber();
+        if (mSn == std::numeric_limits<SequenceNumber>::max())
+        {
+            throw std::runtime_error(
+                "Sequence number overflow in test account");
+        }
         return ++mSn;
     }
     SequenceNumber loadSequenceNumber();
```

### src/transactions/test/BumpSequenceTests.cpp
```diff
@@ -51,7 +51,12 @@ TEST_CASE("bump sequence", "[tx][bumpsequence]")
                 REQUIRE(a.loadSequenceNumber() == newSeq);
                 SECTION("no more tx when INT64_MAX is reached")
                 {
-                    REQUIRE_THROWS_AS(a.pay(root, 1), ex_txBAD_SEQ);
+                    REQUIRE_THROWS_AS(
+                        applyTx(
+                            {a.tx({payment(root, 1)},
+                                  std::numeric_limits<SequenceNumber>::min())},
+                            *app),
+                        ex_txBAD_SEQ);
                 }
             }
             SECTION("backward jump (no-op)")
```
