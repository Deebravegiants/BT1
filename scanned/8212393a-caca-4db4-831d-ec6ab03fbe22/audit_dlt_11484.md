# [?] fix: avoid panic in `get_context` when `get_block` fails (#661)

## Summary
Severity: Unknown
Chain: Light client
Component: a16z/helios
Published: 2025-07-24
Source: https://github.com/a16z/helios/commit/dc35564cfc72b527715ae0d1cbe4f335a3f7c634
Type: security-commit

## Details
fix: avoid panic in `get_context` when `get_block` fails (#661)

* fix: replace unwrap with proper error handling in get_context

Replace unwrap() calls in get_context() with proper error handling
to prevent panics when RPC providers returns error or None.

Fixes #627

* fix: replace unwrap with proper error handling in opstack get_context

Replace unwrap() calls in get_context() with proper error handling
to prevent panics when RPC providers returns error or None.

Related to #627

## Patch
### ethereum/src/evm.rs
```diff
@@ -59,7 +59,7 @@ impl<E: ExecutionProivder<Ethereum>> EthereumEvm<E> {
 
         let mut evm = self
             .get_context(tx, self.block_id, validate_tx)
-            .await
+            .await?
             .with_db(db)
             .build_mainnet();
 
@@ -88,14 +88,14 @@ impl<E: ExecutionProivder<Ethereum>> EthereumEvm<E> {
         tx: &TransactionRequest,
         block_id: BlockId,
         validate_tx: bool,
-    ) -> Context {
+    ) -> Result<Context, EvmError> {
         let block = self
             .execution
             .get_block(block_id, false)
             .await
-            .unwrap()
+            .map_err(|err| EvmError::Generic(err.to_string()))?
             .ok_or(ExecutionError::BlockNotFound(block_id))
-            .unwrap();
+            .map_err(|err| EvmError::Generic(err.to_string()))?;
 
         let mut tx_env = Self::tx_env(tx);
 
@@ -116,10 +116,10 @@ impl<E: ExecutionProivder<Ethereum>> EthereumEvm<E> {
         cfg.disable_base_fee = !validate_tx;
         cfg.disable_nonce_check = !validate_tx;
 
-        Context::mainnet()
+        Ok(Context::mainnet()
             .with_tx(tx_env)
             .with_block(Self::block_env(&block, &self.fork_schedule))
-            .with_cfg(cfg)
+            .with_cfg(cfg))
     }
 
     fn tx_env(tx: &TransactionRequest) -> TxEnv {
```

### opstack/src/evm.rs
```diff
@@ -63,7 +63,7 @@ impl<E: ExecutionProivder<OpStack>> OpStackEvm<E> {
 
         let mut evm = self
             .get_context(tx, self.block_id, validate_tx)
-            .await
+            .await?
             .with_db(db)
             .build_op();
 
@@ -92,14 +92,14 @@ impl<E: ExecutionProivder<OpStack>> OpStackEvm<E> {
         tx: &OpTransactionRequest,
         block_id: BlockId,
         validate_tx: bool,
-    ) -> OpContext<EmptyDB> {
+    ) -> Result<OpContext<EmptyDB>, EvmError> {
         let block = self
             .execution
             .get_block(block_id, false)
             .await
-            .unwrap()
+            .map_err(|err| EvmError::Generic(err.to_string()))?
             .ok_or(ExecutionError::BlockNotFound(block_id))
-            .unwrap();
+            .map_err(|err| EvmError::Generic(err.to_string()))?;
 
         let mut tx_env = Self::tx_env(tx);
 
@@ -123,10 +123,10 @@ impl<E: ExecutionProivder<OpStack>> OpStackEvm<E> {
         let mut op_tx_env = OpTransaction::new(tx_env);
         op_tx_env.enveloped_tx = Some(Bytes::new());
 
-        Context::op()
+        Ok(Context::op()
             .with_tx(op_tx_env)
             .with_block(Self::block_env(&block, &self.fork_schedule))
-            .with_cfg(cfg)
+            .with_cfg(cfg))
     }
 
     fn tx_env(tx: &OpTransactionRequest) -> TxEnv {
```

### tests/rpc_equivalence.rs
```diff
@@ -991,6 +991,29 @@ async fn test_get_historical_block(helios: &RootProvider, expected: &RootProvide
     Ok(())
 }
 
+async fn test_get_too_old_block(helios: &RootProvider, expected: &RootProvider) -> Result<()> {
+    let latest_block = expected.get_block_number().await?;
+    let latest_block_num = latest_block;
+
+    let old_block_num = latest_block_num.saturating_sub(20000);
+
+    let helios_block = helios.get_block_by_number(old_block_num.into()).await?;
+
+    ensure!(
+        helios_block.is_none(),
+        "Helios should return None for a block outside the proof window"
+    );
+
+    let expected_block = expected.get_block_by_number(old_block_num.into()).await?;
+
+    ensure!(
+        expected_block.is_some(),
+        "The trusted provider should have returned the historical block"
+    );
+
+    Ok(())
+}
+
 async fn test_get_historical_balance(helios: &RootProvider, expected: &RootProvider) -> Result<()> {
     let latest = helios.get_block_number().await?;
     let historical_block_num = latest.saturating_sub(100);
@@ -1430,6 +1453,7 @@ async fn rpc_equivalence_tests() {
         spawn_test!(test_get_logs_block_range, "get_logs_block_range"),
         // Historical Data
         spawn_test!(test_get_historical_block, "get_historical_block"),
+        spawn_test!(test_get_too_old_block, "get_too_old_block"),
     ];
 
     // Collect results
```
