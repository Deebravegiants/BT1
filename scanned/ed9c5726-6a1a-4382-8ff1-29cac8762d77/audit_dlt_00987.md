# [?] fix[venom]: fix `extract32` overflow and `bytesN` clamping (#4986)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2026-05-21
Source: https://github.com/vyperlang/vyper/commit/037d31678f2f1f56c4bc69bb240bee21c8f6b34e
Type: security-commit

## Details
fix[venom]: fix `extract32` overflow and `bytesN` clamping (#4986)

Venom `extract32` had two validation gaps versus legacy codegen. The
bounds check computed `start + 32` without overflow protection — a near-
max start would wrap around to a small value, bypassing the out-of-
bounds assertion. Reuse `_assert_slice_bounds` (already used by `slice`)
which handles this correctly.

The output clamping was also incomplete: `_clamp_extract32_result` had
ad-hoc logic that didn't canonicalize `bytesN` output (dirty trailing
bytes from the 32-byte load could leak through). Legacy codegen applies
the basetype clamp for all primitive types. Consolidate all output
clamping into `clamp_basetype`, extending it to handle `BytesM_T`,
`AddressT`, `BoolT`, and 256-bit integers alongside the existing
signed/unsigned integer paths.

## Patch
### tests/functional/builtins/codegen/test_extract32.py
```diff
@@ -143,6 +143,34 @@ def foo() -> bytes32:
     assert c.foo() == b"defghijklmnopqrstuvwxyz123456789"
 
 
+def test_extract32_start_overflow_reverts(get_contract, tx_failed):
+    code = """
+@external
+def foo(start: uint256) -> bytes32:
+    x: Bytes[32] = b"abcdefghijklmnopqrstuvwxyz123456"
+    return extract32(x, start, output_type=bytes32)
+    """
+
+    c = get_contract(code)
+
+    with tx_failed():
+        c.foo(2**256 - 1)
+
+
+def test_extract32_bytes_m_clamp(get_contract, tx_failed):
+    code = """
+@external
+def foo(inp: Bytes[32]) -> bytes4:
+    return extract32(inp, 0, output_type=bytes4)
+    """
+
+    c = get_contract(code)
+
+    assert c.foo(b"abcd" + b"\x00" * 28) == b"abcd"
+    with tx_failed():
+        c.foo(b"abcdX" + b"\x00" * 27)
+
+
 def test_extract32_signed_clamp_regression(get_contract, tx_failed):
     """
     Regression test: extract32 with signed output types must validate bounds.
```

### vyper/codegen_venom/arithmetic.py
```diff
@@ -12,10 +12,12 @@
 from vyper import ast as vy_ast
 from vyper.codegen.arithmetic import calculate_largest_base, calculate_largest_power
 from vyper.exceptions import CompilerPanic, TypeCheckFailure
-from vyper.semantics.types import DecimalT, IntegerT
+from vyper.semantics.types import AddressT, BoolT, BytesM_T, DecimalT, IntegerT
 from vyper.venom.basicblock import IRLiteral, IROperand
 from vyper.venom.builder import VenomBuilder
 
+AnyPrimType = Union[AddressT, BoolT, BytesM_T, DecimalT, IntegerT]  # TODO: move to shared location
+
 
 def safe_add(
     b: VenomBuilder, x: IROperand, y: IROperand, typ: Union[IntegerT, DecimalT]
@@ -235,8 +237,26 @@ def safe_pow(
     return b.exp(x, y)
 
 
-def clamp_basetype(b: VenomBuilder, val: IROperand, typ: Union[IntegerT, DecimalT]) -> IROperand:
+def clamp_basetype(b: VenomBuilder, val: IROperand, typ: AnyPrimType) -> IROperand:
     """Clamp value to type bounds."""
+    if isinstance(typ, BytesM_T):
+        if typ.m < 32:
+            b.assert_(b.iszero(b.shl(IRLiteral(typ.m * 8), val)))
+        return val
+
+    if isinstance(typ, AddressT):
+        ok = b.iszero(b.gt(val, IRLiteral((1 << 160) - 1)))
+        b.assert_(ok)
+        return val
+
+    if isinstance(typ, BoolT):
+        ok = b.iszero(b.gt(val, IRLiteral(1)))
+        b.assert_(ok)
+        return val
+
+    if isinstance(typ, IntegerT) and typ.bits == 256:
+        return val
+
     lo, hi = typ.int_bounds
 
     if typ.is_signed:
```

### vyper/codegen_venom/builtins/bytes.py
```diff
@@ -11,8 +11,9 @@
 from typing import TYPE_CHECKING
 
 from vyper import ast as vy_ast
+from vyper.codegen_venom.arithmetic import clamp_basetype
 from vyper.codegen_venom.value import VyperValue
-from vyper.semantics.types import AddressT, BytesM_T, BytesT, IntegerT, StringT
+from vyper.semantics.types import AddressT, BytesM_T, BytesT, StringT
 from vyper.semantics.types.bytestrings import _BytestringT
 from vyper.venom.basicblock import IRLiteral, IROperand, IRVariable
 
@@ -278,45 +279,15 @@ def lower_extract32(node: vy_ast.Call, ctx: VenomCodegenContext) -> IROperand:
     start = Expr(start_node, ctx).lower_value()
 
     # Bounds check: start + 32 <= length
-    end = b.add(start, IRLiteral(32))
-    oob = b.gt(end, src_len)
-    b.assert_(b.iszero(oob))
+    _assert_slice_bounds(ctx, start, IRLiteral(32), src_len)
 
     # Load 32 bytes at offset
     load_ptr = b.add(src_data, start)
     result = b.mload(load_ptr)
 
     # Apply type-specific clamping if needed
     out_t = node._metadata["type"]
-    return _clamp_extract32_result(result, out_t, ctx)
-
-
-def _clamp_extract32_result(val: IROperand, out_t, ctx: VenomCodegenContext) -> IROperand:
-    """Apply bounds check for extract32 output type."""
-    b = ctx.builder
-
-    if isinstance(out_t, IntegerT):
-        # Need to clamp to type bounds for signed/unsigned integers
-        if out_t.bits < 256:
-            if out_t.is_signed:
-                # For signed types, check signextend(val) == val
-                # This ensures the value's high bits match the sign bit
-                bytes_minus_1 = out_t.bits // 8 - 1
-                canonical = b.signextend(IRLiteral(bytes_minus_1), val)
-                b.assert_(b.eq(val, canonical))
-            else:
-                # For unsigned types, check value fits in type range
-                mask = (1 << out_t.bits) - 1
-                too_big = b.gt(val, IRLiteral(mask))
-                b.assert_(b.iszero(too_big))
-    elif isinstance(out_t, AddressT):
-        # Address is 160 bits, ensure high 96 bits are zero
-        mask = (1 << 160) - 1
-        too_big = b.gt(val, IRLiteral(mask))
-        b.assert_(b.iszero(too_big))
-
-    # bytes32 and bytesM need no clamping
-    return val
+    return clamp_basetype(b, result, out_t)
 
 
 # Export handlers
```
