# [?] fix[builtins]: fix panic in `shift()` negative value folds (#5109)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2026-08-25
Source: https://github.com/vyperlang/vyper/commit/f6c7838df8d63dc1acdddb2f5bc438858d9934c0
Type: security-commit

## Details
fix[builtins]: fix panic in `shift()` negative value folds (#5109)

folding `shift()` with a negative first argument computed the left
shift modulo 2**256, producing an unsigned constant which is out of
bounds for the signed output type. `shift(-1, 1)` failed to compile
with "Expected int256 but literal can only be cast as uint256" while
the same expression with a runtime operand compiles and returns -2.

leave negative left shifts unfolded so they go through runtime
codegen, which handles signed values correctly.

---------

Co-authored-by: Charles Cooper <cooper.charles.m@gmail.com>

## Patch
### .github/workflows/pull-request.yaml
```diff
@@ -48,6 +48,7 @@ jobs:
             test
             lang
             stdlib
+            builtins
             ux
             parser
             tool
```

### tests/functional/builtins/codegen/test_bitwise.py
```diff
@@ -4,7 +4,7 @@
 
 from vyper.compiler import compile_code
 from vyper.exceptions import InvalidLiteral, InvalidOperation, TypeMismatch, UnimplementedException
-from vyper.utils import unsigned_to_signed
+from vyper.utils import SizeLimits, unsigned_to_signed
 
 
 def get_code_for_type(typ, use_shift=True):
@@ -211,6 +211,47 @@ def _shl(x: int256, y: uint256) -> int256:
             assert c._shl(t, s) == unsigned_to_signed((t << s) % (2**256), 256)
 
 
+def test_shift_builtin_negative_literal(get_contract):
+    # folding the deprecated `shift()` builtin must not turn a negative
+    # value into an unsigned constant, which is out of bounds for the
+    # signed output type
+    code = """
+@external
+def foo() -> int256:
+    return shift(-1, 1)
+
+@external
+def bar() -> int256:
+    return shift(-4, -1)
+    """
+    c = get_contract(code)
+    assert c.foo() == -2
+    assert c.bar() == -2
+
+
+@pytest.mark.parametrize(
+    "value,shift,expected",
+    [
+        (-1, 0, -1),
+        (-1, 1, -2),
+        (-1, 255, SizeLimits.MIN_INT256),
+        (-1, 256, 0),
+        (-2, 255, 0),
+        (-4, -1, -2),
+    ],
+)
+def test_shift_builtin_negative_literal_constant(get_contract, value, shift, expected):
+    code = f"""
+FOO: constant(int256) = shift({value}, {shift})
+
+@external
+def foo() -> int256:
+    return FOO
+    """
+    c = get_contract(code)
+    assert c.foo() == expected
+
+
 def test_precedence(get_contract):
     code = """
 @external
```

### vyper/builtins/functions.py
```diff
@@ -97,6 +97,7 @@
     keccak256,
     method_id,
     method_id_int,
+    wrap256,
 )
 from vyper.warnings import vyper_warn
 
@@ -1345,7 +1346,8 @@ def _try_fold(self, node):
         if shift < 0:
             value = value >> -shift
         else:
-            value = (value << shift) % (2**256)
+            is_signed_shift = value < 0
+            value = wrap256(value << shift, signed=is_signed_shift)
         return vy_ast.Int.from_node(node, value=value)
 
     def fetch_call_return(self, node):
```
