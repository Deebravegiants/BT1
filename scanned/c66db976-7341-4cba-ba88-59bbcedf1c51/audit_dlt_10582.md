# [?] Merge pull request #385 from DavidKnott/add-uint256-overflow-protection

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2017-10-18
Source: https://github.com/vyperlang/vyper/commit/64c2820e1dacccf7b526857de9c8bc94f43f54b6
Type: security-commit

## Details
Merge pull request #385 from DavidKnott/add-uint256-overflow-protection

Add overflow protection to num256 functions

## Patch
### tests/parser/types/numbers/test_num256.py
```diff
@@ -4,7 +4,7 @@
     get_contract_with_gas_estimation, get_contract, assert_tx_failed
 
 
-def test_num256_code():
+def test_num256_code(assert_tx_failed):
     num256_code = """
 def _num256_add(x: num256, y: num256) -> num256:
     return num256_add(x, y)
@@ -31,16 +31,24 @@ def _num256_le(x: num256, y: num256) -> bool:
     return num256_le(x, y)
     """
 
-    c = get_contract_with_gas_estimation(num256_code)
+    c = get_contract(num256_code)
     x = 126416208461208640982146408124
     y = 7128468721412412459
 
+    t.s = s
     assert c._num256_add(x, y) == x + y
+    assert c._num256_add(0,y) == y
+    assert c._num256_add(y,0) == y
+    assert_tx_failed(t, lambda: c._num256_add(2**255, 2**255))
     assert c._num256_sub(x, y) == x - y
-    assert c._num256_sub(y, x) == 2**256 + y - x
+    assert_tx_failed(t, lambda: c._num256_sub(y, x))
+    assert c._num256_sub(0, 0) == 0
     assert c._num256_mul(x, y) == x * y
-    assert c._num256_mul(2**128, 2**128) == 0
+    assert_tx_failed(t, lambda: c._num256_mul(2**255, 2))
+    assert c._num256_mul(2**255, 0) == 0
+    assert c._num256_mul(0, 2**255) == 0
     assert c._num256_div(x, y) == x // y
+    assert_tx_failed(t, lambda: c._num256_div(2**255, 0))
     assert c._num256_div(y, x) == 0
     assert c._num256_gt(x, y) is True
     assert c._num256_ge(x, y) is True
@@ -54,15 +62,47 @@ def _num256_le(x: num256, y: num256) -> bool:
 
     print("Passed num256 operation tests")
 
-def test_num256_with_exponents():
+
+def test_num256_mod(assert_tx_failed):
+    num256_code = """
+def _num256_mod(x: num256, y: num256) -> num256:
+    return num256_mod(x, y)
+
+def _num256_addmod(x: num256, y: num256, z: num256) -> num256:
+    return num256_addmod(x, y, z)
+
+def _num256_mulmod(x: num256, y: num256, z: num256) -> num256:
+    return num256_mulmod(x, y, z)
+    """
+
+    c = get_contract(num256_code)
+    t.s = s
+
+    assert c._num256_mod(3, 2) == 1
+    assert c._num256_mod(34, 32) == 2
+    assert c._num256_addmod(1, 2, 2) == 1
+    assert c._num256_addmod(32, 2, 32) == 2
+    assert c._num256_addmod((2**256) - 1, 0, 2) == 1
+    assert_tx_failed(t, lambda: c._num256_addmod((2**256) - 1, 1, 1))
+    assert c._num256_mulmod(3, 1, 2) == 1
+    assert c._num256_mulmod(200, 3, 601) == 600
+    assert c._num256_mulmod(2**255, 1, 3) == 2
+    assert_tx_failed(t, lambda: c._num256_mulmod(2**255, 2, 1))
+
+
+def test_num256_with_exponents(assert_tx_failed):
     exp_code = """
 def _num256_exp(x: num256, y: num256) -> num256:
         return num256_exp(x,y)
     """
 
     c = get_contract(exp_code)
+    t.s = s
+
+    assert c._num256_exp(2, 0) == 1
+    assert c._num256_exp(2, 1) == 2
     assert c._num256_exp(2, 3) == 8
-    assert c._num256_exp(2**128, 2) == 0
+    assert_tx_failed(t, lambda: c._num256_exp(2**128, 2))
     assert c._num256_exp(2**64, 2) == 2**128
     assert c._num256_exp(7**23, 3) == 7**69
 
```

### viper/functions.py
```diff
@@ -652,27 +652,43 @@ def bitwise_xor(expr, args, kwargs, context):
 
 @signature('num256', 'num256')
 def num256_add(expr, args, kwargs, context):
-    return LLLnode.from_list(['add', args[0], args[1]], typ=BaseType('num256'), pos=getpos(expr))
+    return LLLnode.from_list(['seq',
+                                # Checks that: a + b > a
+                                ['assert', ['or', ['iszero', args[1]], ['gt', ['add', args[0], args[1]], args[0]]]],
+                                ['add', args[0], args[1]]], typ=BaseType('num256'), pos=getpos(expr))
 
 
 @signature('num256', 'num256')
 def num256_sub(expr, args, kwargs, context):
-    return LLLnode.from_list(['sub', args[0], args[1]], typ=BaseType('num256'), pos=getpos(expr))
+    return LLLnode.from_list(['seq',
+                                # Checks that: a >= b
+                                ['assert', ['or', ['iszero', args[1]], ['sge', args[0], args[1]]]],
+                                ['sub', args[0], args[1]]], typ=BaseType('num256'), pos=getpos(expr))
 
 
 @signature('num256', 'num256')
 def num256_mul(expr, args, kwargs, context):
-    return LLLnode.from_list(['mul', args[0], args[1]], typ=BaseType('num256'), pos=getpos(expr))
+    return LLLnode.from_list(['seq',
+                                # Checks that: a == 0 || a / b == b
+                                ['assert', ['or', ['iszero', args[0]],
+                                ['eq', ['div', ['mul', args[0], args[1]], args[0]], args[1]]]],
+                                ['mul', args[0], args[1]]], typ=BaseType('num256'), pos=getpos(expr))
 
 
 @signature('num256', 'num256')
 def num256_div(expr, args, kwargs, context):
-    return LLLnode.from_list(['div', args[0], args[1]], typ=BaseType('num256'), pos=getpos(expr))
+    return LLLnode.from_list(['seq',
+                                # Checks that:  b != 0
+                                ['assert', args[1]],
+                                ['div', args[0], args[1]]], typ=BaseType('num256'), pos=getpos(expr))
 
 
 @signature('num256', 'num256')
 def num256_exp(expr, args, kwargs, context):
-    return LLLnode.from_list(['exp', args[0], args[1]], typ=BaseType('num256'), pos=getpos(expr))
+    return LLLnode.from_list(['seq',
+                                ['assert', ['or', ['or', ['eq', args[1], 1], ['iszero', args[1]]],
+                                ['lt', args[0], ['exp', args[0], args[1]]]]],
+                                ['exp', args[0], args[1]]], typ=BaseType('num256'), pos=getpos(expr))
 
 
 @signature('num256', 'num256')
@@ -682,12 +698,17 @@ def num256_mod(expr, args, kwargs, context):
 
 @signature('num256', 'num256', 'num256')
 def num256_addmod(expr, args, kwargs, context):
-    return LLLnode.from_list(['addmod', args[0], args[1], args[2]], typ=BaseType('num256'), pos=getpos(expr))
+    return LLLnode.from_list(['seq',
+                                ['assert', ['or', ['iszero', args[1]], ['gt', ['add', args[0], args[1]], args[0]]]],
+                                ['addmod', args[0], args[1], args[2]]], typ=BaseType('num256'), pos=getpos(expr))
 
 
 @signature('num256', 'num256', 'num256')
 def num256_mulmod(expr, args, kwargs, context):
-    return LLLnode.from_list(['mulmod', args[0], args[1], args[2]], typ=BaseType('num256'), pos=getpos(expr))
+    return LLLnode.from_list(['seq',
+                                ['assert', ['or', ['iszero', args[0]],
+                                ['eq', ['div', ['mul', args[0], args[1]], args[0]], args[1]]]],
+                                ['mulmod', args[0], args[1], args[2]]], typ=BaseType('num256'), pos=getpos(expr))
 
 
 @signature('num256')
```
