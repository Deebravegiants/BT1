# [?] fix(anvil): stop pending-block queries from crashing the node (#16714)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-09-08
Source: https://github.com/foundry-rs/foundry/commit/93c758bc44d6d6010be10ce310479774fb2ebbcb
Type: security-commit

## Details
fix(anvil): stop pending-block queries from crashing the node (#16714)

* fix(anvil): stop pending-block eth_call/getBlockByNumber from crashing the node

with_pending_block called the same execute_with_block_executor() that
do_mine_block already handles via ?, but did .expect(\"pending block
execution failed\") on it instead - any Err there panics the whole
process (release builds set panic = \"abort\", so this takes down every
connected client, not just the current request).

It's reachable in ordinary operation: Prague+ post-execution deposit-
request parsing decodes any log at the deposit-contract address whose
topic0 matches DepositEvent, and a contract placed there via the
documented anvil_setCode cheat that emits a shorter/malformed log makes
that decode fail. Reproduced with a minimal LOG1-then-STOP contract at
the deposit address plus a pending tx, then eth_getBlockByNumber(\"pending\").

with_pending_block/pending_block now return Result and propagate the
error like do_mine_block does, threaded through every caller up to the
JSON-RPC boundary (eth_getBlockByNumber, eth_getHeaderByNumber,
eth_getBlockTransactionCountByNumber, eth_getBlockReceipts,
eth_getTransactionByBlockNumberAndIndex, simulate's pending path).

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Lh6V2uPTUqauqq45BM7m5k

* fix(anvil): return pending block result directly

Remove redundant Result wrapping flagged by clippy without changing pending-block error propagation. AI-assisted CI fix by Centaur.

Co-authored-by: Derek Cofausper <256792747+decofe@users.noreply.github.com>

---------

Co-authored-by: Claude Sonnet 5 <noreply@anthropic.com>
Co-authored-by: DaniPopes <57450786+DaniPopes@users.noreply.github.com>
Co-authored-by: Derek Cofausper <256792747+decofe@users.noreply.github.com>
Co-authored-by: Mablr <59505383+mablr@users.noreply.github.com>

## Patch
### .changelog/anvil-pending-block-panic-on-invalid-deposit-log.md
```diff
@@ -0,0 +1,5 @@
+---
+anvil: patch
+---
+
+Fixed a node panic when building the pending block if a Prague+ post-execution deposit-request log couldn't be decoded, instead of returning an RPC error.
```

### crates/anvil/src/eth/api.rs
```diff
@@ -1578,7 +1578,7 @@ impl EthApi<FoundryNetwork> {
     ) -> Result<Option<AnyRpcTransaction>> {
         node_info!("eth_getTransactionByBlockNumberAndIndex");
         if block == BlockNumber::Pending {
-            return Ok(self.pending_block_full().await.and_then(|block| {
+            return Ok(self.pending_block_full().await?.and_then(|block| {
                 let WithOtherFields { inner: block, .. } = block.0;
                 block.transactions.into_transactions().nth(idx.into())
             }));
@@ -2581,7 +2581,7 @@ impl EthApi<FoundryNetwork> {
     pub async fn block_by_number(&self, number: BlockNumber) -> Result<Option<AnyRpcBlock>> {
         node_info!("eth_getBlockByNumber");
         if number == BlockNumber::Pending {
-            return Ok(Some(self.pending_block().await));
+            return Ok(Some(self.pending_block().await?));
         }
 
         self.backend.block_by_number(number).await
@@ -2596,7 +2596,7 @@ impl EthApi<FoundryNetwork> {
     ) -> Result<Option<WithOtherFields<AnyRpcHeader>>> {
         node_info!("eth_getHeaderByNumber");
         if number == BlockNumber::Pending {
-            let WithOtherFields { inner: block, other } = self.pending_block().await.0;
+            let WithOtherFields { inner: block, other } = self.pending_block().await?.0;
             return Ok(Some(WithOtherFields { inner: block.header, other }));
         }
 
@@ -2612,7 +2612,7 @@ impl EthApi<FoundryNetwork> {
     pub async fn block_by_number_full(&self, number: BlockNumber) -> Result<Option<AnyRpcBlock>> {
         node_info!("eth_getBlockByNumber");
         if number == BlockNumber::Pending {
-            return Ok(self.pending_block_full().await);
+            return self.pending_block_full().await;
         }
         self.backend.block_by_number_full(number).await
     }
@@ -2717,7 +2717,7 @@ impl EthApi<FoundryNetwork> {
         node_info!("eth_getBlockTransactionCountByNumber");
         if block_number == BlockNumber::Pending {
             let txs = self.pool.ready_transactions().collect();
-            let block = self.backend.pending_block(txs).await;
+            let block = self.backend.pending_block(txs).await?;
             return Ok(Some(U256::from(block.block.body.transactions.len())));
         }
 
@@ -3669,7 +3669,7 @@ impl EthApi<FoundryNetwork> {
             if transactions.is_empty() {
                 return Ok(Some(Vec::new()));
             }
-            return Ok(Some(self.backend.pending_block_receipts(transactions).await));
+            return Ok(Some(self.backend.pending_block_receipts(transactions).await?));
         }
 
         self.backend.block_receipts(number).await
@@ -4774,25 +4774,28 @@ impl EthApi<FoundryNetwork> {
     }
 
     /// Returns the pending block with tx hashes
-    async fn pending_block(&self) -> AnyRpcBlock {
+    async fn pending_block(&self) -> Result<AnyRpcBlock> {
         let transactions = self.pool.ready_transactions().collect::<Vec<_>>();
-        let info = self.backend.pending_block(transactions).await;
-        self.backend.convert_block(info.block)
+        let info = self.backend.pending_block(transactions).await?;
+        Ok(self.backend.convert_block(info.block))
     }
 
     /// Returns the full pending block with `Transaction` objects
-    async fn pending_block_full(&self) -> Option<AnyRpcBlock> {
+    async fn pending_block_full(&self) -> Result<Option<AnyRpcBlock>> {
         let transactions = self.pool.ready_transactions().collect::<Vec<_>>();
         let BlockInfo { block, transactions, receipts: _ } =
-            self.backend.pending_block(transactions).await;
+            self.backend.pending_block(transactions).await?;
 
         let mut partial_block = self.backend.convert_block(block.clone());
 
         let mut block_transactions = Vec::with_capacity(block.body.transactions.len());
         let base_fee = self.backend.base_fee();
 
         for info in transactions {
-            let tx = block.body.transactions.get(info.transaction_index as usize)?.clone();
+            let Some(tx) = block.body.transactions.get(info.transaction_index as usize).cloned()
+            else {
+                return Ok(None);
+            };
 
             let tx = transaction_build(
                 Some(info.transaction_hash),
@@ -4806,7 +4809,7 @@ impl EthApi<FoundryNetwork> {
 
         partial_block.transactions = BlockTransactions::from(block_transactions);
 
-        Some(partial_block)
+        Ok(Some(partial_block))
     }
 
     /// Prepares transaction request by filling missing fields using Anvil's API, then attempts
```

### crates/anvil/src/eth/backend/mem/mod.rs
```diff
@@ -5674,7 +5674,7 @@ where
     pub async fn pending_block(
         &self,
         pool_transactions: Vec<Arc<PoolTransaction<FoundryTxEnvelope>>>,
-    ) -> BlockInfo<N> {
+    ) -> Result<BlockInfo<N>, BlockchainError> {
         self.with_pending_block(pool_transactions, |_, block| block).await
     }
 
@@ -5685,7 +5685,7 @@ where
         &self,
         pool_transactions: Vec<Arc<PoolTransaction<FoundryTxEnvelope>>>,
         f: F,
-    ) -> T
+    ) -> Result<T, BlockchainError>
     where
         F: FnOnce(Box<dyn MaybeFullDatabase + '_>, BlockInfo<N>) -> T,
     {
@@ -5701,27 +5701,21 @@ where
         let inspector_tx_config = self.inspector_tx_config();
         let gas_config = self.pool_tx_gas_config(&evm_env);
 
-        let (pool_result, block_result) = self
-            .execute_with_block_executor(
-                &mut cache_db,
-                &evm_env,
-                parent_hash,
-                spec_id,
-                self.hardfork(),
-                Some(B256::ZERO),
-                BlockExecutionKind::Complete,
-                &pool_transactions,
-                &gas_config,
-                &inspector_tx_config,
-                &|pool_tx, account| {
-                    self.validate_pool_transaction_for(
-                        &pool_tx.pending_transaction,
-                        account,
-                        &evm_env,
-                    )
-                },
-            )
-            .expect("pending block execution failed");
+        let (pool_result, block_result) = self.execute_with_block_executor(
+            &mut cache_db,
+            &evm_env,
+            parent_hash,
+            spec_id,
+            self.hardfork(),
+            Some(B256::ZERO),
+            BlockExecutionKind::Complete,
+            &pool_transactions,
+            &gas_config,
+            &inspector_tx_config,
+            &|pool_tx, account| {
+                self.validate_pool_transaction_for(&pool_tx.pending_transaction, account, &evm_env)
+            },
+        )?;
 
         // Extract inner CacheDB (which implements MaybeFullDatabase)
         let cache_db = cache_db.0;
@@ -5739,7 +5733,7 @@ where
             Some(B256::ZERO),
         );
 
-        f(Box::new(cache_db), block_info)
+        Ok(f(Box::new(cache_db), block_info))
     }
 
     /// Returns the ERC20/TIP20 token balance for an account.
@@ -6200,7 +6194,7 @@ where
                         let block = block.block;
                         f(state, block_env_from_header(&block.header))
                     })
-                    .await;
+                    .await?;
                 return Ok(result);
             }
             Some(BlockRequest::Number(bn)) => Some(BlockNumber::Number(bn)),
@@ -6264,7 +6258,7 @@ where
                         let block_env = block_env_from_header(&block_info.block.header);
                         f(state, block_env, context)
                     })
-                    .await;
+                    .await?;
             }
             Some(BlockRequest::Number(number)) => Some(BlockNumber::Number(number)),
             None => None,
@@ -7289,9 +7283,9 @@ where
     pub async fn pending_block_receipts(
         &self,
         pool_transactions: Vec<Arc<PoolTransaction<FoundryTxEnvelope>>>,
-    ) -> Vec<FoundryTxReceipt> {
+    ) -> Result<Vec<FoundryTxReceipt>, BlockchainError> {
         let BlockInfo { block, transactions, receipts } =
-            self.pending_block(pool_transactions).await;
+            self.pending_block(pool_transactions).await?;
         let block_hash = block.header.hash_slow();
         let mut pending_receipts = Vec::with_capacity(receipts.len());
         let mut next_log_index = 0;
@@ -7309,7 +7303,7 @@ where
             next_log_index += log_count;
         }
 
-        pending_receipts
+        Ok(pending_receipts)
     }
 
     /// Returns the blocks receipts for the given number
@@ -8552,7 +8546,7 @@ impl Backend<FoundryNetwork> {
                         optimism_jovian,
                     )
                 })
-                .await
+                .await?
             }
             block_request => {
                 let base_block_number = match block_request.as_ref() {
```

### crates/anvil/tests/it/eip6110.rs
```diff
@@ -0,0 +1,39 @@
+use alloy_eips::{BlockNumberOrTag, eip6110::MAINNET_DEPOSIT_CONTRACT_ADDRESS};
+use alloy_network::TransactionBuilder;
+use alloy_primitives::bytes;
+use alloy_provider::Provider;
+use alloy_rpc_types::TransactionRequest;
+use alloy_serde::WithOtherFields;
+use anvil::{NodeConfig, spawn};
+use foundry_evm::hardfork::EthereumHardfork;
+
+#[tokio::test(flavor = "multi_thread")]
+async fn eip6110_pending_block_returns_malformed_deposit_error() {
+    let node_config = NodeConfig::test().with_hardfork(Some(EthereumHardfork::Prague.into()));
+    let (api, handle) = spawn(node_config).await;
+    let provider = handle.http_provider();
+
+    // PUSH32 DepositEvent topic, PUSH1 size=0, PUSH1 offset=0, LOG1, STOP.
+    api.anvil_set_code(
+        MAINNET_DEPOSIT_CONTRACT_ADDRESS,
+        bytes!("7f649bbc62d0e31342afea4e5cd82d4049e7e1ee912fc0889aa790803be39038c560006000a100"),
+    )
+    .await
+    .unwrap();
+    api.anvil_set_auto_mine(false).await.unwrap();
+    let from = handle.dev_wallets().next().unwrap().address();
+    let _pending = provider
+        .send_transaction(WithOtherFields::new(
+            TransactionRequest::default()
+                .from(from)
+                .to(MAINNET_DEPOSIT_CONTRACT_ADDRESS)
+                .with_gas_limit(100_000),
+        ))
+        .await
+        .unwrap();
+
+    let error = provider.get_block_by_number(BlockNumberOrTag::Pending).await.unwrap_err();
+    let response = error.as_error_resp().expect("should return a JSON-RPC error");
+    assert_eq!(response.code, -32603);
+    assert_eq!(provider.get_block_number().await.unwrap(), 0);
+}
```

### crates/anvil/tests/it/main.rs
```diff
@@ -6,6 +6,7 @@ mod beacon_api;
 mod block_index;
 mod eip2935;
 mod eip4844;
+mod eip6110;
 mod eip7702;
 mod eip7928;
 mod filter;
```
