# [?] Merge pull request #1550 from davesque/fix-reentrant-constant

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2019-07-25
Source: https://github.com/vyperlang/vyper/commit/ac417a38b7e598e8a9f672b010da202e187f31c2
Type: security-commit

## Details
Merge pull request #1550 from davesque/fix-reentrant-constant

Fix compilable constant, nonreentrant functions

## Patch
### tests/signatures/test_invalid_function_decorators.py
```diff
@@ -0,0 +1,24 @@
+import pytest
+
+from vyper import (
+    compiler,
+)
+from vyper.exceptions import (
+    StructureException,
+)
+
+FAILING_CONTRACTS = [
+    """
+@public
+@constant
+@nonreentrant('lock')
+def nonreentrant_foo() -> uint256:
+    return 1
+    """,
+]
+
+
+@pytest.mark.parametrize('failing_contract_code', FAILING_CONTRACTS)
+def test_invalid_function_decorators(failing_contract_code):
+    with pytest.raises(StructureException):
+        compiler.compile_code(failing_contract_code)
```

### vyper/parser/parser.py
```diff
@@ -96,7 +96,7 @@ def parse_external_contracts(external_contracts, global_ctx):
             sig = FunctionSignature.from_definition(
                 _def,
                 contract_def=True,
-                constant=constant,
+                constant_override=constant,
                 custom_structs=global_ctx._structs,
                 constants=global_ctx._constants
             )
```

### vyper/signatures/function_signature.py
```diff
@@ -157,7 +157,7 @@ def from_definition(cls,
                         custom_structs=None,
                         contract_def=False,
                         constants=None,
-                        constant=False):
+                        constant_override=False):
         if not custom_structs:
             custom_structs = {}
 
@@ -219,8 +219,13 @@ def from_definition(cls,
             else:
                 mem_pos += get_size_of_type(parsed_type) * 32
 
-        # Apply decorators
-        const, payable, private, public, nonreentrant_key = False, False, False, False, ''
+        const = constant_override
+        payable = False
+        private = False
+        public = False
+        nonreentrant_key = ''
+
+        # Update function properties from decorators
         for dec in code.decorator_list:
             if isinstance(dec, ast.Name) and dec.id == "constant":
                 const = True
@@ -258,10 +263,9 @@ def from_definition(cls,
                 "Function visibility must be declared (@public or @private)",
                 code,
             )
-        if constant and nonreentrant_key:
+        if const and nonreentrant_key:
             raise StructureException("@nonreentrant makes no sense on a @constant function.", code)
-        if constant:
-            const = True
+
         # Determine the return type and whether or not it's constant. Expects something
         # of the form:
         # def foo(): ...
```
