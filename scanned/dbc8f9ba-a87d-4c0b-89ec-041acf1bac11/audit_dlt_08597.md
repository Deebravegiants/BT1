# [?] Enable underflow fix after specified date

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2016-01-27
Source: https://github.com/XRPLF/rippled/commit/278f679bb1355171919df556b8b7614847cc056c
Type: security-commit

## Details
Enable underflow fix after specified date

## Patch
### src/ripple/app/tests/Offer.test.cpp
```diff
@@ -153,7 +153,7 @@ class Offer_test : public beast::unit_test::suite
         {
             auto const closeTime = STAmountSO::soTime + timeDelta;
             env.close (closeTime);
-            *stAmountCalcSwitchover = closeTime <= STAmountSO::soTime;
+            *stAmountCalcSwitchover = closeTime > STAmountSO::soTime;
             // Will fail without the underflow fix
             auto expectedResult = *stAmountCalcSwitchover ?
                 tesSUCCESS : tecPATH_PARTIAL;
```

### src/ripple/protocol/STAmount.h
```diff
@@ -410,7 +410,7 @@ class STAmountSO
     explicit STAmountSO(NetClock::time_point const closeTime)
         : saved_(*stAmountCalcSwitchover)
     {
-        *stAmountCalcSwitchover = closeTime <= soTime;
+        *stAmountCalcSwitchover = closeTime > soTime;
     }
 
     ~STAmountSO()
```
