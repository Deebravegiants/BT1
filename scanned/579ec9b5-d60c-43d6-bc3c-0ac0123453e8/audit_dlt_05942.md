# [?] fix[lang]: filter oob array access during folding (#4571)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2025-04-12
Source: https://github.com/vyperlang/vyper/commit/2d515d3b34097b05ee3bc9c6eaee3682f166cbd3
Type: security-commit

## Details
fix[lang]: filter oob array access during folding (#4571)

constant folding was not filtering out oob array index accesses. this is
because it was raising `UnfoldableNode`, which is caught by the folding
machinery. this commit changes it to an `ArrayIndexException`, which
will propagate to the user and abort compilation.

---------

Co-authored-by: cyberthirst <cyberthirst.eth@gmail.com>

## Patch
### tests/unit/ast/nodes/test_fold_subscript.py
```diff
@@ -46,3 +46,47 @@ def foo(array: int128[10]) -> int128:
     """
     with pytest.raises(ArrayIndexException):
         compile_code(source)
+
+
+failing_list = [
+    "MAX: constant(DynArray[uint256, 10]) = [1, 2, 3]",
+    "MAX: constant(uint256[3]) = [1, 2, 3]",
+    "MAX: constant((uint256, uint256, uint256)) = (1, 2, 3)",
+]
+
+
+@pytest.mark.parametrize("decl", failing_list)
+def test_oob_index_for_subscriptable_types(decl):
+    source = f"""
+{decl}
+a: constant(uint256) = MAX[3]
+
+@external
+def foo() -> uint256:
+    return a
+    """
+    with pytest.raises(ArrayIndexException):
+        compile_code(source)
+
+
+def test_oob_index_subscript_within_subscript():
+    source = """
+MAX: constant(uint256[3]) = [1, 2, 3]
+a: constant(uint256) = MAX[MAX[0]+MAX[1]]
+
+@external
+def foo() -> uint256:
+    return a
+    """
+    with pytest.raises(ArrayIndexException):
+        compile_code(source)
+
+
+def test_oob_index_literal_array():
+    source = """
+@external
+def foo() -> uint256:
+    return [[1], [2], [3], [4]][0][1]
+    """
+    with pytest.raises(ArrayIndexException):
+        compile_code(source)
```

### vyper/semantics/analysis/constant_folding.py
```diff
@@ -1,5 +1,5 @@
 from vyper import ast as vy_ast
-from vyper.exceptions import InvalidLiteral, UnfoldableNode, VyperException
+from vyper.exceptions import ArrayIndexException, InvalidLiteral, UnfoldableNode, VyperException
 from vyper.semantics.analysis.base import VarInfo
 from vyper.semantics.analysis.common import VyperNodeVisitorBase
 from vyper.semantics.namespace import get_namespace
@@ -235,6 +235,6 @@ def visit_Subscript(self, node) -> vy_ast.ExprNode:
 
         idx = slice_.value
         if idx < 0 or idx >= len(elements):
-            raise UnfoldableNode("invalid index value")
+            raise ArrayIndexException("out of bounds", node.slice)
 
         return elements[idx]
```
