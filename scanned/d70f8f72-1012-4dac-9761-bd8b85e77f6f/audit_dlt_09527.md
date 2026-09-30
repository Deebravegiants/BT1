# [?] Merge pull request #672 from chainflip-io/fix/cfe-doesn't-panic-on-reidentify

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2021-10-13
Source: https://github.com/chainflip-io/chainflip-backend/commit/35ab1a17dccf9ad9181c34e6b76e239a432cad2c
Type: security-commit

## Details
Merge pull request #672 from chainflip-io/fix/cfe-doesn't-panic-on-reidentify

Only return error/cfe panic if self_identified with different Id

## Patch
### state-chain/client/cf-p2p/src/lib.rs
```diff
@@ -279,12 +279,17 @@ pub fn new_p2p_validator_network_node<
 				/// Identify ourselves to the network
 				fn self_identify(&self, validator_id: AccountIdBs58) -> Result<u64> {
 					let mut state = self.state.lock().unwrap();
-					if let Some(_existing_id) = state.local_validator_id {
-						Err(jsonrpc_core::Error::invalid_params(
-							"Have already self identified",
-						))
+					let validator_id: AccountId = validator_id.into();
+					if let Some(existing_id) = state.local_validator_id {
+						if existing_id != validator_id {
+							Err(jsonrpc_core::Error::invalid_params(
+								format!("Have already self identified with a different AccountId. New Id: {:?}, Old Id: {:?}", validator_id, existing_id),
+							))
+						} else {
+							log::warn!("Repeat call to self_identify");
+							Ok(200)
+						}
 					} else {
-						let validator_id: AccountId = validator_id.into();
 						state.local_validator_id = Some(validator_id.clone());
 						encode_and_send(
 							&self.p2p_network_service,
@@ -646,16 +651,18 @@ mod tests {
 	}
 
 	#[tokio::test]
-	async fn repeat_self_identify_fails() {
+	async fn repeat_self_identify_doesnt_fail_unless_id_different() {
 		let network = TestNetwork::new();
 		let node_0 = new_node(PeerId::random(), network.clone());
 
 		let try_self_identify =
-			|| async { node_0.self_identify(AccountIdBs58([0; 32])).compat().await };
+			|account_id: [u8; 32]| node_0.self_identify(AccountIdBs58(account_id)).compat();
 
-		assert!(matches!(try_self_identify().await, Ok(200u64)));
+		let matching_id = [1; 32];
+		assert!(matches!(try_self_identify(matching_id).await, Ok(200u64)));
+		assert!(matches!(try_self_identify(matching_id).await, Ok(200u64)));
 		assert!(matches!(
-			try_self_identify().await,
+			try_self_identify([2; 32]).await,
 			Err(RpcError::JsonRpcError(_))
 		));
 	}
```
