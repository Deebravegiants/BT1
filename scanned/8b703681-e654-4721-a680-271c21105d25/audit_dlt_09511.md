# [?] fix: Don't panic in SCC extrinsic detection (PRO-1250) (#5146)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2024-08-13
Source: https://github.com/chainflip-io/chainflip-backend/commit/6fd367fbb39f8211779b246f95e0e1efc76448ce
Type: security-commit

## Details
fix: Don't panic in SCC extrinsic detection (PRO-1250) (#5146)

fix: PRO-1250

## Patch
### engine/src/state_chain_observer/client/extrinsic_api/signed/submission_watcher.rs
```diff
@@ -443,47 +443,36 @@ impl<'a, 'env, BaseRpcClient: base_rpc_api::BaseRpcApi + Send + Sync + 'static>
 			warn!(target: "state_chain_client", request_id = request_id, submission_id = submission_id, "Block not found with hash {block_hash:?}");
 			None
 		} {
-			info!(target: "state_chain_client", request_id = request_id, submission_id = submission_id, "Request found in unchecked block '{block_hash:?}' with tx_hash '{tx_hash:?}'");
-			let Some((extrinsic_index, _extrinsic)) =
+			if let Some((extrinsic_index, _extrinsic)) =
 				extrinsics.iter().enumerate().find(|(_extrinsic_index, extrinsic)| {
 					tx_hash ==
 						<state_chain_runtime::Runtime as frame_system::Config>::Hashing::hash_of(
 							extrinsic,
 						)
-				})
-			else {
-				error!(target: "state_chain_client", request_id = request_id, submission_id = submission_id, "Submission not found in block '{block_hash:?}' with tx_hash '{tx_hash:?}', for the original request: {:?}", requests.get_mut(&request_id));
-				for (extrinsic_index, extrinsic) in extrinsics.iter().enumerate() {
-					error!(target: "state_chain_client", request_id = request_id, submission_id = submission_id, "Found extrinsic in block '{block_hash:?}' with index '{extrinsic_index:?}' and tx_hash '{tx_hash:?}'", tx_hash = <state_chain_runtime::Runtime as frame_system::Config>::Hashing::hash_of(
-						extrinsic,
+				}) {
+				let extrinsic_events = events
+					.iter()
+					.filter_map(|event_record| match event_record.as_ref() {
+						frame_system::EventRecord {
+							phase: frame_system::Phase::ApplyExtrinsic(index),
+							event,
+							..
+						} if *index as usize == extrinsic_index => Some(event.clone()),
+						_ => None,
+					})
+					.collect::<Vec<_>>();
+
+				if let Some(request) = requests.get_mut(&request_id) {
+					let until_in_block_sender = request.until_in_block_sender.take().unwrap();
+					let _result = until_in_block_sender.send(self.decide_extrinsic_success(
+						tx_hash,
+						extrinsic_events,
+						header.clone(),
 					));
 				}
-				error!(target: "state_chain_client", request_id = request_id, submission_id = submission_id, "All pending requests: {:?}", requests);
-				error!(target: "state_chain_client", request_id = request_id, submission_id = submission_id, "All pending submissions: {:?}", self.submissions_by_nonce);
-				error!(target: "state_chain_client", request_id = request_id, submission_id = submission_id, "Full block cache: {:?}", self.block_cache);
-				panic!("{SUBSTRATE_BEHAVIOUR}");
-			};
-
-			let extrinsic_events = events
-				.iter()
-				.filter_map(|event_record| match event_record.as_ref() {
-					frame_system::EventRecord {
-						phase: frame_system::Phase::ApplyExtrinsic(index),
-						event,
-						..
-					} if *index as usize == extrinsic_index => Some(event.clone()),
-					_ => None,
-				})
-				.collect::<Vec<_>>();
-
-			if let Some(request) = requests.get_mut(&request_id) {
-				info!(target: "state_chain_client", request_id = request_id, submission_id = submission_id, "Request found in block with hash {block_hash:?}, tx_hash {tx_hash:?}, and extrinsic index {extrinsic_index}.");
-				let until_in_block_sender = request.until_in_block_sender.take().unwrap();
-				let _result = until_in_block_sender.send(self.decide_extrinsic_success(
-					tx_hash,
-					extrinsic_events,
-					header.clone(),
-				));
+			} else {
+				// PRO-1250
+				error!(target: "state_chain_client", request_id = request_id, submission_id = submission_id, "Submission not found in block '{block_hash:?}' with tx_hash '{tx_hash:?}', for the original request: {:?}", requests.get_mut(&request_id));
 			}
 		}
 
```
