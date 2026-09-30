# [?] Remove reentrancy FP due to call to view/pure functions or state variable getters (fix #126)

## Summary
Severity: Unknown
Chain: Tooling
Component: crytic/slither
Published: 2019-02-05
Source: https://github.com/crytic/slither/commit/77cd643360111b56328b4c15b1e68373c6fa9953
Type: security-commit

## Details
Remove reentrancy FP due to call to view/pure functions or state variable getters (fix #126)

## Patch
### slither/detectors/reentrancy/reentrancy.py
```diff
@@ -13,6 +13,7 @@
 from slither.slithir.operations import (HighLevelCall, LowLevelCall,
                                         LibraryCall,
                                         Send, Transfer)
+from slither.core.variables.variable import Variable
 
 def union_dict(d1, d2):
     d3 = {k: d1.get(k, set()) | d2.get(k, set()) for k in set(list(d1.keys()) + list(d2.keys()))}
@@ -49,6 +50,10 @@ def _can_callback(irs):
             if isinstance(ir, LowLevelCall):
                 return True
             if isinstance(ir, HighLevelCall) and not isinstance(ir, LibraryCall):
+                if isinstance(ir.function, Function) and (ir.function.view or ir.function.pure):
+                    continue
+                if isinstance(ir.function, Variable):
+                    continue
                 return True
         return False
 
```
