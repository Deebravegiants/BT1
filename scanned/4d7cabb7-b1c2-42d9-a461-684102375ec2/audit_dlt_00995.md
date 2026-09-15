# [?] fix[codegen]: recursive dynarray oob check (#4091)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2024-06-11
Source: https://github.com/vyperlang/vyper/commit/21f7172274e551c721e9e35ab3c9d8322a2455d0
Type: security-commit

## Details
fix[codegen]: recursive dynarray oob check (#4091)

this commit fixes more edge cases in `abi_decode` dynarray
validation. these are bugs which were missed (or regressions) in
1f6b9433fbd524, which itself was a continuation of eb011367cc769.

there are multiple fixes contained in this commit.

- similar conceptual error as in 1f6b9433fbd524. when the
length word is out-of-bounds and its runtime is value is zero,
`make_setter` does not enter recursion and therefore there is
no oob check. an example payload which demonstrates this is in
`test_nested_invalid_dynarray_head()`. the fix is to check the
size of the static section ("embedded static size") before entering
the recursion, rather than child_type.static_size (which could be
zero). essentially, this checks that the end of the static section is
in bounds, rather than the beginning.

- the fallback case in `complex_make_setter` could be referring to a
tuple of dynamic types, which makes the tuple itself dynamic, so there
needs to be an oob check there as well.

- `static_size()` is more appropriate than `min_size()` for abi payload
validation, because you can have "valid" ABI payloads where the runtime
length of the dynamic section is zero, because the heads in the static
section all point back into the static section. this commit replaces
the `static_size()` check with `min_size()` check, everywhere.

- remove `returndatasize` check in external calls, because it gets
checked anyways during `make_setter` oob checks.

- add a comment clarifying that payloads larger than `size_bound()` get
rejected by `abi_decode` but not calldata decoding.

tests for each case, contributed by @trocher

---------

Co-authored-by: trocher <trooocher@proton.me>

### tests/functional/builtins/codegen/test_abi_decode.py
```diff
@@ -1323,3 +1323,101 @@ def run(x: Bytes[2 * 32 + 3 * 32  + 3 * 32 * 4]):
 
     with tx_failed():
         c.run(data)
+
+
+def test_nested_invalid_dynarray_head(get_contract, tx_failed):
+    code = """
+@nonpayable
+@external
+def foo(x:Bytes[320]):
+    if True:
+        a: Bytes[320-32] = b''
+
+        # make the word following the buffer x_mem dirty to make a potential
+        # OOB revert
+        fake_head: uint256 = 32
+    x_mem: Bytes[320] = x
+
+    y: DynArray[DynArray[uint256, 2], 2] = _abi_decode(x_mem,DynArray[DynArray[uint256, 2], 2])
+
+@nonpayable
+@external
+def bar(x:Bytes[320]):
+    x_mem: Bytes[320] = x
+
+    y:DynArray[DynArray[uint256, 2], 2] = _abi_decode(x_mem,DynArray[DynArray[uint256, 2], 2])
+    """
+    c = get_contract(code)
+
+    encoded = (0x20, 0x02)  # head of the dynarray  # len of outer
+    inner = (
+        0x0,  # head1
+        # 0x0,  # head2
+    )
+
+    encoded = _abi_payload_from_tuple(encoded + inner)
+    with tx_failed():
+        c.foo(encoded)  # revert
+    with tx_failed():
+        c.bar(encoded)  # return [[],[]]
+
+
+def test_static_outer_type_invalid_heads(get_contract, tx_failed):
+    code = """
+@nonpayable
+@external
+def foo(x:Bytes[320]):
+    x_mem: Bytes[320] = x
+    y:DynArray[uint256, 2][2] = _abi_decode(x_mem,DynArray[uint256, 2][2])
+
+@nonpayable
+@external
+def bar(x:Bytes[320]):
+    if True:
+        a: Bytes[160] = b''
+        # write stuff here to make the call revert in case decode do
+        # an out of bound access:
+        fake_head: uint256 = 32
+    x_mem: Bytes[320] = x
+    y:DynArray[uint256, 2][2] = _abi_decode(x_mem,DynArray[uint256, 2][2])
+    """
+    c = get_contract(code)
+
+    encoded = (0x20,)  # head of the static array
+    inner = (
+        0x00,  # head of the first dynarray
+        # 0x00,  # head of the second dynarray
+    )
+
+    encoded = _abi_payload_from_tuple(encoded + inner)
+
+    with tx_failed():
+        c.foo(encoded)
+    with tx_failed():
+        c.bar(encoded)
+
+
+def test_abi_decode_max_size(get_contract, tx_failed):
+    # test case where the payload is "too large" than the max size
+    # of abi encoding the type. this can happen when the payload is
+    # "sparse" and has garbage bytes in between the static and dynamic
+    # sections
+    code = """
+@external
+def foo(a:Bytes[1000]):
+    v: DynArray[uint256, 1] = _abi_decode(a,DynArray[uint256, 1])
+    """
+    c = get_contract(code)
+
+    payload = (
+        0xA0,  # head
+        0x00,  # garbage
+        0x00,  # garbage
+        0x00,  # garbage
+        0x00,  # garbage
+        0x01,  # len
+        0x12,  # elem1
+    )
+
+    with tx_failed():
+        c.foo(_abi_payload_from_tuple(payload))
```

### tests/functional/codegen/calling_convention/test_external_contract_calls.py
```diff
@@ -2519,13 +2519,13 @@ def foo(a: DynArray[{typ}, 3], b: String[5]):
     encoded = abi.encode(f"({typ}[],string)", val).hex()
     data = f"0x{sig}{encoded}"
 
-    # Dynamic size is short by 1 byte
-    malformed = data[:264]
+    # Static size is short by 1 byte
+    malformed = data[:136]
     with tx_failed():
         env.message_call(c1.address, data=malformed)
 
-    # Dynamic size is at least minimum (132 bytes * 2 + 2 (for 0x) = 266)
-    valid = data[:266]
+    # Static size is at least minimum ((4 + 64) bytes * 2 + 2 (for 0x) = 138)
+    valid = data[:138]
     env.message_call(c1.address, data=valid)
 
 
```

### vyper/builtins/functions.py
```diff
@@ -2482,7 +2482,7 @@ def build_IR(self, expr, args, kwargs, context):
             wrapped_typ = calculate_type_for_external_return(output_typ)
 
         abi_size_bound = wrapped_typ.abi_type.size_bound()
-        abi_min_size = wrapped_typ.abi_type.min_size()
+        abi_min_size = wrapped_typ.abi_type.static_size()
 
         # Get the size of data
         input_max_len = data.typ.maxlen
@@ -2506,6 +2506,10 @@ def build_IR(self, expr, args, kwargs, context):
 
             ret = ["seq"]
 
+            # NOTE: we could replace these 4 lines with
+            # `[assert [le, abi_min_size, data_len]]`. it depends on
+            # what we consider a "valid" payload.
+            # cf. test_abi_decode_max_size()
             if abi_min_size == abi_size_bound:
                 ret.append(["assert", ["eq", abi_min_size, data_len]])
             else:
```

### vyper/codegen/core.py
```diff
@@ -895,10 +895,7 @@ def _abi_payload_size(ir_node):
         # the amount of size each value occupies in static section
         # (the amount of size it occupies in the dynamic section is handled in
         # make_setter recursion)
-        item_size = ir_node.typ.value_type.abi_type.static_size()
-        if item_size == 0:
-            # manual optimization; the mload cannot currently be optimized out
-            return ["add", OFFSET, 0]
+        item_size = ir_node.typ.value_type.abi_type.embedded_static_size()
         return ["add", OFFSET, ["mul", get_dyn_array_count(ir_node), item_size]]
 
     if isinstance(ir_node.typ, _BytestringT):
@@ -982,7 +979,15 @@ def make_setter(left, right, hi=None):
     # Complex Types
     assert isinstance(left.typ, (SArrayT, TupleT, StructT))
 
-    return _complex_make_setter(left, right, hi=hi)
+    with right.cache_when_complex("c_right") as (b1, right):
+        ret = ["seq"]
+        if hi is not None:
+            item_end = add_ofst(right, right.typ.abi_type.static_size())
+            len_check = ["assert", ["le", item_end, hi]]
+            ret.append(len_check)
+
+        ret.append(_complex_make_setter(left, right, hi=hi))
+        return b1.resolve(IRnode.from_list(ret))
 
 
 # locations with no dedicated copy opcode
```

### vyper/codegen/external_call.py
```diff
@@ -86,9 +86,8 @@ def _unpack_returndata(buf, fn_type, call_kwargs, contract_address, context, exp
 
     abi_return_t = wrapped_return_t.abi_type
 
-    min_return_size = abi_return_t.min_size()
     max_return_size = abi_return_t.size_bound()
-    assert 0 < min_return_size <= max_return_size
+    assert 0 <= max_return_size
 
     ret_ofst = buf
     ret_len = max_return_size
@@ -103,15 +102,6 @@ def _unpack_returndata(buf, fn_type, call_kwargs, contract_address, context, exp
 
     unpacker = ["seq"]
 
-    # revert when returndatasize is not in bounds
-    # (except when return_override is provided.)
-    if not call_kwargs.skip_contract_check:
-        assertion = IRnode.from_list(
-            ["assert", ["ge", "returndatasize", min_return_size]],
-            error_msg="returndatasize too small",
-        )
-        unpacker.append(assertion)
-
     assert isinstance(wrapped_return_t, TupleT)
 
     # unpack strictly
```

### vyper/codegen/function_definitions/external_function.py
```diff
@@ -84,7 +84,7 @@ def handler_for(calldata_kwargs, default_kwargs):
 
         # ensure calldata is at least of minimum length
         args_abi_t = calldata_args_t.abi_type
-        calldata_min_size = args_abi_t.min_size() + 4
+        calldata_min_size = args_abi_t.static_size() + 4
 
         # TODO optimize make_setter by using
         # TupleT(list(arg.typ for arg in calldata_kwargs + default_kwargs))
```
