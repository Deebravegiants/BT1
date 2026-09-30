# [?] fix: timestamp overflow

## Summary
Severity: Unknown
Chain: Morpho
Component: morpho-org/morpho-blue
Published: 2023-08-25
Source: https://github.com/morpho-org/morpho-blue/commit/b8538fee642c8fadfca405c5d8304376198f0020
Type: security-commit

## Details
fix: timestamp overflow

## Patch
### certora/specs/BlueAccrueInterests.spec
```diff
@@ -38,6 +38,8 @@ rule supplyAccruesInterests()
     address onbehalf;
     bytes data;
 
+    require e.block.timestamp < 2^128;
+
     storage init = lastStorage;
 
     // check that calling accrueInterest first has no effect.
@@ -63,6 +65,8 @@ rule withdrawAccruesInterests()
     address onbehalf;
     address receiver;
 
+    require e.block.timestamp < 2^128;
+
     storage init = lastStorage;
 
     // check that calling accrueInterest first has no effect.
@@ -88,6 +92,8 @@ rule borrowAccruesInterests()
     address onbehalf;
     address receiver;
 
+    require e.block.timestamp < 2^128;
+
     storage init = lastStorage;
 
     // check that calling accrueInterest first has no effect.
@@ -113,6 +119,8 @@ rule repayAccruesInterests()
     address onbehalf;
     bytes data;
 
+    require e.block.timestamp < 2^128;
+
     storage init = lastStorage;
 
     // check that calling accrueInterest first has no effect.
@@ -148,6 +156,7 @@ filtered {
     MorphoHarness.MarketParams marketParams;
 
     require e1.block.timestamp == e2.block.timestamp;
+    require e1.block.timestamp < 2^128;
 
     storage init = lastStorage;
 
```
