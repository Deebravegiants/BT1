# [?] Merge pull request #2053 from iamdefinitelyahuman/fix-folding-intermediate-overflow

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2020-06-27
Source: https://github.com/vyperlang/vyper/commit/0946b4e61f4f270bbbbc6d4737a420d1fcd989b3
Type: security-commit

## Details
Merge pull request #2053 from iamdefinitelyahuman/fix-folding-intermediate-overflow

Overflow checks during constant folding

## Patch
### tests/ast/nodes/test_evaluate_binop_decimal.py
```diff
@@ -5,7 +5,11 @@
 from hypothesis import strategies as st
 
 from vyper import ast as vy_ast
-from vyper.exceptions import TypeMismatch, ZeroDivisionException
+from vyper.exceptions import (
+    OverflowException,
+    TypeMismatch,
+    ZeroDivisionException,
+)
 
 st_decimals = st.decimals(
     min_value=-(2 ** 32), max_value=2 ** 32, allow_nan=False, allow_infinity=False, places=10,
@@ -76,8 +80,8 @@ def foo({input_value}) -> decimal:
         vy_ast.folding.replace_literal_ops(vyper_ast)
         expected = vyper_ast.body[0].value.value
         is_valid = -(2 ** 127) <= expected < 2 ** 127
-    except ZeroDivisionException:
-        # for division/modulus by 0, expect the contract call to revert
+    except (OverflowException, ZeroDivisionException):
+        # for overflow or division/modulus by 0, expect the contract call to revert
         is_valid = False
 
     if is_valid:
```

### tests/ast/test_folding.py
```diff
@@ -2,6 +2,7 @@
 
 from vyper import ast as vy_ast
 from vyper.ast import folding
+from vyper.exceptions import OverflowException
 
 
 def test_integration():
@@ -31,6 +32,30 @@ def test_replace_binop_nested():
     assert vy_ast.compare_nodes(test_ast, expected_ast)
 
 
+def test_replace_binop_nested_intermediate_overflow():
+    test_ast = vy_ast.parse_to_ast("2**255 * 2 / 10")
+    with pytest.raises(OverflowException):
+        folding.fold(test_ast)
+
+
+def test_replace_binop_nested_intermediate_underflow():
+    test_ast = vy_ast.parse_to_ast("-2**255 * 2 - 10 + 100")
+    with pytest.raises(OverflowException):
+        folding.fold(test_ast)
+
+
+def test_replace_decimal_nested_intermediate_overflow():
+    test_ast = vy_ast.parse_to_ast("170141183460469231731687303715884105726.0 + 1.1 - 10.0")
+    with pytest.raises(OverflowException):
+        folding.fold(test_ast)
+
+
+def test_replace_decimal_nested_intermediate_underflow():
+    test_ast = vy_ast.parse_to_ast("-170141183460469231731687303715884105726.0 - 2.1 + 10.0")
+    with pytest.raises(OverflowException):
+        folding.fold(test_ast)
+
+
 def test_replace_literal_ops():
     test_ast = vy_ast.parse_to_ast("[not True, True and False, True or False]")
     expected_ast = vy_ast.parse_to_ast("[False, False, True]")
```

### tests/parser/functions/test_convert_to_decimal.py
```diff
@@ -45,7 +45,7 @@ def test_convert_from_uint256_overflow(get_contract_with_gas_estimation, assert_
     code = """
 @public
 def foo() -> decimal:
-    return convert(2**256 - 1, decimal)
+    return convert(2**127, decimal)
     """
 
     assert_compile_failed(lambda: get_contract_with_gas_estimation(code), InvalidLiteral)
```

### tests/parser/functions/test_convert_to_int128.py
```diff
@@ -158,7 +158,7 @@ def test() -> int128:
     code = """
 @public
 def test() -> int128:
-    return convert(2**256 - 1, int128)
+    return convert(2**127, int128)
     """
 
     assert_compile_failed(lambda: get_contract_with_gas_estimation(code), InvalidLiteral)
```

### tests/parser/types/numbers/test_uint256.py
```diff
@@ -183,20 +183,3 @@ def max_ne() -> (bool):
     assert c.max_gte() is False
     assert c.max_gt() is False
     assert c.max_ne() is True
-
-
-def test_uint256_constant_folding(get_contract_with_gas_estimation):
-    code = """
-@public
-def maximum() -> uint256:
-    return 2**256 - 1
-
-
-@public
-def minimum() -> uint256:
-    return 2**256 - 2**256
-    """
-
-    c = get_contract_with_gas_estimation(code)
-    assert c.maximum() == 2 ** 256 - 1
-    assert c.minimum() == 0
```

### vyper/ast/nodes.py
```diff
@@ -169,6 +169,22 @@ def _raise_syntax_exc(error_msg: str, ast_struct: dict) -> None:
     )
 
 
+def _validate_numeric_bounds(
+    node: Union["BinOp", "UnaryOp"], value: Union[decimal.Decimal, int]
+) -> None:
+    if isinstance(value, decimal.Decimal):
+        lower, upper = SizeLimits.MINNUM, SizeLimits.MAXNUM
+    elif isinstance(value, int):
+        lower, upper = SizeLimits.MINNUM, SizeLimits.MAX_UINT256
+    else:
+        raise CompilerPanic(f"Unexpected return type from {node._op}: {type(value)}")
+    if not lower <= value <= upper:
+        raise OverflowException(
+            f"Result of {node.op.description} ({value}) is outside bounds of all numeric types",
+            node,
+        )
+
+
 class VyperNode:
     """
     Base class for all vyper AST nodes.
@@ -777,6 +793,7 @@ def evaluate(self) -> VyperNode:
             raise UnfoldableNode("Node contains invalid field(s) for evaluation")
 
         value = self.op._op(self.operand.value)
+        _validate_numeric_bounds(self, value)
         return type(self.operand).from_node(self, value=value)
 
 
@@ -814,6 +831,7 @@ def evaluate(self) -> VyperNode:
             raise UnfoldableNode("Node contains invalid field(s) for evaluation")
 
         value = self.op._op(left.value, right.value)
+        _validate_numeric_bounds(self, value)
         return type(left).from_node(self, value=value)
 
 
```
