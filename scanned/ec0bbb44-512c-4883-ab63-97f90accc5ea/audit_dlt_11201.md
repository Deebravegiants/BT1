# [?] starknet_os_runner: avoid panic in require bouncer lock (#11763)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/sequencer
Published: 2026-01-20
Source: https://github.com/starkware-libs/sequencer/commit/c421fa2ab62037e733911d8d46974eb74fe5c1f8
Type: security-commit

## Details
starknet_os_runner: avoid panic in require bouncer lock (#11763)

## Patch
### crates/starknet_os_runner/src/errors.rs
```diff
@@ -17,6 +17,8 @@ pub enum VirtualBlockExecutorError {
     TransactionExecutionError(String),
     #[error("Block state unavailable after execution")]
     StateUnavailable,
+    #[error("Failed to acquire bouncer lock: {0}")]
+    BouncerLockError(String),
 }
 
 #[derive(Debug, Error)]
```

### crates/starknet_os_runner/src/virtual_block_executor.rs
```diff
@@ -26,6 +26,7 @@ use starknet_api::core::{ChainId, ClassHash};
 use starknet_api::transaction::fields::Fee;
 use starknet_api::transaction::{InvokeTransaction, Transaction, TransactionHash};
 use starknet_api::versioned_constants_logic::VersionedConstantsTrait;
+use tracing::error;
 
 use crate::errors::VirtualBlockExecutorError;
 
@@ -202,7 +203,14 @@ pub(crate) trait VirtualBlockExecutor: Send + 'static {
         let executed_class_hashes = transaction_executor
             .bouncer
             .lock()
-            .expect("Bouncer lock failed.")
+            .map_err(|e| {
+                error!(
+                    "Unexpected error: failed to acquire bouncer lock after transaction \
+                     execution. This should never happen: {}",
+                    e
+                );
+                VirtualBlockExecutorError::BouncerLockError(e.to_string())
+            })?
             .get_executed_class_hashes();
 
         Ok(VirtualBlockExecutionData {
```
