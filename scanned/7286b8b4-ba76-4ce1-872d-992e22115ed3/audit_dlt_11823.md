# [?] Fix missing support for this.variable() in reentrancy detector

## Summary
Severity: Unknown
Chain: Tooling
Component: crytic/slither
Published: 2019-02-12
Source: https://github.com/crytic/slither/commit/c0f9f09b59316c01e00820b8f93e752c2e5f6fc9
Type: security-commit

## Details
Fix missing support for this.variable() in reentrancy detector

## Patch
### slither/detectors/reentrancy/reentrancy.py
```diff
@@ -59,6 +59,8 @@ def _can_callback(self, irs):
                 # We can check that the function called is
                 # reentrancy-safe
                 if ir.destination == SolidityVariable('this'):
+                    if isinstance(ir.function, Variable):
+                        continue
                     if not ir.function.all_high_level_calls():
                         if not ir.function.all_low_level_calls():
                             continue
```
