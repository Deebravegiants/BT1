# [?] fix metric panic when request both espace v1 and v2 rpc

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2025-02-25
Source: https://github.com/Conflux-Chain/conflux-rust/commit/01edc2984e603f2f22ac3225f4687b75dbf04038
Type: security-commit

## Details
fix metric panic when request both espace v1 and v2 rpc

uncomment code

## Patch
### crates/rpc/rpc-middlewares/src/metrics.rs
```diff
@@ -31,7 +31,7 @@ impl<S> Metrics<S> {
         // interceptors for the same RPC API.
         let mut timers = METRICS_INTERCEPTOR_TIMERS.lock();
         if !timers.contains_key(name) {
-            let timer = register_timer_with_group("rpc", name.as_str());
+            let timer = register_timer_with_group("async_rpc", name.as_str());
             timers.insert(name.clone(), timer);
         }
         Ok(())
```

### integration_tests/tests/cross_space/phantom_transaction_test.py
```diff
@@ -260,8 +260,7 @@ def emitEVM(n):
 
         # TODO: check logs bloom, cumulative gas used
 
-        # FIXME: check eth_getTransactionReceipt, this will cause full node panic
-        # assert_equal(receipt, self.nodes[0].eth_getTransactionReceipt(receipt["transactionHash"]))
+        assert_equal(receipt, self.nodes[0].eth_getTransactionReceipt(receipt["transactionHash"]))
 
         for idx2, log in enumerate(receipt["logs"]):
             assert_equal(log["address"], evmContractAddr.lower())
@@ -342,8 +341,7 @@ def emitEVM(n):
 
         # TODO: check logs bloom, cumulative gas used
 
-        # FIXME: check eth_getTransactionReceipt, this will cause full node panic
-        # assert_equal(receipt, self.nodes[0].eth_getTransactionReceipt(receipt["transactionHash"]))
+        assert_equal(receipt, self.nodes[0].eth_getTransactionReceipt(receipt["transactionHash"]))
 
         for idx2, log in enumerate(receipt["logs"]):
             assert_equal(log["address"], evmContractAddr.lower())
```
