# [?] Avoid overflow in ExchangeTests with bigMultiply()

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/stellar-core
Published: 2021-03-01
Source: https://github.com/stellar/stellar-core/commit/44baa22ae00005d613537f600a816aaa0f3791a0
Type: security-commit

## Details
Avoid overflow in ExchangeTests with bigMultiply()

## Patch
### src/transactions/test/ExchangeTests.cpp
```diff
@@ -745,8 +745,9 @@ TEST_CASE("ExchangeV10", "[exchange]")
             else
             {
                 REQUIRE(res.wheatStays ==
-                        (maxWheatSend * p.n >
-                         std::min(maxSheepSend * p.d, maxWheatReceive * p.n)));
+                        bigMultiply(maxWheatSend, p.n) >
+                            std::min(bigMultiply(maxSheepSend, p.d),
+                                     bigMultiply(maxWheatReceive, p.n)));
             }
             REQUIRE(res.numWheatReceived == wheatReceive);
             REQUIRE(res.numSheepSend == sheepSend);
```
