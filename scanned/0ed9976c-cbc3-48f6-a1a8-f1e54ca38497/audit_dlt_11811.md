# [?] Fix crash when casting an address and accessing its members

## Summary
Severity: Unknown
Chain: Tooling
Component: crytic/slither
Published: 2025-05-26
Source: https://github.com/crytic/slither/commit/beb6dd925fb360a45b6077861c49bfad5610da79
Type: security-commit

## Details
Fix crash when casting an address and accessing its members

## Patch
### slither/visitors/expression/constants_folding.py
```diff
@@ -356,6 +356,14 @@ def _post_member_access(self, expression: expressions.MemberAccess) -> None:
         ):
             # User defined type .wrap call handled in _post_call_expression
             return
+        elif (
+            isinstance(expression.expression, TypeConversion)
+            and expression.expression.type == ElementaryType("address")
+            and expression.member_name in ["balance", "code", "codehash"]
+        ):
+            # We need to raise NotConstant for these case here otherwise expression.expression.value would crash in the following condition
+            # because TypeConversion does not have a value. See https://github.com/crytic/slither/issues/2717
+            raise NotConstant
         elif (
             isinstance(expression.expression.value, Contract)
             and expression.member_name in expression.expression.value.variables_as_dict
```
