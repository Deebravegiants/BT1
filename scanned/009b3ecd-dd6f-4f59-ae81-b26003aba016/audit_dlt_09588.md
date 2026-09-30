# [?] Avoid panic during close.

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2021-08-26
Source: https://github.com/Conflux-Chain/conflux-rust/commit/579d9fc725071e37f10de877624cc5946757bfbf
Type: security-commit

## Details
Avoid panic during close.

## Patch
### core/src/pos/protocol/message/block_retrieval.rs
```diff
@@ -46,8 +46,10 @@ impl Request for BlockRetrievalRpcRequest {
     fn notify_error(&mut self, error: Error) {
         let res_tx = self.response_tx.take();
         if let Some(tx) = res_tx {
-            tx.send(Err(error))
-                .expect("send ResponseTX EmptyError should succeed");
+            if let Err(e) = tx.send(Err(error)) {
+                // receiver dropped, we can just drop this error.
+                debug!("send ResponseTX EmptyError: e={:?}", e);
+            }
         }
     }
 
```
