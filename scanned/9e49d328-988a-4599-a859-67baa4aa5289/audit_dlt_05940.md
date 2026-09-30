# [?] fix[ux]: panic explicitly in `safe_pow()` for two-variable case (#5134)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2026-06-23
Source: https://github.com/vyperlang/vyper/commit/751931ff6993f2ec742a867eecb951d2229d6536
Type: security-commit

## Details
fix[ux]: panic explicitly in `safe_pow()` for two-variable case (#5134)

the else branch of `safe_pow()` (neither base nor exponent is a compile-
time constant) silently `return`ed `None`, which propagates into IR
construction in `expr.py` and would surface as a cryptic downstream
crash if the front-end guard were ever bypassed.

raise `CodegenPanic("unreachable")` instead of returning `None`,
matching the defensive `raise` style used a few lines above. the branch
is unreachable today because the type checker rejects two-variable
exponentiation with `InvalidOperation`, so mark it `# pragma: nocover`.

fixes GH 5026

## Patch
### vyper/codegen/arithmetic.py
```diff
@@ -10,7 +10,7 @@
     is_numeric_type,
 )
 from vyper.codegen.ir_node import IRnode
-from vyper.exceptions import CompilerPanic, TypeCheckFailure, UnimplementedException
+from vyper.exceptions import CodegenPanic, CompilerPanic, TypeCheckFailure, UnimplementedException
 
 
 def calculate_largest_power(a: int, num_bits: int, is_signed: bool) -> int:
@@ -368,11 +368,9 @@ def safe_pow(x, y):
                 ok = ["and", ["sge", x, lower_bound], ["sle", x, upper_bound]]
             else:
                 ok = ["le", x, upper_bound]
-    else:
-        # `a ** b` where neither `a` or `b` are known
-        # TODO this is currently unreachable, once we implement a way to do it safely
-        # remove the check in `vyper/context/types/value/numeric.py`
-        return
+    else:  # pragma: nocover
+        # type checker guarantees pow has at least one literal operand
+        raise CodegenPanic("unreachable")
 
     assertion = IRnode.from_list(["assert", ok], error_msg="safepow")
     return IRnode.from_list(["seq", assertion, ["exp", x, y]])
```
