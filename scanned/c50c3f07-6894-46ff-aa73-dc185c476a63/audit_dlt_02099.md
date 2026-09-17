# [?] Merge pull request from GHSA-j2x6-9323-fp7h

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2022-04-13
Source: https://github.com/vyperlang/vyper/commit/049dbdc647b2ce838fae7c188e6bb09cf16e470b
Type: security-commit

## Details
Merge pull request from GHSA-j2x6-9323-fp7h

This commit addresses two issues in validating returndata, both related
to the inferred type of the external call return.

First, it addresses an issue with interfaces imported from JSON. The
JSON_ABI encoding type was added in 0.3.0 as part of the calling
convention refactor to mimic the old code's behavior when the signature
of a function had `is_from_json` toggled to True. However, both
implementations were a workaround for the fact that in
FunctionSignatures from JSON with Bytes return types, length is set to 1
as a hack to ensure they always typecheck - almost always resulting in a
runtime revert.

This commit removes the JSON_ABI encoding type, so that dynamic
returndata from an interface defined with .json ABI file cannot result
in a buffer overrun(!). To avoid the issue with always runtime
reverting, codegen uses the uses the inferred ContractFunction type of
the Call.func member (which is both more accurate than the inferred type
of the Call expression, and the return type on the FunctionSignature!)
to calculate the length of the external Bytes array.

Second, this commit addresses an issue with validating call returns in
complex expressions. In the following examples, the type of the call
return is either inferred incorrectly or it takes a path through codegen
which avoids generating runtime clamps:

```
interface Foo:
    def returns_int128() -> int128: view
    def returns_Bytes3() -> Bytes[3]: view

foo: Foo
...
x: uint256 = convert(self.foo.returns_int128(), uint256)
y: Bytes[32] = concat(self.foo.returns_Bytes3(), b"")
```

To address this issue, if the type of returndata needs validation, this
commit decodes the returndata "strictly" into a newly allocated buffer
at the time of the call, to avoid unvalidated data accidentally getting
into the runtime. This does result in extra memory traffic which is a
performance hit, but the performance issue can be addressed at a later
date with a zero-copy buffering scheme (parent Expr allocates the
buffer).

Additional minor fixes and cleanup:
- fix compiler panic in new_type_to_old_type for Tuples
- remove `_should_decode` helper function as it duplicates `needs_clamp`
- minor optimization in returndatasize check - assert ge uses one fewer
  instruction than assert gt.

### tests/parser/functions/test_interfaces.py
```diff
@@ -6,7 +6,7 @@
 from vyper.builtin_interfaces import ERC20, ERC721
 from vyper.cli.utils import extract_file_interface_imports
 from vyper.compiler import compile_code, compile_codes
-from vyper.exceptions import InterfaceViolation, StructureException
+from vyper.exceptions import ArgumentException, InterfaceViolation, StructureException
 
 
 def test_basic_extract_interface():
@@ -308,6 +308,170 @@ def test():
     assert erc20.balanceOf(sender) == 1000
 
 
+# test data returned from external interface gets clamped
+@pytest.mark.parametrize("typ", ("int128", "uint8"))
+def test_external_interface_int_clampers(get_contract, assert_tx_failed, typ):
+    external_contract = f"""
+@external
+def ok() -> {typ}:
+    return 1
+
+@external
+def should_fail() -> int256:
+    return -2**255 # OOB for all int/uint types with less than 256 bits
+    """
+
+    code = f"""
+interface BadContract:
+    def ok() -> {typ}: view
+    def should_fail() -> {typ}: view
+
+foo: BadContract
+
+@external
+def __init__(addr: BadContract):
+    self.foo = addr
+
+
+@external
+def test_ok() -> {typ}:
+    return self.foo.ok()
+
+@external
+def test_fail() -> {typ}:
+    return self.foo.should_fail()
+
+@external
+def test_fail2() -> {typ}:
+    x: {typ} = self.foo.should_fail()
+    return x
+
+@external
+def test_fail3() -> int256:
+    return convert(self.foo.should_fail(), int256)
+    """
+
+    bad_c = get_contract(external_contract)
+    c = get_contract(
+        code,
+        bad_c.address,
+        interface_codes={"BadCode": {"type": "vyper", "code": external_contract}},
+    )
+    assert bad_c.ok() == 1
+    assert bad_c.should_fail() == -(2 ** 255)
+
+    assert c.test_ok() == 1
+    assert_tx_failed(lambda: c.test_fail())
+    assert_tx_failed(lambda: c.test_fail2())
+    assert_tx_failed(lambda: c.test_fail3())
+
+
+# test data returned from external interface gets clamped
+def test_external_interface_bytes_clampers(get_contract, assert_tx_failed):
+    external_contract = """
+@external
+def ok() -> Bytes[2]:
+    return b"12"
+
+@external
+def should_fail() -> Bytes[3]:
+    return b"123"
+    """
+
+    code = """
+interface BadContract:
+    def ok() -> Bytes[2]: view
+    def should_fail() -> Bytes[2]: view
+
+foo: BadContract
+
+@external
+def __init__(addr: BadContract):
+    self.foo = addr
+
+
+@external
+def test_ok() -> Bytes[2]:
+    return self.foo.ok()
+
+@external
+def test_fail() -> Bytes[3]:
+    return self.foo.should_fail()
+    """
+
+    bad_c = get_contract(external_contract)
+    c = get_contract(code, bad_c.address)
+    assert bad_c.ok() == b"12"
+    assert bad_c.should_fail() == b"123"
+
+    assert c.test_ok() == b"12"
+    assert_tx_failed(lambda: c.test_fail())
+
+
+# test data returned from external interface gets clamped
+def test_json_abi_bytes_clampers(get_contract, assert_tx_failed, assert_compile_failed):
+    external_contract = """
+@external
+def returns_Bytes3() -> Bytes[3]:
+    return b"123"
+    """
+
+    should_not_compile = """
+import BadJSONInterface as BadJSONInterface
+@external
+def foo(x: BadJSONInterface) -> Bytes[2]:
+    return slice(x.returns_Bytes3(), 0, 2)
+    """
+
+    code = """
+import BadJSONInterface as BadJSONInterface
+
+foo: BadJSONInterface
+
+@external
+def __init__(addr: BadJSONInterface):
+    self.foo = addr
+
+
+@external
+def test_fail1() -> Bytes[2]:
+    # should compile, but raise runtime exception
+    return self.foo.returns_Bytes3()
+
+@external
+def test_fail2() -> Bytes[2]:
+    # should compile, but raise runtime exception
+    x: Bytes[2] = self.foo.returns_Bytes3()
+    return x
+
+@external
+def test_fail3() -> Bytes[3]:
+    # should revert - returns_Bytes3 is inferred to have return type Bytes[2]
+    # (because test_fail3 comes after test_fail1)
+    return self.foo.returns_Bytes3()
+
+    """
+
+    bad_c = get_contract(external_contract)
+    bad_c_interface = {
+        "BadJSONInterface": {
+            "type": "json",
+            "code": compile_code(external_contract, ["abi"])["abi"],
+        }
+    }
+
+    assert_compile_failed(
+        lambda: get_contract(should_not_compile, interface_codes=bad_c_interface), ArgumentException
+    )
+
+    c = get_contract(code, bad_c.address, interface_codes=bad_c_interface)
+    assert bad_c.returns_Bytes3() == b"123"
+
+    assert_tx_failed(lambda: c.test_fail1())
+    assert_tx_failed(lambda: c.test_fail2())
+    assert_tx_failed(lambda: c.test_fail3())
+
+
 def test_units_interface(w3, get_contract):
     code = """
 import balanceof as BalanceOf
```

### vyper/codegen/core.py
```diff
@@ -123,10 +123,7 @@ def _dynarray_make_setter(dst, src):
 
         # for ABI-encoded dynamic data, we must loop to unpack, since
         # the layout does not match our memory layout
-        should_loop = (
-            src.encoding in (Encoding.ABI, Encoding.JSON_ABI)
-            and src.typ.subtype.abi_type.is_dynamic()
-        )
+        should_loop = src.encoding == Encoding.ABI and src.typ.subtype.abi_type.is_dynamic()
 
         # if the subtype is dynamic, there might be a lot of
         # unused space inside of each element. for instance
@@ -379,7 +376,7 @@ def _get_element_ptr_tuplelike(parent, key):
 
     ofst = 0  # offset from parent start
 
-    if parent.encoding in (Encoding.ABI, Encoding.JSON_ABI):
+    if parent.encoding == Encoding.ABI:
         if parent.location == STORAGE:
             raise CompilerPanic("storage variables should not be abi encoded")  # pragma: notest
 
@@ -449,7 +446,7 @@ def _get_element_ptr_array(parent, key, array_bounds_check):
         # NOTE: there are optimization rules for this when ix or bound is literal
         ix = IRnode.from_list([clamp_op, ix, bound], typ=ix.typ)
 
-    if parent.encoding in (Encoding.ABI, Encoding.JSON_ABI):
+    if parent.encoding == Encoding.ABI:
         if parent.location == STORAGE:
             raise CompilerPanic("storage variables should not be abi encoded")  # pragma: notest
 
@@ -703,20 +700,20 @@ def _freshname(name):
 # returns True if t is ABI encoded and is a type that needs any kind of
 # validation
 def needs_clamp(t, encoding):
-    if encoding not in (Encoding.ABI, Encoding.JSON_ABI):
+    if encoding == Encoding.VYPER:
         return False
+    if encoding != Encoding.ABI:
+        raise CompilerPanic("unreachable")  # pragma: notest
     if isinstance(t, (ByteArrayLike, DArrayType)):
-        if encoding == Encoding.JSON_ABI:
-            # don't have bytestring size bound from json, don't clamp
-            return False
-        return True
-    if isinstance(t, BaseType) and t.typ not in ("int256", "uint256", "bytes32"):
         return True
+    if isinstance(t, BaseType):
+        return t.typ not in ("int256", "uint256", "bytes32")
     if isinstance(t, SArrayType):
         return needs_clamp(t.subtype, encoding)
     if isinstance(t, TupleLike):
         return any(needs_clamp(m, encoding) for m in t.tuple_members())
-    return False
+
+    raise CompilerPanic("unreachable")  # pragma: notest
 
 
 # Create an x=y statement, where the types may be compound
```

### vyper/codegen/external_call.py
```diff
@@ -6,10 +6,12 @@
     check_assign,
     check_external_call,
     dummy_node_for_type,
-    get_element_ptr,
+    make_setter,
+    needs_clamp,
 )
 from vyper.codegen.ir_node import Encoding, IRnode
 from vyper.codegen.types import InterfaceType, TupleType, get_type_for_exact_size
+from vyper.codegen.types.convert import new_type_to_old_type
 from vyper.exceptions import StateAccessViolation, TypeCheckFailure
 
 
@@ -59,22 +61,19 @@ def _pack_arguments(contract_sig, args, context):
     return buf, mstore_method_id + [encode_args], args_ofst, args_len
 
 
-def _returndata_encoding(contract_sig):
-    if contract_sig.is_from_json:
-        return Encoding.JSON_ABI
-    return Encoding.ABI
+def _unpack_returndata(buf, contract_sig, skip_contract_check, context, expr):
+    # expr.func._metadata["type"].return_type is more accurate
+    # than contract_sig.return_type in the case of JSON interfaces.
+    ast_return_t = expr.func._metadata["type"].return_type
 
-
-def _unpack_returndata(buf, contract_sig, skip_contract_check, context):
-    return_t = contract_sig.return_type
-    if return_t is None:
+    if ast_return_t is None:
         return ["pass"], 0, 0
 
+    # sanity check
+    return_t = new_type_to_old_type(ast_return_t)
+    check_assign(dummy_node_for_type(return_t), dummy_node_for_type(contract_sig.return_type))
+
     return_t = calculate_type_for_external_return(return_t)
-    # if the abi signature has a different type than
-    # the vyper type, we need to wrap and unwrap the type
-    # so that the ABI decoding works correctly
-    should_unwrap_abi_tuple = return_t != contract_sig.return_type
 
     abi_return_t = return_t.abi_type
 
@@ -88,25 +87,30 @@ def _unpack_returndata(buf, contract_sig, skip_contract_check, context):
     # revert when returndatasize is not in bounds
     ret = []
     # runtime: min_return_size <= returndatasize
-    # TODO move the -1 optimization to IR optimizer
     if not skip_contract_check:
-        ret += [["assert", ["gt", "returndatasize", min_return_size - 1]]]
+        ret += [["assert", ["ge", "returndatasize", min_return_size]]]
 
-    # add as the last IRnode a pointer to the return data structure
+    encoding = Encoding.ABI
 
-    # the return type has been wrapped by the calling contract;
-    # unwrap it so downstream code isn't confused.
-    # basically this expands to buf+32 if the return type has been wrapped
-    # in a tuple AND its ABI type is dynamic.
-    # in most cases, this simply will evaluate to ret.
-    # in the special case where the return type has been wrapped
-    # in a tuple AND its ABI type is dynamic, it expands to buf+32.
-    buf = IRnode(buf, typ=return_t, encoding=_returndata_encoding(contract_sig), location=MEMORY)
+    buf = IRnode.from_list(
+        buf,
+        typ=return_t,
+        location=MEMORY,
+        encoding=encoding,
+        annotation=f"{expr.node_source_code} returndata buffer",
+    )
 
-    if should_unwrap_abi_tuple:
-        buf = get_element_ptr(buf, 0, array_bounds_check=False)
+    assert isinstance(return_t, TupleType)
+    # unpack strictly
+    if needs_clamp(return_t, encoding):
+        buf2 = IRnode.from_list(
+            context.new_internal_variable(return_t), typ=return_t, location=MEMORY
+        )
 
-    ret += [buf]
+        ret.append(make_setter(buf2, buf))
+        ret.append(buf2)
+    else:
+        ret.append(buf)
 
     return ret, ret_ofst, ret_len
 
@@ -145,7 +149,7 @@ def _external_call_helper(
     buf, arg_packer, args_ofst, args_len = _pack_arguments(contract_sig, args_ir, context)
 
     ret_unpacker, ret_ofst, ret_len = _unpack_returndata(
-        buf, contract_sig, skip_contract_check, context
+        buf, contract_sig, skip_contract_check, context, expr
     )
 
     sub += arg_packer
@@ -169,15 +173,7 @@ def _external_call_helper(
     if contract_sig.return_type is not None:
         sub += ret_unpacker
 
-    ret = IRnode.from_list(
-        sub,
-        typ=contract_sig.return_type,
-        location=MEMORY,
-        # set the encoding to ABI here, downstream code will decode and add clampers.
-        encoding=_returndata_encoding(contract_sig),
-    )
-
-    return ret
+    return IRnode.from_list(sub, typ=contract_sig.return_type, location=MEMORY)
 
 
 def _get_special_kwargs(stmt_expr, context):
```

### vyper/codegen/function_definitions/external_function.py
```diff
@@ -3,36 +3,14 @@
 import vyper.utils as util
 from vyper.address_space import CALLDATA, DATA, MEMORY
 from vyper.ast.signatures.function_signature import FunctionSignature, VariableRecord
+from vyper.codegen.abi_encoder import abi_encoding_matches_vyper
 from vyper.codegen.context import Context
-from vyper.codegen.core import get_element_ptr, getpos, make_setter
+from vyper.codegen.core import get_element_ptr, getpos, make_setter, needs_clamp
 from vyper.codegen.expr import Expr
 from vyper.codegen.function_definitions.utils import get_nonreentrant_lock
 from vyper.codegen.ir_node import Encoding, IRnode
 from vyper.codegen.stmt import parse_body
-from vyper.codegen.types.types import (
-    BaseType,
-    ByteArrayLike,
-    DArrayType,
-    SArrayType,
-    TupleLike,
-    TupleType,
-)
-from vyper.exceptions import CompilerPanic
-
-
-def _should_decode(typ):
-    # either a basetype which needs to be clamped
-    # or a complex type which contains something that
-    # needs to be clamped.
-    if isinstance(typ, BaseType):
-        return typ.typ not in ("int256", "uint256", "bytes32")
-    if isinstance(typ, (ByteArrayLike, DArrayType)):
-        return True
-    if isinstance(typ, SArrayType):
-        return _should_decode(typ.subtype)
-    if isinstance(typ, TupleLike):
-        return any(_should_decode(t) for t in typ.tuple_members())
-    raise CompilerPanic(f"_should_decode({typ})")  # pragma: notest
+from vyper.codegen.types.types import TupleType
 
 
 # register function args with the local calling context.
@@ -53,7 +31,7 @@ def _register_function_args(context: Context, sig: FunctionSignature) -> List[IR
 
         arg_ir = get_element_ptr(base_args_ofst, i)
 
-        if _should_decode(arg.typ):
+        if needs_clamp(arg.typ, Encoding.ABI):
             # allocate a memory slot for it and copy
             p = context.new_variable(arg.name, arg.typ, is_mutable=False)
             dst = IRnode(p, typ=arg.typ, location=MEMORY)
@@ -62,6 +40,7 @@ def _register_function_args(context: Context, sig: FunctionSignature) -> List[IR
             copy_arg.source_pos = getpos(arg.ast_source)
             ret.append(copy_arg)
         else:
+            assert abi_encoding_matches_vyper(arg.typ)
             # leave it in place
             context.vars[arg.name] = VariableRecord(
                 name=arg.name,
```

### vyper/codegen/ir_node.py
```diff
@@ -47,8 +47,6 @@ class Encoding(Enum):
     VYPER = auto()
     # abi encoded, default for args/return values from external funcs
     ABI = auto()
-    # abi encoded, same as ABI but no clamps for bytestrings
-    JSON_ABI = auto()
     # future: packed
 
 
```

### vyper/codegen/types/convert.py
```diff
@@ -32,7 +32,7 @@ def new_type_to_old_type(typ: new.BasePrimitive) -> old.NodeType:
     if isinstance(typ, new.DynamicArrayDefinition):
         return old.DArrayType(new_type_to_old_type(typ.value_type), typ.length)
     if isinstance(typ, new.TupleDefinition):
-        return old.TupleType(typ.value_type)
+        return old.TupleType([new_type_to_old_type(t) for t in typ.value_type])
     if isinstance(typ, new.StructDefinition):
         return old.StructType(
             {n: new_type_to_old_type(t) for (n, t) in typ.members.items()}, typ._id
```
