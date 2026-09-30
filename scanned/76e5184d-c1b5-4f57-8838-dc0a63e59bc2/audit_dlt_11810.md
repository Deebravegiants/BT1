# [?] Fix crash when casting a string to byte*

## Summary
Severity: Unknown
Chain: Tooling
Component: crytic/slither
Published: 2025-05-26
Source: https://github.com/crytic/slither/commit/666e61b9ff9a75134115b2d6b02c6543fac8b3ef
Type: security-commit

## Details
Fix crash when casting a string to byte*

## Patch
### slither/visitors/expression/constants_folding.py
```diff
@@ -450,6 +450,8 @@ def _post_type_conversion(self, expression: expressions.TypeConversion) -> None:
             value = int.from_bytes(expr.value, "big")
         elif str(expression.type).startswith("byte") and isinstance(expr.value, int):
             value = int.to_bytes(expr.value, 32, "big")
+        elif str(expression.type).startswith("byte") and isinstance(expr.value, str):
+            value = expr.value
         else:
             value = convert_string_to_fraction(expr.converted_value)
         set_val(expression, value)
```
