# [?] fix[codegen]: overflow check in `slice()` (#3818)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2024-03-21
Source: https://github.com/vyperlang/vyper/commit/f8d4b97ab91ec14ac55911fd0aee5eec7def0fa8
Type: security-commit

## Details
fix[codegen]: overflow check in `slice()` (#3818)

the buffer out-of-bounds check in slice() does not take into account the
possibility for arithmetic overflow. this commit fixes the oob check by
adding an overflow check. it also refactors the slice check into a
helper function, and adds relevant tests.

patches GHSA-9x7f-gwxq-6f2c.
---------

Co-authored-by: cyberthirst <cyberthirst.eth@gmail.com>

## Patch
### tests/functional/builtins/codegen/test_slice.py
```diff
@@ -442,3 +442,66 @@ def test_slice_bytes32_calldata_extended(get_contract, code, result):
         c.bar(3, "0x0001020304050607080910111213141516171819202122232425262728293031", 5).hex()
         == result
     )
+
+
+# test cases crafted based on advisory GHSA-9x7f-gwxq-6f2c
+oob_fail_list = [
+    """
+d: public(Bytes[256])
+
+@external
+def do_slice():
+    x : uint256 = max_value(uint256)
+    self.d = b"\x01\x02\x03\x04\x05\x06"
+    assert len(slice(self.d, 1, x)) == max_value(uint256)
+    """,
+    """
+@external
+def do_slice():
+    x: uint256 = max_value(uint256)
+    # y == 0x3232323232323232323232323232323232323232323232323232323232323232
+    y: uint256 = 22704331223003175573249212746801550559464702875615796870481879217237868556850
+    z: uint96 = 1
+    if True:
+        placeholder : uint256[16] = [y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y]
+    s: String[32] = slice(uint2str(z), 1, x)
+    assert slice(s, 1, 2) == "22"
+    """,
+    """
+x: public(Bytes[64])
+secret: uint256
+
+@deploy
+def __init__():
+    self.x = empty(Bytes[64])
+    self.secret = 42
+
+@external
+def do_slice() -> Bytes[64]:
+    start: uint256 = max_value(uint256) - 63
+    return slice(self.x, start, 64)
+    """,
+    # tests bounds check in adhoc location calldata
+    """
+interface IFace:
+    def choose_value(_x: uint256, _y: uint256, _z: uint256, idx: uint256) -> Bytes[32]: nonpayable
+
+@external
+def choose_value(_x: uint256, _y: uint256, _z: uint256, idx: uint256) -> Bytes[32]:
+    assert idx % 32 == 4
+    return slice(msg.data, idx, 32)
+
+@external
+def do_slice():
+    idx: uint256 = max_value(uint256) - 27
+    ret: uint256 = _abi_decode(extcall IFace(self).choose_value(1, 2, 3, idx), uint256)
+    assert ret == 0
+    """,
+]
+
+
+@pytest.mark.parametrize("bad_code", oob_fail_list)
+def test_slice_buffer_oob_reverts(bad_code, get_contract, tx_failed):
+    c = get_contract(bad_code)
+    with tx_failed():
+        c.do_slice()
```

### vyper/builtins/functions.py
```diff
@@ -229,6 +229,18 @@ def build_IR(self, expr, context):
 ADHOC_SLICE_NODE_MACROS = ["~calldata", "~selfcode", "~extcode"]
 
 
+# make sure we don't overrun the source buffer, checking for overflow:
+# valid inputs satisfy:
+#   `assert !(start+length > src_len || start+length < start`
+def _make_slice_bounds_check(start, length, src_len):
+    with start.cache_when_complex("start") as (b1, start):
+        with add_ofst(start, length).cache_when_complex("end") as (b2, end):
+            arithmetic_overflow = ["lt", end, start]
+            buffer_oob = ["gt", end, src_len]
+            ok = ["iszero", ["or", arithmetic_overflow, buffer_oob]]
+            return b1.resolve(b2.resolve(["assert", ok]))
+
+
 def _build_adhoc_slice_node(sub: IRnode, start: IRnode, length: IRnode, context: Context) -> IRnode:
     assert length.is_literal, "typechecker failed"
     assert isinstance(length.value, int)  # mypy hint
@@ -241,7 +253,7 @@ def _build_adhoc_slice_node(sub: IRnode, start: IRnode, length: IRnode, context:
     if sub.value == "~calldata":
         node = [
             "seq",
-            ["assert", ["le", ["add", start, length], "calldatasize"]],  # runtime bounds check
+            _make_slice_bounds_check(start, length, "calldatasize"),
             ["mstore", np, length],
             ["calldatacopy", np + 32, start, length],
             np,
@@ -251,7 +263,7 @@ def _build_adhoc_slice_node(sub: IRnode, start: IRnode, length: IRnode, context:
     elif sub.value == "~selfcode":
         node = [
             "seq",
-            ["assert", ["le", ["add", start, length], "codesize"]],  # runtime bounds check
+            _make_slice_bounds_check(start, length, "codesize"),
             ["mstore", np, length],
             ["codecopy", np + 32, start, length],
             np,
@@ -266,8 +278,7 @@ def _build_adhoc_slice_node(sub: IRnode, start: IRnode, length: IRnode, context:
             sub.args[0],
             [
                 "seq",
-                # runtime bounds check
-                ["assert", ["le", ["add", start, length], ["extcodesize", "_extcode_address"]]],
+                _make_slice_bounds_check(start, length, ["extcodesize", "_extcode_address"]),
                 ["mstore", np, length],
                 ["extcodecopy", "_extcode_address", np + 32, start, length],
                 np,
@@ -440,8 +451,7 @@ def build_IR(self, expr, args, kwargs, context):
 
             ret = [
                 "seq",
-                # make sure we don't overrun the source buffer
-                ["assert", ["le", ["add", start, length], src_len]],  # bounds check
+                _make_slice_bounds_check(start, length, src_len),
                 do_copy,
                 ["mstore", dst, length],  # set length
                 dst,  # return pointer to dst
```
