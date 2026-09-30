# [?] fix[ux]: fix panic in pow folding (#4996)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2026-05-22
Source: https://github.com/vyperlang/vyper/commit/66202171e038637e95bc550b8e36ae21054fa5f1
Type: security-commit

## Details
fix[ux]: fix panic in pow folding (#4996)

The constant-fold path for `**` in `Pow._op` calls
`math.log(decimal.Decimal(left))` to estimate whether `l**r` would
overflow `2**256` and result in a compiler hang or crash. The estimate
is only defined for `left > 1`; for any negative base it raises
`ValueError`, denying valid in-range expressions such as
`(-2) ** 2 == 4` and `(-1) ** 100 == 1`. The same math.log call also
crashes on `0 ** 0` and `1 ** N`.

Guard the heuristic with `left > 1` so degenerate bases skip the
estimate and fall through to the exact `int(left**right)` fold, which
already handles them correctly.

## Patch
### tests/unit/ast/nodes/test_fold_binop_int.py
```diff
@@ -131,3 +131,32 @@ def foo({input_value}) -> int128:
     else:
         with tx_failed():
             contract.foo(*values)
+
+
+@pytest.mark.parametrize(
+    "expr,expected",
+    [
+        ("(-2) ** 2", 4),
+        ("(-2) ** 3", -8),
+        ("(-1) ** 100", 1),
+        ("(-1) ** 101", -1),
+        ("0 ** 0", 1),
+        ("1 ** 99", 1),
+    ],
+)
+def test_binop_pow_degenerate_base(expr, expected):
+    # Negative bases (and 0/1 bases) used to trip the log-based overflow
+    # heuristic in Pow._op, which called math.log on Decimal(left).
+    vyper_ast = parse_and_fold(expr)
+    folded = vyper_ast.body[0].value.get_folded_value()
+    assert folded.value == expected
+
+
+@pytest.mark.parametrize("expr", ["(-2) ** 1000", "(-3) ** 500"])
+def test_binop_pow_negative_base_overflow(expr):
+    # Bases with magnitude > 1 must still be caught by the log-based bound.
+    from vyper.exceptions import InvalidLiteral
+
+    with pytest.raises(InvalidLiteral):
+        vyper_ast = parse_and_fold(expr)
+        vyper_ast.body[0].value.get_folded_value()
```

### vyper/ast/nodes.py
```diff
@@ -1133,10 +1133,16 @@ def _op(self, left, right):
         # stage since we are just trying to filter out inputs which can cause
         # the compiler to hang. the others will get caught during constant
         # folding or codegen.
+        # |left| <= 1 can never overflow (result magnitude stays <= 1), so
+        # fast-path it before the log-based heuristic. math.log is undefined
+        # for left <= 0 and zero for left == 1, so the log check below would
+        # also be ill-defined for those cases.
+        if abs(left) <= 1:
+            return int(left**right)
         # l**r > 2**256
         # r * ln(l) > ln(2 ** 256)
         # r > ln(2 ** 256) / ln(l)
-        if right > math.log(decimal.Decimal(2**257)) / math.log(decimal.Decimal(left)):
+        if right > math.log(decimal.Decimal(2**257)) / math.log(decimal.Decimal(abs(left))):
             raise InvalidLiteral("Out of bounds", self)
 
         return int(left**right)
```
