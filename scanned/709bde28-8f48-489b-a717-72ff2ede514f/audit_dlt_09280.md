# [?] Merge pull request #412 from DavidKnott/add-uint256-overflow-protection

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2017-10-19
Source: https://github.com/vyperlang/vyper/commit/c9f0a0e8ebc2c277d0026be89700a6f789d455fd
Type: security-commit

## Details
Merge pull request #412 from DavidKnott/add-uint256-overflow-protection

Fix sub num256

## Patch
### tests/parser/types/numbers/test_num256.py
```diff
@@ -36,19 +36,23 @@ def _num256_le(x: num256, y: num256) -> bool:
     y = 7128468721412412459
 
     t.s = s
+    NUM256_MAX = 2**256 -1  # Max possible num256 value
     assert c._num256_add(x, y) == x + y
     assert c._num256_add(0,y) == y
     assert c._num256_add(y,0) == y
-    assert_tx_failed(t, lambda: c._num256_add(2**255, 2**255))
+    assert_tx_failed(t, lambda: c._num256_add(NUM256_MAX, NUM256_MAX))
     assert c._num256_sub(x, y) == x - y
     assert_tx_failed(t, lambda: c._num256_sub(y, x))
     assert c._num256_sub(0, 0) == 0
+    assert c._num256_sub(NUM256_MAX, 0) == NUM256_MAX
+    assert_tx_failed(t, lambda: c._num256_sub(1, 2))
+    assert c._num256_sub(NUM256_MAX, 1) == NUM256_MAX - 1
     assert c._num256_mul(x, y) == x * y
-    assert_tx_failed(t, lambda: c._num256_mul(2**255, 2))
-    assert c._num256_mul(2**255, 0) == 0
-    assert c._num256_mul(0, 2**255) == 0
+    assert_tx_failed(t, lambda: c._num256_mul(NUM256_MAX, 2))
+    assert c._num256_mul(NUM256_MAX, 0) == 0
+    assert c._num256_mul(0, NUM256_MAX) == 0
     assert c._num256_div(x, y) == x // y
-    assert_tx_failed(t, lambda: c._num256_div(2**255, 0))
+    assert_tx_failed(t, lambda: c._num256_div(NUM256_MAX, 0))
     assert c._num256_div(y, x) == 0
     assert c._num256_gt(x, y) is True
     assert c._num256_ge(x, y) is True
```

### viper/functions.py
```diff
@@ -662,7 +662,7 @@ def num256_add(expr, args, kwargs, context):
 def num256_sub(expr, args, kwargs, context):
     return LLLnode.from_list(['seq',
                                 # Checks that: a >= b
-                                ['assert', ['or', ['iszero', args[1]], ['sge', args[0], args[1]]]],
+                                ['assert', ['ge', args[0], args[1]]],
                                 ['sub', args[0], args[1]]], typ=BaseType('num256'), pos=getpos(expr))
 
 
```
