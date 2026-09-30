# [?] Merge pull request from GHSA-4v9q-cgpw-cf38

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2022-06-06
Source: https://github.com/vyperlang/vyper/commit/6b4d8ff185de071252feaa1c319712b2d6577f8d
Type: security-commit

## Details
Merge pull request from GHSA-4v9q-cgpw-cf38

in external call codegen, when `extcodesize` is called on the target
address, the IR for evaluating the target address can be evaluated
twice. this can result in any side effects (embedded in the evaluation
of the target address) being executed twice.

## Patch
### tests/parser/features/external_contracts/test_external_contract_calls.py
```diff
@@ -2411,3 +2411,44 @@ def bar(foo: Foo):
     # fails due to returndatasize being nonzero but also lt 64
     assert_tx_failed(lambda: c.bar(bad_1.address))
     c.bar(bad_2.address)
+
+
+def test_contract_address_evaluation(get_contract):
+    callee_code = """
+# implements: Foo
+
+interface Counter:
+    def increment_counter(): nonpayable
+
+@external
+def foo():
+    pass
+
+@external
+def bar() -> address:
+    Counter(msg.sender).increment_counter()
+    return self
+    """
+    code = """
+# implements: Counter
+
+interface Foo:
+    def foo(): nonpayable
+    def bar() -> address: nonpayable
+
+counter: uint256
+
+@external
+def increment_counter():
+    self.counter += 1
+
+@external
+def do_stuff(f: Foo) -> uint256:
+    Foo(f.bar()).foo()
+    return self.counter
+    """
+
+    c1 = get_contract(code)
+    c2 = get_contract(callee_code)
+
+    assert c1.do_stuff(c2.address) == 1
```

### vyper/codegen/external_call.py
```diff
@@ -168,15 +168,7 @@ def _extcodesize_check(address):
     return ["assert", ["extcodesize", address]]
 
 
-def ir_for_external_call(call_expr, context):
-    from vyper.codegen.expr import Expr  # TODO rethink this circular import
-
-    contract_address = Expr.parse_value_expr(call_expr.func.value, context)
-    call_kwargs = _parse_kwargs(call_expr, context)
-    args_ir = [Expr(x, context).ir_node for x in call_expr.args]
-
-    assert isinstance(contract_address.typ, InterfaceType)
-
+def _external_call_helper(contract_address, args_ir, call_kwargs, call_expr, context):
     # expr.func._metadata["type"].return_type is more accurate
     # than fn_sig.return_type in the case of JSON interfaces.
     fn_type = call_expr.func._metadata["type"]
@@ -223,3 +215,17 @@ def ir_for_external_call(call_expr, context):
         ret.append(ret_unpacker)
 
     return IRnode.from_list(ret, typ=return_t, location=MEMORY)
+
+
+def ir_for_external_call(call_expr, context):
+    from vyper.codegen.expr import Expr  # TODO rethink this circular import
+
+    contract_address = Expr.parse_value_expr(call_expr.func.value, context)
+    assert isinstance(contract_address.typ, InterfaceType)
+    args_ir = [Expr(x, context).ir_node for x in call_expr.args]
+    call_kwargs = _parse_kwargs(call_expr, context)
+
+    with contract_address.cache_when_complex("external_contract") as (b1, contract_address):
+        return b1.resolve(
+            _external_call_helper(contract_address, args_ir, call_kwargs, call_expr, context)
+        )
```
