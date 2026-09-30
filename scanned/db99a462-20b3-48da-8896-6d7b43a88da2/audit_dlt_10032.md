# [?] fix: sequencer number panic.

## Summary
Severity: Unknown
Chain: Movement
Component: movement-network/movement
Published: 2024-07-15
Source: https://github.com/movement-network/movement/commit/7c54319e5e02131e6e995b077b26ccee3aa2335a
Type: security-commit

## Details
fix: sequencer number panic.

## Patch
### networks/suzuka/suzuka-client/.aptos/config.yaml
```diff
@@ -1,8 +0,0 @@
----
-profiles:
-  default:
-    private_key: "0xfbc0596f14bd008b20269a52e22311842453ccd3dd64575bc656dc8e755244b7"
-    public_key: "0xbe11803a40d33723d0a294cb657dd2477af4c31cae019f1e4bd783084033d1f6"
-    account: 00da3c48fe5d426966ae33945eff05cdbc5fb9a986c92d26a9d7665d99efdeff
-    rest_url: "http://localhost:30731/"
-    faucet_url: "http://localhost:30732/"
```

### networks/suzuka/suzuka-client/src/tests/mod.rs
```diff
@@ -1,18 +1,18 @@
 use crate::load_soak_testing::{execute_test, init_test, ExecutionConfig, Scenario, TestKind};
 use crate::{
-	coin_client::CoinClient,
+	coin_client::{CoinClient, /*TransferOptions*/},
 	rest_client::{
 		aptos_api_types::{TransactionOnChainData, ViewFunction},
 		Client, FaucetClient,
 	},
 	types::{chain_id::ChainId, LocalAccount},
+	transaction_builder::TransactionBuilder,
 };
 use anyhow::Context;
 use aptos_sdk::crypto::ed25519::Ed25519PrivateKey;
 use aptos_sdk::crypto::ValidCryptoMaterialStringExt;
 use aptos_sdk::move_types::identifier::Identifier;
 use aptos_sdk::move_types::language_storage::ModuleId;
-use aptos_sdk::transaction_builder::TransactionBuilder;
 use aptos_sdk::types::account_address::AccountAddress;
 use aptos_sdk::types::transaction::authenticator::AuthenticationKey;
 use aptos_sdk::types::transaction::EntryFunction;
@@ -180,6 +180,73 @@ async fn test_example_interaction() -> Result<(), anyhow::Error> {
 			.context("Failed to get Bob's account balance the second time")?
 	);
 
+	// malformed sequence number
+	/*let options = TransferOptions::default();
+	let chain_id = rest_client
+            .get_index()
+            .await
+            .context("Failed to get chain ID")?
+            .inner()
+            .chain_id;
+	let transaction_builder = TransactionBuilder::new(
+		TransactionPayload::EntryFunction(EntryFunction::new(
+			ModuleId::new(AccountAddress::ONE, Identifier::new("coin").unwrap()),
+			Identifier::new("transfer").unwrap(),
+			vec![TypeTag::from_str(options.coin_type).unwrap()],
+			vec![
+				bcs::to_bytes(&bob.address()).unwrap(),
+				bcs::to_bytes(&1_000).unwrap(),
+			],
+		)),
+		SystemTime::now()
+			.duration_since(UNIX_EPOCH)
+			.unwrap()
+			.as_secs()
+			+ options.timeout_secs,
+		ChainId::new(chain_id),
+	)
+	.sender(alice.address())
+	.sequence_number(alice.sequence_number())
+	.max_gas_amount(options.max_gas_amount)
+	.gas_unit_price(options.gas_unit_price);
+	let signed_txn = alice.sign_with_transaction_builder(transaction_builder);
+
+	// first send should work
+	let txn_hash = rest_client
+		.submit(&signed_txn)
+		.await
+		.context("Failed to submit transfer transaction")?
+		.into_inner();
+	rest_client.wait_for_transaction(&txn_hash).await.context(
+		"Failed when waiting for the transfer transaction with a malformed sequence number",
+	)?;
+
+	// second send should fail...
+	let txn_hash = rest_client
+		.submit(&signed_txn)
+		.await
+		.context("Failed to submit transfer transaction")?
+		.into_inner();
+	match rest_client.wait_for_transaction(&txn_hash).await {
+		Ok(_) => panic!("Expected transaction to fail"),
+		Err(e) => {
+			println!("Expected transaction failed: {:?}", e);
+		}
+	}
+
+	// ...but not crash the node.
+	// So, this should work.
+	let txn_hash = coin_client
+		.transfer(&mut alice, bob.address(), 1_000, None)
+		.await
+		.context("Failed to submit transaction to transfer coins")?; // <:!:section_5
+															 // :!:>section_6
+	rest_client
+		.wait_for_transaction(&txn_hash)
+		.await
+		.context("Failed when waiting for the transfer transaction")?;*/
+
+
 	Ok(())
 }
 
```

### protocol-units/execution/opt-executor/src/executor/transaction_pipe.rs
```diff
@@ -43,6 +43,7 @@ impl Executor {
 
 										let mut core_mempool = self.core_mempool.write().await;
 
+										tracing::debug!("Adding transaction to mempool: {:?} {:?}", transaction, transaction.sequence_number());
 										let status = core_mempool.add_txn(
 											transaction.clone(),
 											0,
@@ -53,9 +54,10 @@ impl Executor {
 
 										match status.code {
 											MempoolStatusCode::Accepted => {
-
+												tracing::debug!("Transaction accepted: {:?}", transaction);
 											},
 											_ => {
+												tracing::debug!("Transaction not accepted: {:?}", status);
 												Err(TransactionPipeError::TransactionNotAccepted(status))?;
 											}
 										}
@@ -174,6 +176,56 @@ mod tests {
 		Ok(())
 	}
 
+	#[tokio::test]
+	async fn test_pipe_mempool_with_malformed_transaction() -> Result<(), anyhow::Error> {
+		// header
+		let mut executor = Executor::try_test_default()?;
+		let user_transaction = create_signed_transaction(
+			0, 
+			executor.maptos_config.chain.maptos_chain_id.clone()
+		);
+
+		// send transaction to mempool
+		let (req_sender, callback) = oneshot::channel();
+		executor
+			.mempool_client_sender
+			.send(MempoolClientRequest::SubmitTransaction(user_transaction.clone(), req_sender))
+			.await?;
+
+		// tick the transaction pipe
+		let (tx, rx) = async_channel::unbounded();
+		executor.tick_transaction_pipe(tx.clone()).await?;
+
+		// receive the callback
+		callback.await??;
+
+		// receive the transaction
+		let received_transaction = rx.recv().await?;
+		assert_eq!(received_transaction, user_transaction);
+
+		// send the same transaction again
+		let (req_sender, callback) = oneshot::channel();
+		executor
+			.mempool_client_sender
+			.send(MempoolClientRequest::SubmitTransaction(user_transaction.clone(), req_sender))
+			.await?;
+
+		// tick the transaction pipe
+		executor.tick_transaction_pipe(tx).await?;
+		/*match executor.tick_transaction_pipe(tx).await {
+			Err(TransactionPipeError::TransactionNotAccepted(_)) => {}
+			Err(e) => return Err(anyhow::anyhow!("Unexpected error: {:?}", e)),
+			Ok(_) => return Err(anyhow::anyhow!("Expected error")),
+		}*/
+
+		callback.await??;
+
+		let received_transaction = rx.recv().await?;
+		assert_eq!(received_transaction, user_transaction);
+
+		Ok(())
+	}
+
 	#[tokio::test]
 	async fn test_pipe_mempool_from_api() -> Result<(), anyhow::Error> {
 		let mut executor = Executor::try_test_default()?;
```
