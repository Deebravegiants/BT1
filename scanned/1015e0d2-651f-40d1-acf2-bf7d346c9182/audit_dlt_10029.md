# [?] fix: missing transaction increment and underflow protection.

## Summary
Severity: Unknown
Chain: Movement
Component: movement-network/movement
Published: 2024-07-27
Source: https://github.com/movement-network/movement/commit/cd70d4fd1131138ec21fea18ad2717a62a300a72
Type: security-commit

## Details
fix: missing transaction increment and underflow protection.

## Patch
### protocol-units/execution/dof/src/v1.rs
```diff
@@ -13,6 +13,7 @@ use tokio::time::interval;
 use tokio_stream::wrappers::IntervalStream;
 use tokio::time::Duration;
 use tokio_stream::StreamExt;
+use std::sync::atomic::Ordering;
 
 #[derive(Clone)]
 pub struct Executor {
@@ -133,10 +134,12 @@ impl DynOptFinExecutor for Executor {
 	}
 
 	fn decrement_transactions_in_flight(&self, count : u64) {
-		self.executor.transactions_in_flight.fetch_sub(
-			count,
-			std::sync::atomic::Ordering::Relaxed, // relaxed because this is just for load shedding, now need for strict ordering.
-		);
+		
+		// fetch sub mind the underflow
+		self.executor.transactions_in_flight.fetch_update(Ordering::Relaxed, Ordering::Relaxed, |current| {
+			Some(current.saturating_sub(count))
+		}).unwrap_or_else(|_| 0);
+
 	}
 }
 
```

### protocol-units/execution/opt-executor/src/executor/mod.rs
```diff
@@ -8,7 +8,7 @@ use aptos_api::context::Context;
 use aptos_config::config::NodeConfig;
 use aptos_db::AptosDB;
 use aptos_executor::block_executor::BlockExecutor;
-use aptos_mempool::{core_mempool::CoreMempool, MempoolClientRequest, MempoolClientSender};
+use aptos_mempool::{MempoolClientRequest, MempoolClientSender};
 use aptos_storage_interface::DbReaderWriter;
 use aptos_types::validator_signer::ValidatorSigner;
 use aptos_vm::AptosVM;
```

### protocol-units/execution/opt-executor/src/executor/transaction_pipe.rs
```diff
@@ -126,6 +126,8 @@ impl Executor {
 					.send(transaction)
 					.await
 					.map_err(|e| anyhow::anyhow!("Error sending transaction: {:?}", e))?;
+				// increment transactions in flight
+				self.transactions_in_flight.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
 			}
 			_ => {
 				warn!("Transaction not accepted: {:?}", status);
```
