# [?] Fixes #767, overflow checking for multiplication.

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2018-04-16
Source: https://github.com/vyperlang/vyper/commit/0a94db21380e95fab8f242750487b1575eb8e154
Type: security-commit

## Details
Fixes #767, overflow checking for multiplication.

## Patch
### tests/parser/types/numbers/test_decimals.py
```diff
@@ -121,3 +121,21 @@ def iarg() -> wei_value:
     assert c.iarg() == 14
 
     print('Passed fractional multiplication test')
+
+
+def test_mul_overflow(t, assert_tx_failed, get_contract_with_gas_estimation, chain):
+    mul_code = """
+
+@public
+def _num_mul(x: decimal, y: int128) -> decimal:
+    return x * y
+
+    """
+
+    c = get_contract_with_gas_estimation(mul_code)
+
+    t.s = chain
+    NUM_1 = 85070591730234615865843651857942052864.0
+    NUM_2 = 136112946768375385385349842973
+
+    assert_tx_failed(lambda: c._num_mul(NUM_1, NUM_2))
```

### vyper/parser/expr.py
```diff
@@ -242,13 +242,13 @@ def arithmetic(self):
                 o = LLLnode.from_list(['with', 'r', right, ['with', 'l', left,
                                         ['with', 'ans', ['mul', 'l', 'r'],
                                             ['seq',
-                                                ['assert', ['or', ['eq', ['sdiv', 'ans', 'l'], 'r'], ['not', 'l']]],
+                                                ['assert', ['or', ['eq', ['sdiv', 'ans', 'l'], 'r'], ['iszero', 'l']]],
                                                 ['sdiv', 'ans', DECIMAL_DIVISOR]]]]], typ=BaseType('decimal', new_unit), pos=getpos(self.expr))
             elif (ltyp == 'int128' and rtyp == 'decimal') or (ltyp == 'decimal' and rtyp == 'int128'):
                 o = LLLnode.from_list(['with', 'r', right, ['with', 'l', left,
                                         ['with', 'ans', ['mul', 'l', 'r'],
                                             ['seq',
-                                                ['assert', ['or', ['eq', ['sdiv', 'ans', 'l'], 'r'], ['not', 'l']]],
+                                                ['assert', ['or', ['eq', ['sdiv', 'ans', 'l'], 'r'], ['iszero', 'l']]],
                                                 'ans']]]], typ=BaseType('decimal', new_unit), pos=getpos(self.expr))
             else:
                 raise Exception("Unsupported Operation 'mul(%r, %r)'" % (ltyp, rtyp))
```
