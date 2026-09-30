# [?] fix: powmod256 crash for large literal exponents (#3190)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2022-12-12
Source: https://github.com/vyperlang/vyper/commit/c1a3bf5cbee0f1f82fcdfb492582048d06dd8d12
Type: security-commit

## Details
fix: powmod256 crash for large literal exponents (#3190)

use python builtin powmod (`pow(x,y,z)`) - which uses constant space
memory instead of calculating `x ** y % z`

## Patch
### tests/builtins/folding/test_powmod.py
```diff
@@ -5,7 +5,7 @@
 from vyper import ast as vy_ast
 from vyper.builtins import functions as vy_fn
 
-st_uint256 = st.integers(min_value=0, max_value=256)
+st_uint256 = st.integers(min_value=0, max_value=2 ** 256)
 
 
 @pytest.mark.fuzzing
```

### vyper/builtins/functions.py
```diff
@@ -1571,7 +1571,7 @@ def evaluate(self, node):
         if left.value < 0 or right.value < 0:
             raise UnfoldableNode
 
-        value = (left.value ** right.value) % (2 ** 256)
+        value = pow(left.value, right.value, 2 ** 256)
         return vy_ast.Int.from_node(node, value=value)
 
     def build_IR(self, expr, context):
```
