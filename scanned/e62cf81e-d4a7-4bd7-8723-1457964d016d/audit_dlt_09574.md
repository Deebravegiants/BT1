# [?] Fix the overflow issue for a large gas price in rpc call.

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2022-05-23
Source: https://github.com/Conflux-Chain/conflux-rust/commit/c877c5f4fac1fb70be7e38cef79600675bb8a8b2
Type: security-commit

## Details
Fix the overflow issue for a large gas price in rpc call.

## Patch
### core/src/executive/executive.rs
```diff
@@ -1016,7 +1016,9 @@ impl<
     ) -> DbResult<ExecutionOutcome> {
         let is_native_tx = tx.space() == Space::Native;
         let options = TransactOptions::virtual_call();
-        let value_and_fee = tx.value() + tx.gas() * tx.gas_price();
+        let value_and_fee = tx
+            .value()
+            .saturating_add(tx.gas().saturating_mul(*tx.gas_price()));
         // If tx.from is specified (is not zero)
         if !tx.sender().address.is_zero() {
             let balance = self.state.balance(&tx.sender())?;
```

### tests/rpc/test_estimate_and_call.py
```diff
@@ -31,4 +31,26 @@ def test_call(self):
         assert_equal(call_res, "0x")
 
         call_request["from"] = hex_to_b32_address(self.rand_addr())
-        assert_raises_rpc_error(-32015, None, self.node.cfx_call, call_request)
\ No newline at end of file
+        assert_raises_rpc_error(-32015, None, self.node.cfx_call, call_request)
+
+    def test_call_with_large_price(self):
+        to = self.rand_addr()
+        call_request = {
+            "from": hex_to_b32_address(to),
+            "to": hex_to_b32_address(to),
+            "value": hex(100),
+            "gasPrice": hex(2**255),
+            "storageLimit": hex(2**64-1)
+        }
+        assert_raises_rpc_error(-32015, None, self.node.cfx_call, call_request)
+
+    def test_estimate_with_large_price(self):
+        to = self.rand_addr()
+        call_request = {
+            "from": hex_to_b32_address(to),
+            "to": hex_to_b32_address(to),
+            "value": hex(100),
+            "gasPrice": hex(2**255),
+            "storageLimit": hex(2**64-1)
+        }
+        assert_raises_rpc_error(-32015, None, self.node.cfx_estimateGasAndCollateral, call_request)
```
