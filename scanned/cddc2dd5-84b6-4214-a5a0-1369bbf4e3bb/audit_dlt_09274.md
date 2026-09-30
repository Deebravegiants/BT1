# [?] modify sqrt calculations to avoid upper bound overflow

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2019-11-05
Source: https://github.com/vyperlang/vyper/commit/f0689901d8679df2205454d795bbf1ba99bd00b4
Type: security-commit

## Details
modify sqrt calculations to avoid upper bound overflow

## Patch
### vyper/functions/functions.py
```diff
@@ -1210,7 +1210,7 @@ def sqrt(expr, args, kwargs, context):
 if x == 0.0:
     z = 0.0
 else:
-    z = (x + 1.0) / 2.0
+    z = x / 2.0 + 0.5
     y: decimal = x
 
     for i in range(256):
```
