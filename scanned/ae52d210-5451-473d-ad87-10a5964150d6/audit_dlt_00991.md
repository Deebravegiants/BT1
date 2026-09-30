# [?] fix[ux]: fix false positive for overflow in type checker (#4385)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2024-12-09
Source: https://github.com/vyperlang/vyper/commit/12ab4919cc4618fcac4f5d24d45a0e7fdbc4a48c
Type: security-commit

## Details
fix[ux]: fix false positive for overflow in type checker (#4385)

this commit fixes a false positive for integer overflow in
the typechecker involving nested pow operations by filtering
`OverflowException` in `_validate_op`. the previous code assumed that
`validate_numeric_op` could throw anything besides `InvalidOperation`,
but for the `Pow` binop, it can throw `OverflowException`.

---------

Co-authored-by: Charles Cooper <cooper.charles.m@gmail.com>

## Patch
### tests/functional/codegen/types/numbers/test_exponents.py
```diff
@@ -173,3 +173,17 @@ def foo(b: int128) -> int128:
     c.foo(max_power)
     with tx_failed():
         c.foo(max_power + 1)
+
+
+valid_list = [
+    """
+@external
+def foo() -> uint256:
+    return (10**18)**2
+    """
+]
+
+
+@pytest.mark.parametrize("good_code", valid_list)
+def test_exponent_success(good_code):
+    assert compile_code(good_code) is not None
```

### vyper/semantics/analysis/utils.py
```diff
@@ -41,7 +41,7 @@ def _validate_op(node, types_list, validation_fn_name):
         try:
             _validate_fn(node)
             ret.append(type_)
-        except InvalidOperation as e:
+        except (InvalidOperation, OverflowException) as e:
             err_list.append(e)
 
     if ret:
```

### vyper/semantics/types/primitives.py
```diff
@@ -173,11 +173,11 @@ def _get_lr():
             if isinstance(left, vy_ast.Int):
                 if left.value >= 2**value_bits:
                     raise OverflowException(
-                        "Base is too large, calculation will always overflow", left
+                        f"Base is too large for {self}, calculation will always overflow", left
                     )
                 elif left.value < -(2**value_bits):
                     raise OverflowException(
-                        "Base is too small, calculation will always underflow", left
+                        f"Base is too small for {self}, calculation will always underflow", left
                     )
             elif isinstance(right, vy_ast.Int):
                 if right.value < 0:
```
