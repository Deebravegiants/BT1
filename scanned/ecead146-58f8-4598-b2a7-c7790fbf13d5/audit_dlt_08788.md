# [?] fix(oob): inst modexp pircing f of max (#1107)

## Summary
Severity: Unknown
Chain: Linea
Component: LFDT-Lineth/lineth-monorepo
Published: 2024-09-05
Source: https://github.com/LFDT-Lineth/lineth-monorepo/commit/212182ba2537138327b6212cccd73526a7d011bb
Type: security-commit

## Details
fix(oob): inst modexp pircing f of max (#1107)

* fix(oob): inst modexp pircing f of max

* fix(oob): naming ceilingOfMaxDividedBy8

## Patch
### tracer/arithmetization/src/main/java/net/consensys/linea/zktracer/module/oob/OobOperation.java
```diff
@@ -1074,16 +1074,14 @@ private void setModexpPricing(ModexpPricingOobCall prcModexpPricingOobCall) {
         callToISZERO(1, BigInteger.ZERO, prcModexpPricingOobCall.getExponentLog());
 
     // row i + 2
-    final BigInteger fOfMax =
+    final BigInteger ceilingOfMaxDividedBy8 =
         callToDIV(
             2,
             BigInteger.ZERO,
-            BigInteger.valueOf(
-                (long) prcModexpPricingOobCall.getMaxMbsBbs()
-                        * prcModexpPricingOobCall.getMaxMbsBbs()
-                    + 7),
+            BigInteger.valueOf((long) prcModexpPricingOobCall.getMaxMbsBbs() + 7),
             BigInteger.ZERO,
             BigInteger.valueOf(8));
+    final BigInteger fOfMax = ceilingOfMaxDividedBy8.multiply(ceilingOfMaxDividedBy8);
 
     // row i + 3
     BigInteger bigNumerator;
```

### tracer/linea-constraints
```diff
@@ -1 +1 @@
-Subproject commit c9e660b0fa57e20c61d950a74c7c6366fbffe3a2
+Subproject commit 7fe32e2761e3246628fc135dd5e3837e01ba1295
```
