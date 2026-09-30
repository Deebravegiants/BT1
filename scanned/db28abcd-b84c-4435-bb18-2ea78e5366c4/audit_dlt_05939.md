# [?] fix[stdlib]: fix panic in `abi_encode` (#5154)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2026-07-20
Source: https://github.com/vyperlang/vyper/commit/36b5ad4d9f0134faa7d14e1588de740aff7ff57b
Type: security-commit

## Details
fix[stdlib]: fix panic in `abi_encode` (#5154)

fixes the assumption that the argument of 'ensure_tuple' is always a
literal. this is done by querying the folded value instead of the node
itself. the xfail tests are added to document an issue surrounding
constant folding 'empty', which predates this commit. cleanup: some
comments were converted to docstrings for compiler UX.

## Patch
### tests/functional/syntax/test_abi_decode.py
```diff
@@ -1,7 +1,7 @@
 import pytest
 
 from vyper import compiler
-from vyper.exceptions import TypeMismatch
+from vyper.exceptions import CompilerPanic, TypeMismatch, UnfoldableNode
 
 fail_list = [
     (
@@ -31,13 +31,31 @@ def test_abi_decode_fail(bad_code, exc):
         compiler.compile_code(bad_code)
 
 
-valid_list = ["""
+valid_list = [
+    """
 @external
 def foo(x: Bytes[32]) -> uint256:
     return _abi_decode(x, uint256)
-    """]
+    """,
+    """
+@external
+def foo(x: Bytes[32]) -> uint256:
+    return _abi_decode(x, uint256, unwrap_tuple=(0 < 1))
+    """,
+]
 
 
 @pytest.mark.parametrize("good_code", valid_list)
 def test_abi_decode_success(good_code):
     assert compiler.compile_code(good_code) is not None
+
+
+# UnfoldableNode on legacy, CompilerPanic in venom
+@pytest.mark.xfail(raises=(UnfoldableNode, CompilerPanic))
+def test_abi_decode_unwrap_tuple_foldable_expr():
+    code = """
+@external
+def f(x: Bytes[32]) -> uint256:
+    return abi_decode(x, uint256, unwrap_tuple=empty(bool))
+    """
+    assert compiler.compile_code(code) is not None
```

### tests/functional/syntax/test_abi_encode.py
```diff
@@ -1,7 +1,7 @@
 import pytest
 
 from vyper import compiler
-from vyper.exceptions import InvalidLiteral, TypeMismatch
+from vyper.exceptions import InvalidLiteral, TypeMismatch, UnfoldableNode
 
 fail_list = [
     (
@@ -119,9 +119,24 @@ def foo(x: Bytes[1]) -> Bytes[68]:
 def foo() -> Bytes[224]:
     return _abi_encode(BAR)
     """,
+    """
+@external
+def foo(x: Bytes[1]) -> Bytes[96]:
+    return _abi_encode(x, ensure_tuple=(0 < 1))
+    """,
 ]
 
 
 @pytest.mark.parametrize("good_code", valid_list)
 def test_abi_encode_success(good_code):
     assert compiler.compile_code(good_code) is not None
+
+
+@pytest.mark.xfail(raises=UnfoldableNode)
+def test_abi_encode_ensure_tuple_foldable_expr():
+    code = """
+@external
+def f(x: uint256) -> Bytes[64]:
+    return abi_encode(x, ensure_tuple=empty(bool))
+    """
+    assert compiler.compile_code(code) is not None
```

### vyper/builtins/functions.py
```diff
@@ -109,15 +109,20 @@
 
 
 class FoldedFunctionT(BuiltinFunctionT):
-    # Base class for nodes which should always be folded
+    """
+    Base class for nodes which should always be folded
+    """
 
     _modifiability = Modifiability.CONSTANT
 
 
 class TypenameFoldedFunctionT(FoldedFunctionT):
-    # Base class for builtin functions that:
-    # (1) take a typename as the only argument; and
-    # (2) should always be folded.
+    """
+    Base class for builtin functions that:
+    (1) take a typename as the only argument; and
+    (2) should always be folded.
+    """
+
     _inputs = [("typename", TYPE_T.any())]
 
     def fetch_call_return(self, node):
@@ -2251,11 +2256,14 @@ def infer_kwarg_types(self, node):
 
     def fetch_call_return(self, node):
         self._validate_arg_types(node)
-        ensure_tuple = next(
-            (arg.value.value for arg in node.keywords if arg.arg == "ensure_tuple"), True
-        )
+        kwargs = {kw.arg: kw.value for kw in node.keywords}
+
+        if "ensure_tuple" in kwargs:
+            ensure_tuple = kwargs["ensure_tuple"].get_folded_value().value
+        else:
+            ensure_tuple = True
+
         assert isinstance(ensure_tuple, bool)
-        has_method_id = "method_id" in [arg.arg for arg in node.keywords]
 
         # figure out the output type by converting
         # the types to ABI_Types and calling size_bound API
@@ -2272,7 +2280,7 @@ def fetch_call_return(self, node):
 
         maxlen = arg_abi_t.size_bound()
 
-        if has_method_id:
+        if "method_id" in kwargs:
             # the output includes 4 bytes for the method_id.
             maxlen += 4
 
```
