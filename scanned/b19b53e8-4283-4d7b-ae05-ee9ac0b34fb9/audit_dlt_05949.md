# [?] fix: compiler was panicking when a `break` is outside of a loop (#3177)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2022-12-07
Source: https://github.com/vyperlang/vyper/commit/1a568bf7378e93806f22b1beb873097bc1970ad4
Type: security-commit

## Details
fix: compiler was panicking when a `break` is outside of a loop (#3177)

* fixed the compiler panicking when a break is outside of a loop

* added tests and improved test for continue

Co-authored-by: Tanguy Rocher <tanguy.rocher@protonmail.com>

## Patch
### tests/parser/features/iteration/test_break.py
```diff
@@ -1,5 +1,9 @@
 from decimal import Decimal
 
+import pytest
+
+from vyper.exceptions import StructureException
+
 
 def test_break_test(get_contract_with_gas_estimation):
     break_test = """
@@ -79,3 +83,41 @@ def foo(n: int128) -> int128:
     assert c.foo(200) == 23
     assert c.foo(4000000) == 66
     print("Passed aug-assignment break composite test")
+
+
+fail_list = [
+    (
+        """
+@external
+def foo():
+    a: uint256 = 3
+    break
+    """,
+        StructureException,
+    ),
+    (
+        """
+@external
+def foo():
+    if True:
+        break
+    """,
+        StructureException,
+    ),
+    (
+        """
+@external
+def foo():
+    for i in [1, 2, 3]:
+        b: uint256 = i
+    if True:
+        break
+    """,
+        StructureException,
+    ),
+]
+
+
+@pytest.mark.parametrize("bad_code,exc", fail_list)
+def test_block_fail(assert_compile_failed, get_contract_with_gas_estimation, bad_code, exc):
+    assert_compile_failed(lambda: get_contract_with_gas_estimation(bad_code), exc)
```

### tests/parser/features/iteration/test_continue.py
```diff
@@ -1,5 +1,7 @@
 import pytest
 
+from vyper.exceptions import StructureException
+
 
 def test_continue1(get_contract_with_gas_estimation):
     code = """
@@ -59,29 +61,38 @@ def foo() -> int128:
 
 
 fail_list = [
-    """
+    (
+        """
 @external
 def foo():
     a: uint256 = 3
     continue
     """,
-    """
+        StructureException,
+    ),
+    (
+        """
 @external
 def foo():
     if True:
         continue
     """,
-    """
+        StructureException,
+    ),
+    (
+        """
 @external
 def foo():
     for i in [1, 2, 3]:
         b: uint256 = i
     if True:
         continue
     """,
+        StructureException,
+    ),
 ]
 
 
-@pytest.mark.parametrize("bad_code", fail_list)
-def test_block_fail(assert_compile_failed, get_contract_with_gas_estimation, bad_code):
-    assert_compile_failed(lambda: get_contract_with_gas_estimation(bad_code))
+@pytest.mark.parametrize("bad_code,exc", fail_list)
+def test_block_fail(assert_compile_failed, get_contract_with_gas_estimation, bad_code, exc):
+    assert_compile_failed(lambda: get_contract_with_gas_estimation(bad_code), exc)
```

### vyper/semantics/analysis/local.py
```diff
@@ -160,7 +160,7 @@ def _validate_msg_data_attribute(node: vy_ast.Attribute) -> None:
 
 class FunctionNodeVisitor(VyperNodeVisitorBase):
 
-    ignored_types = (vy_ast.Break, vy_ast.Constant, vy_ast.Pass)
+    ignored_types = (vy_ast.Constant, vy_ast.Pass)
     scope_name = "function"
 
     def __init__(
@@ -289,6 +289,11 @@ def visit_Continue(self, node):
         if for_node is None:
             raise StructureException("`continue` must be enclosed in a `for` loop", node)
 
+    def visit_Break(self, node):
+        for_node = node.get_ancestor(vy_ast.For)
+        if for_node is None:
+            raise StructureException("`break` must be enclosed in a `for` loop", node)
+
     def visit_Return(self, node):
         values = node.value
         if values is None:
```
