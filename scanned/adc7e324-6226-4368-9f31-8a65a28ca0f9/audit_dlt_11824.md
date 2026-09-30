# [?] Improve reentrancy heuristic: ignore call to this. if the destination is reentrancy-safe (close #127)

## Summary
Severity: Unknown
Chain: Tooling
Component: crytic/slither
Published: 2019-02-09
Source: https://github.com/crytic/slither/commit/02661eb0ffff56f4fff60f3e00fd065ef9d8332e
Type: security-commit

## Details
Improve reentrancy heuristic: ignore call to this. if the destination is reentrancy-safe (close #127)

## Patch
### slither/detectors/reentrancy/reentrancy.py
```diff
@@ -6,7 +6,7 @@
 """
 
 from slither.core.cfg.node import NodeType
-from slither.core.declarations import Function, SolidityFunction
+from slither.core.declarations import Function, SolidityFunction, SolidityVariable
 from slither.core.expressions import UnaryOperation, UnaryOperationType
 from slither.detectors.abstract_detector import (AbstractDetector,
                                                  DetectorClassification)
@@ -55,6 +55,13 @@ def _can_callback(self, irs):
                         continue
                     if isinstance(ir.function, Variable):
                         continue
+                # If there is a call to itself
+                # We can check that the function called is
+                # reentrancy-safe
+                if ir.destination == SolidityVariable('this'):
+                    if not ir.function.all_high_level_calls():
+                        if not ir.function.all_low_level_calls():
+                            continue
                 return True
         return False
 
```
