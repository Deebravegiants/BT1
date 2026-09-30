# [?] fix: crash node on batch write failure.

## Summary
Severity: Unknown
Chain: Movement
Component: movement-network/movement
Published: 2024-08-07
Source: https://github.com/movement-network/movement/commit/efb76032747dfa518bbf212d3cab0ea817f61c0b
Type: security-commit

## Details
fix: crash node on batch write failure.

## Patch
### networks/suzuka/suzuka-full-node/src/partial.rs
```diff
@@ -164,26 +164,12 @@ where
 		Ok(())
 	}
 
-	async fn send_transaction_batch_writes(&self) -> Result<(), anyhow::Error> {
+	async fn write_transactions_to_da(&self) -> Result<(), anyhow::Error> {
 		loop {
 			self.next_transaction_batch_write().await?;
 		}
 	}
 
-	pub async fn write_transactions_to_da(&self) -> Result<(), anyhow::Error> {
-		loop {
-			// run send transaction batch writes and submit transaction batch writes concurrently
-			match self.send_transaction_batch_writes().await {
-				Ok(_) => {}
-				Err(e) => {
-					error!("Failed to send transaction batch writes: {:?}", e);
-				}
-			}
-		}
-
-		Ok(())
-	}
-
 	// receive transactions from the transaction channel and send them to be executed
 	// ! This assumes the m1 da light node is running sequencer mode
 	pub async fn read_blocks_from_da(&self) -> Result<(), anyhow::Error> {
```
