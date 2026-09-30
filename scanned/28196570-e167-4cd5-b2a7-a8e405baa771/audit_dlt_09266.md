# [?] Merge pull request from GHSA-f5x6-7qgp-jhf3

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2023-07-25
Source: https://github.com/vyperlang/vyper/commit/019a37ab98ff53f04fecfadf602b6cd5ac748f7f
Type: security-commit

## Details
Merge pull request from GHSA-f5x6-7qgp-jhf3

## Patch
### tests/parser/functions/test_ecrecover.py
```diff
@@ -40,3 +40,21 @@ def test_ecrecover_uints2() -> address:
     assert c.test_ecrecover_uints2() == local_account.address
 
     print("Passed ecrecover test")
+
+
+def test_invalid_signature(get_contract):
+    code = """
+dummies: HashMap[address, HashMap[address, uint256]]
+
+@external
+def test_ecrecover(hash: bytes32, v: uint8, r: uint256) -> address:
+    # read from hashmap to put garbage in 0 memory location
+    s: uint256 = self.dummies[msg.sender][msg.sender]
+    return ecrecover(hash, v, r, s)
+    """
+    c = get_contract(code)
+    hash_ = bytes(i for i in range(32))
+    v = 0  # invalid v! ecrecover precompile will not write to output buffer
+    r = 0
+    # note web3.py decoding of 0x000..00 address is None.
+    assert c.test_ecrecover(hash_, v, r) is None
```

### vyper/builtins/functions.py
```diff
@@ -764,29 +764,19 @@ def infer_arg_types(self, node):
 
     @process_inputs
     def build_IR(self, expr, args, kwargs, context):
-        placeholder_node = IRnode.from_list(
-            context.new_internal_variable(BytesT(128)), typ=BytesT(128), location=MEMORY
-        )
+        input_buf = context.new_internal_variable(get_type_for_exact_size(128))
+        output_buf = MemoryPositions.FREE_VAR_SPACE
         return IRnode.from_list(
             [
                 "seq",
-                ["mstore", placeholder_node, args[0]],
-                ["mstore", ["add", placeholder_node, 32], args[1]],
-                ["mstore", ["add", placeholder_node, 64], args[2]],
-                ["mstore", ["add", placeholder_node, 96], args[3]],
-                [
-                    "pop",
-                    [
-                        "staticcall",
-                        ["gas"],
-                        1,
-                        placeholder_node,
-                        128,
-                        MemoryPositions.FREE_VAR_SPACE,
-                        32,
-                    ],
-                ],
-                ["mload", MemoryPositions.FREE_VAR_SPACE],
+                # clear output memory first, ecrecover can return 0 bytes
+                ["mstore", output_buf, 0],
+                ["mstore", input_buf, args[0]],
+                ["mstore", input_buf + 32, args[1]],
+                ["mstore", input_buf + 64, args[2]],
+                ["mstore", input_buf + 96, args[3]],
+                ["staticcall", "gas", 1, input_buf, 128, output_buf, 32],
+                ["mload", output_buf],
             ],
             typ=AddressT(),
         )
```
