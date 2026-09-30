# [?] Merge pull request #4386 from oasisprotocol/kostko/fix/rt-propagate-tx-panics

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2021-12-03
Source: https://github.com/oasisprotocol/oasis-core/commit/c660d0cd69a6b980a69bfc6596c81a1fd2341ef4
Type: security-commit

## Details
Merge pull request #4386 from oasisprotocol/kostko/fix/rt-propagate-tx-panics

runtime: Propagate panics during transaction/local RPC/policy dispatch

## Patch
### .changelog/4386.bugfix.md
```diff
@@ -0,0 +1,5 @@
+runtime: Propagate panics during transaction/local RPC/policy dispatch
+
+A panic during transaction/local RPC/policy dispatch signals a serious
+problem so it should be propagated and the runtime should crash to force
+state reset.
```

### runtime/src/dispatcher.rs
```diff
@@ -684,6 +684,10 @@ impl Dispatcher {
         inputs: TxnBatch,
         state: TxDispatchState,
     ) -> Result<Body, Error> {
+        // Make sure to abort the process on panic during transaction processing as that indicates
+        // a serious problem and should make sure to clean up the process.
+        let _guard = AbortOnPanic;
+
         debug!(self.logger, "Received transaction batch request";
             "state_root" => ?state.header.state_root,
             "round" => state.header.round + 1,
@@ -721,7 +725,8 @@ impl Dispatcher {
                 )
             }
         })
-        .await?
+        .await
+        .unwrap() // Propagate panics during transaction dispatch.
     }
 
     async fn dispatch_rpc(
@@ -841,6 +846,10 @@ impl Dispatcher {
         ctx: Context,
         request: Vec<u8>,
     ) -> Result<Body, Error> {
+        // Make sure to abort the process on panic during local RPC processing as that indicates a
+        // serious problem and should make sure to clean up the process.
+        let _guard = AbortOnPanic;
+
         debug!(self.logger, "Received local RPC call request");
 
         let req: RpcRequest = cbor::from_slice(&request)
@@ -869,7 +878,8 @@ impl Dispatcher {
             let response = cbor::to_vec(response);
             Ok(Body::RuntimeLocalRPCCallResponse { response })
         })
-        .await?
+        .await
+        .unwrap() // Propagate panics during local RPC dispatch.
     }
 
     fn handle_km_policy_update(
@@ -878,6 +888,10 @@ impl Dispatcher {
         _ctx: Context,
         signed_policy_raw: Vec<u8>,
     ) -> Result<Body, Error> {
+        // Make sure to abort the process on panic during policy processing as that indicates a
+        // serious problem and should make sure to clean up the process.
+        let _guard = AbortOnPanic;
+
         debug!(self.logger, "Received km policy update request");
         rpc_dispatcher.handle_km_policy_update(signed_policy_raw);
         debug!(self.logger, "KM policy update request complete");
```
