# [?] Merge pull request from GHSA-6r8q-pfpv-7cgj

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2023-05-11
Source: https://github.com/vyperlang/vyper/commit/3de1415ee77a9244eb04bdb695e249d3ec9ed868
Type: security-commit

## Details
Merge pull request from GHSA-6r8q-pfpv-7cgj

for loops of the form `for i in range(x, x+N)`, the range of the
iterator is not checked, leading to potential overflow. the following
example demonstrates the potential for overflow:

```
@external
def test() -> uint16:
    x:uint8 = 255
    a:uint8 = 0
    for i in range(x, x+2):
        a = i
    return convert(a,uint16)  # returns 256
```

this commit fixes the issue by adding a range check before entering the
loop body.

## Patch
### tests/parser/features/iteration/test_for_range.py
```diff
@@ -128,6 +128,45 @@ def foo(a: {typ}) -> {typ}:
     assert c.foo(100) == 31337
 
 
+# test that we can get to the upper range of an integer
+@pytest.mark.parametrize("typ", ["uint8", "int128", "uint256"])
+def test_for_range_edge(get_contract, typ):
+    code = f"""
+@external
+def test():
+    found: bool = False
+    x: {typ} = max_value({typ})
+    for i in range(x, x + 1):
+        if i == max_value({typ}):
+            found = True
+
+    assert found
+
+    found = False
+    x = max_value({typ}) - 1
+    for i in range(x, x + 2):
+        if i == max_value({typ}):
+            found = True
+
+    assert found
+    """
+    c = get_contract(code)
+    c.test()
+
+
+@pytest.mark.parametrize("typ", ["uint8", "int128", "uint256"])
+def test_for_range_oob_check(get_contract, assert_tx_failed, typ):
+    code = f"""
+@external
+def test():
+    x: {typ} = max_value({typ})
+    for i in range(x, x+2):
+        pass
+    """
+    c = get_contract(code)
+    assert_tx_failed(lambda: c.test())
+
+
 @pytest.mark.parametrize("typ", ["int128", "uint256"])
 def test_return_inside_nested_repeater(get_contract, typ):
     code = f"""
```

### vyper/codegen/stmt.py
```diff
@@ -10,6 +10,7 @@
     IRnode,
     append_dyn_array,
     check_assign,
+    clamp,
     dummy_node_for_type,
     get_dyn_array_count,
     get_element_ptr,
@@ -264,6 +265,8 @@ def _parse_For_range(self):
             arg1 = self.stmt.iter.args[1]
             rounds = self._get_range_const_value(arg1.right)
             start = Expr.parse_value_expr(arg0, self.context)
+            _, hi = start.typ.int_bounds
+            start = clamp("le", start, hi + 1 - rounds)
 
         r = rounds if isinstance(rounds, int) else rounds.value
         if r < 1:
```
