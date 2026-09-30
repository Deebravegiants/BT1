# [?] Fix panic when fetching block header in backend.state_at (#3054)

## Summary
Severity: Unknown
Chain: Moonbeam
Component: moonbeam-foundation/moonbeam
Published: 2024-11-25
Source: https://github.com/moonbeam-foundation/moonbeam/commit/ca369f6aec2c9a78c24a657c1e0d1ae04542b91e
Type: security-commit

## Details
Fix panic when fetching block header in backend.state_at (#3054)

## Patch
### node/service/src/lazy_loading/backend.rs
```diff
@@ -1350,40 +1350,42 @@ impl<Block: BlockT + DeserializeOwned> backend::Backend<Block> for Backend<Block
 			.read()
 			.get(&hash)
 			.cloned()
-			.map(|state| (state, false))
+			.map(|state| Ok((state, false)))
 			.unwrap_or_else(|| {
-				let header: Block::Header = self
-					.rpc_client
+				self.rpc_client
 					.header::<Block>(Some(hash))
 					.ok()
 					.flatten()
-					.expect("block header");
-
-				let checkpoint = self.fork_checkpoint.clone();
-				let state = if header.number().gt(checkpoint.number()) {
-					let parent = self.state_at(*header.parent_hash()).ok();
-
-					ForkedLazyBackend::<Block> {
-						rpc_client: self.rpc_client.clone(),
-						block_hash: Some(hash),
-						fork_block: checkpoint.hash(),
-						db: parent.clone().map_or(Default::default(), |p| p.db),
-						removed_keys: parent.map_or(Default::default(), |p| p.removed_keys),
-						before_fork: false,
-					}
-				} else {
-					ForkedLazyBackend::<Block> {
-						rpc_client: self.rpc_client.clone(),
-						block_hash: Some(hash),
-						fork_block: checkpoint.hash(),
-						db: Default::default(),
-						removed_keys: Default::default(),
-						before_fork: true,
-					}
-				};
-
-				(state, true)
-			});
+					.ok_or(sp_blockchain::Error::UnknownBlock(
+						format!("Failed to fetch block header: {:?}", hash).into(),
+					))
+					.map(|header| {
+						let checkpoint = self.fork_checkpoint.clone();
+						let state = if header.number().gt(checkpoint.number()) {
+							let parent = self.state_at(*header.parent_hash()).ok();
+
+							ForkedLazyBackend::<Block> {
+								rpc_client: self.rpc_client.clone(),
+								block_hash: Some(hash),
+								fork_block: checkpoint.hash(),
+								db: parent.clone().map_or(Default::default(), |p| p.db),
+								removed_keys: parent.map_or(Default::default(), |p| p.removed_keys),
+								before_fork: false,
+							}
+						} else {
+							ForkedLazyBackend::<Block> {
+								rpc_client: self.rpc_client.clone(),
+								block_hash: Some(hash),
+								fork_block: checkpoint.hash(),
+								db: Default::default(),
+								removed_keys: Default::default(),
+								before_fork: true,
+							}
+						};
+
+						(state, true)
+					})
+			})?;
 
 		if should_write {
 			self.states.write().insert(hash, backend.clone());
```
