# [?] fix(node/rpc): removed the panic and added error when building RPC actor (op-rs/kona#1709)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2025-05-12
Source: https://github.com/ethereum-optimism/optimism/commit/c6c44f03fb46c79b448c2cf4f9dbbe63ab557cca
Type: security-commit

## Details
fix(node/rpc): removed the panic and added error when building RPC actor (op-rs/kona#1709)

## Patch
### crates/node/service/src/service/standard/error.rs
```diff
@@ -1,6 +1,7 @@
 //! Contains the error type for the [`crate::RollupNode`].
 
 use crate::SyncStartError;
+use jsonrpsee::server::RegisterMethodError;
 use kona_derive::errors::PipelineErrorKind;
 use kona_engine::EngineStateBuilderError;
 use kona_p2p::NetworkBuilderError;
@@ -28,4 +29,7 @@ pub enum RollupNodeError {
     /// An error occured while launching the engine api.
     #[error(transparent)]
     EngineLauncher(#[from] EngineStateBuilderError),
+    /// An error occurred while registering RPC methods.
+    #[error(transparent)]
+    RegisterMethod(#[from] RegisterMethodError),
 }
```

### crates/node/service/src/service/validator.rs
```diff
@@ -61,7 +61,10 @@ pub trait ValidatorNodeService {
     /// The type of derivation pipeline to use for the service.
     type DerivationPipeline: Pipeline + SignalReceiver + Send + Sync + 'static;
     /// The type of error for the service's entrypoint.
-    type Error: From<RpcLauncherError> + From<EngineStateBuilderError> + std::fmt::Debug;
+    type Error: From<RpcLauncherError>
+        + From<EngineStateBuilderError>
+        + From<jsonrpsee::server::RegisterMethodError>
+        + std::fmt::Debug;
 
     /// Returns a reference to the rollup node's [`RollupConfig`].
     fn config(&self) -> &RollupConfig;
@@ -181,10 +184,10 @@ pub trait ValidatorNodeService {
         // The RPC Server should go last to let other actors register their rpc modules.
         let rpc = if let Some(mut rpc) = self.rpc() {
             if let Some(p2p_module) = p2p_module {
-                rpc = rpc.merge(p2p_module.into_rpc()).expect("failed to merge p2p rpc module");
+                rpc = rpc.merge(p2p_module.into_rpc()).map_err(Self::Error::from)?;
             }
 
-            rpc = rpc.merge(rollup_rpc.into_rpc()).expect("failed to merge engine rpc module");
+            rpc = rpc.merge(rollup_rpc.into_rpc()).map_err(Self::Error::from)?;
             let handle = rpc.start().await?;
             Some(RpcActor::new(handle, cancellation.clone()))
         } else {
```
