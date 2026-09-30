# [?] fix[codegen]: panic on potential subscript eval order issue (#4159)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2024-06-19
Source: https://github.com/vyperlang/vyper/commit/4594f8badf13a583875f8891698cd3bbefb1c787
Type: security-commit

## Details
fix[codegen]: panic on potential subscript eval order issue (#4159)

subscript expressions have an evaluation order issue when
evaluation of the index (i.e. `node.index`) modifies the parent
(i.e. `node.value`). because the evaluation of the parent is
interleaved with evaluation of the index, it can result in "invalid"
reads where the length check occurs before evaluation of the index, but
the data read occurs afterwards. if evaluation of the index results in
modification of the container size for instance, the data read from the
container can happen on a dangling reference.

another variant of this issue would be accessing
`self.nested_array.pop().append(...)`; however, this currently happens
to be blocked by a panic in the frontend.

this commit conservatively blocks compilation if the preconditions for
the interleaved evaluation are detected. POC tests that the appropriate
panics are generated are included as well.

---------

Co-authored-by: trocher <trooocher@proton.me>
Co-authored-by: Hubert Ritzdorf <hubert.ritzdorf@chainsecurity.com>
Co-authored-by: cyberthirst <cyberthirst.eth@gmail.com>

## Patch
### tests/functional/codegen/types/test_array_indexing.py
```diff
@@ -1,5 +1,9 @@
 # TODO: rewrite the tests in type-centric way, parametrize array and indices types
 
+import pytest
+
+from vyper.exceptions import CompilerPanic
+
 
 def test_negative_ix_access(get_contract, tx_failed):
     # Arrays can't be accessed with negative indices
@@ -130,3 +134,76 @@ def foo():
     c.foo()
     for i in range(10):
         assert c.arr(i) == i
+
+
+# to fix in future release
+@pytest.mark.xfail(raises=CompilerPanic, reason="risky overlap")
+def test_array_index_overlap(get_contract):
+    code = """
+a: public(DynArray[DynArray[Bytes[96], 5], 5])
+
+@external
+def foo() -> Bytes[96]:
+    self.a.append([b'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'])
+    return self.a[0][self.bar()]
+
+
+@internal
+def bar() -> uint256:
+    self.a[0] = [b'yyy']
+    self.a.pop()
+    return 0
+    """
+    c = get_contract(code)
+    # tricky to get this right, for now we just panic instead of generating code
+    assert c.foo() == b"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
+
+
+# to fix in future release
+@pytest.mark.xfail(raises=CompilerPanic, reason="risky overlap")
+def test_array_index_overlap_extcall(get_contract):
+    code = """
+
+interface Bar:
+    def bar() -> uint256: payable
+
+a: public(DynArray[DynArray[Bytes[96], 5], 5])
+
+@external
+def foo() -> Bytes[96]:
+    self.a.append([b'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'])
+    return self.a[0][extcall Bar(self).bar()]
+
+
+@external
+def bar() -> uint256:
+    self.a[0] = [b'yyy']
+    self.a.pop()
+    return 0
+    """
+    c = get_contract(code)
+    assert c.foo() == b"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
+
+
+# to fix in future release
+@pytest.mark.xfail(raises=CompilerPanic, reason="risky overlap")
+def test_array_index_overlap_extcall2(get_contract):
+    code = """
+interface B:
+    def calculate_index() -> uint256: nonpayable
+
+a: HashMap[uint256, DynArray[uint256, 5]]
+
+@external
+def bar() -> uint256:
+    self.a[0] = [2]
+    return self.a[0][extcall B(self).calculate_index()]
+
+@external
+def calculate_index() -> uint256:
+    self.a[0] = [1]
+    return 0
+    """
+    c = get_contract(code)
+
+    assert c.bar() == 1
```

### tests/functional/codegen/types/test_dynamic_array.py
```diff
@@ -8,6 +8,7 @@
 from vyper.exceptions import (
     ArgumentException,
     ArrayIndexException,
+    CompilerPanic,
     ImmutableViolation,
     OverflowException,
     StackTooDeep,
@@ -1887,3 +1888,18 @@ def boo() -> uint256:
 
     c = get_contract(code)
     assert c.foo() == [1, 2, 3, 4]
+
+
+@pytest.mark.xfail(raises=CompilerPanic)
+def test_dangling_reference(get_contract, tx_failed):
+    code = """
+a: DynArray[DynArray[uint256, 5], 5]
+
+@external
+def foo():
+    self.a = [[1]]
+    self.a.pop().append(2)
+    """
+    c = get_contract(code)
+    with tx_failed():
+        c.foo()
```

### vyper/ast/nodes.pyi
```diff
@@ -23,6 +23,7 @@ class VyperNode:
     end_col_offset: int = ...
     _metadata: dict = ...
     _original_node: Optional[VyperNode] = ...
+    _children: list[VyperNode] = ...
     def __init__(self, parent: Optional[VyperNode] = ..., **kwargs: Any) -> None: ...
     def __hash__(self) -> Any: ...
     def __eq__(self, other: Any) -> Any: ...
```

### vyper/codegen/core.py
```diff
@@ -924,6 +924,26 @@ def potential_overlap(left, right):
     return False
 
 
+# similar to `potential_overlap()`, but compares left's _reads_ vs
+# right's _writes_.
+# TODO: `potential_overlap()` can probably be replaced by this function,
+# but all the cases need to be checked.
+def read_write_overlap(left, right):
+    if not isinstance(left, IRnode) or not isinstance(right, IRnode):
+        return False
+
+    if left.typ._is_prim_word and right.typ._is_prim_word:
+        return False
+
+    if len(left.referenced_variables & right.variable_writes) > 0:
+        return True
+
+    if len(left.referenced_variables) > 0 and right.contains_risky_call:
+        return True
+
+    return False
+
+
 # Create an x=y statement, where the types may be compound
 def make_setter(left, right, hi=None):
     check_assign(left, right)
```

### vyper/codegen/expr.py
```diff
@@ -21,6 +21,7 @@
     make_setter,
     pop_dyn_array,
     potential_overlap,
+    read_write_overlap,
     sar,
     shl,
     shr,
@@ -40,6 +41,7 @@
     UnimplementedException,
     tag_exceptions,
 )
+from vyper.semantics.analysis.utils import get_expr_writes
 from vyper.semantics.types import (
     AddressT,
     BoolT,
@@ -86,6 +88,9 @@ def __init__(self, node, context, is_stmt=False):
             self.ir_node = fn()
             assert isinstance(self.ir_node, IRnode), self.ir_node
 
+        writes = set(access.variable for access in get_expr_writes(self.expr))
+        self.ir_node._writes = writes
+
         self.ir_node.annotation = self.expr.get("node_source_code")
         self.ir_node.ast_source = self.expr
 
@@ -352,6 +357,8 @@ def parse_Subscript(self):
 
         elif is_array_like(sub.typ):
             index = Expr.parse_value_expr(self.expr.slice, self.context)
+            if read_write_overlap(sub, index):
+                raise CompilerPanic("risky overlap")
 
         elif is_tuple_like(sub.typ):
             # should we annotate expr.slice in the frontend with the
```

### vyper/codegen/ir_node.py
```diff
@@ -467,6 +467,18 @@ def referenced_variables(self):
 
         return ret
 
+    @cached_property
+    def variable_writes(self):
+        ret = getattr(self, "_writes", set())
+
+        for arg in self.args:
+            ret |= arg.variable_writes
+
+        if getattr(self, "is_self_call", False):
+            ret |= self.invoked_function_ir.func_ir.variable_writes
+
+        return ret
+
     @cached_property
     def contains_risky_call(self):
         ret = self.value in ("call", "delegatecall", "staticcall", "create", "create2")
```

### vyper/semantics/analysis/utils.py
```diff
@@ -24,7 +24,7 @@
 from vyper.semantics.types.bytestrings import BytesT, StringT
 from vyper.semantics.types.primitives import AddressT, BoolT, BytesM_T, IntegerT
 from vyper.semantics.types.subscriptable import DArrayT, SArrayT, TupleT
-from vyper.utils import checksum_encode, int_to_fourbytes
+from vyper.utils import OrderedSet, checksum_encode, int_to_fourbytes
 
 
 def _validate_op(node, types_list, validation_fn_name):
@@ -681,3 +681,16 @@ def check_modifiability(node: vy_ast.ExprNode, modifiability: Modifiability) ->
 
     info = get_expr_info(node)
     return info.modifiability <= modifiability
+
+
+# TODO: move this into part of regular analysis in `local.py`
+def get_expr_writes(node: vy_ast.VyperNode) -> OrderedSet[VarAccess]:
+    if "writes_r" in node._metadata:
+        return node._metadata["writes_r"]
+    ret: OrderedSet = OrderedSet()
+    if isinstance(node, vy_ast.ExprNode) and node._expr_info is not None:
+        ret = node._expr_info._writes
+    for c in node._children:
+        ret |= get_expr_writes(c)
+    node._metadata["writes_r"] = ret
+    return ret
```
