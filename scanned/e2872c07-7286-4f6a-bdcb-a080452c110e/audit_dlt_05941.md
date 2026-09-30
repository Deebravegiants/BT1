# [?] fix[codegen]: fix panic for type checking iterator types (#4767)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2025-11-04
Source: https://github.com/vyperlang/vyper/commit/a68eb5736eacb63c98db85682c1d2c123604732b
Type: security-commit

## Details
fix[codegen]: fix panic for type checking iterator types (#4767)

the type of the iterator for an array can be a supertype of the array
elements, however an assert was checking for type equivalence, which
led to panics.

## Patch
### tests/functional/syntax/test_dynamic_array.py
```diff
@@ -52,6 +52,19 @@ def test_block_fail(bad_code, exc):
     """
 bar: DynArray[Bytes[30], 10]
     """,  # dynamic arrays of bytestrings are allowed, but not static arrays
+    """
+@external
+def bar():
+    d: DynArray[uint256, 10] = []
+    i: DynArray[uint256, 30] = d
+    """,  # dynamic arrays can be assigned to others of larger size
+    """
+@external
+def bar():
+    d: DynArray[DynArray[uint256, 10], 10] = [[]]
+    for i: DynArray[uint256, 30] in d:
+        pass
+    """,  # dynamic arrays can be assigned to others of larger size
 ]
 
 
```

### vyper/codegen/stmt.py
```diff
@@ -245,7 +245,7 @@ def _parse_For_list(self):
             iter_list = Expr(self.stmt.iter, self.context).ir_node
 
         target_type = self.stmt.target.target._metadata["type"]
-        assert target_type == iter_list.typ.value_type
+        assert target_type.compare_type(iter_list.typ.value_type)
 
         # user-supplied name for loop variable
         varname = self.stmt.target.target.id
```
