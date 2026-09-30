# [?] Fix the deadlock during statements gossiping (#9868)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/polkadot-sdk
Published: 2025-09-30
Source: https://github.com/paritytech/polkadot-sdk/commit/ed4eebb461069f65fda4a88d44ee811dd8c010e3
Type: security-commit

## Details
Fix the deadlock during statements gossiping (#9868)

# Description

During statement store benchmarking we experienced deadlock-like
behavior which we found happened during statement propagation. Every
second statements were propagating, locking the index which possibly
caused the deadlock. After the fix, the observed behavior no longer
occurs.

Even though there is a possibility to unsync the DB and the index for
read operations and release locks earlier, which should be harmless, it
leads to regressions. I suspect because of concurrent access to many
calls of db.get(). Checked with the benchmarks in
https://github.com/paritytech/polkadot-sdk/pull/9884

## Integration

This PR should not affect downstream projects.

---------

Co-authored-by: cmd[bot] <41898282+github-actions[bot]@users.noreply.github.com>

## Patch
### prdoc/pr_9868.prdoc
```diff
@@ -0,0 +1,9 @@
+title: Fix the deadlock during statements gossiping
+doc:
+- audience: Node Dev
+  description: |-
+    During high load the statement store experiences deadlock-like behavior: every second statements were gossiping, locking the index which possibly caused the deadlock. After the fix, the observed behavior no longer occurs.
+
+crates:
+- name: sc-statement-store
+  bump: patch
```

### substrate/client/statement-store/src/lib.rs
```diff
@@ -488,12 +488,7 @@ impl Store {
 	where
 		Block: BlockT,
 		Block::Hash: From<BlockHash>,
-		Client: ProvideRuntimeApi<Block>
-			+ HeaderBackend<Block>
-			+ sc_client_api::ExecutorProvider<Block>
-			+ Send
-			+ Sync
-			+ 'static,
+		Client: ProvideRuntimeApi<Block> + HeaderBackend<Block> + Send + Sync + 'static,
 		Client::Api: ValidateStatement<Block>,
 	{
 		let store = Arc::new(Self::new(path, options, client, keystore, prometheus)?);
@@ -671,21 +666,25 @@ impl Store {
 	/// Perform periodic store maintenance
 	pub fn maintain(&self) {
 		log::trace!(target: LOG_TARGET, "Started store maintenance");
-		let deleted = self.index.write().maintain(self.timestamp());
+		let (deleted, active_count, expired_count): (Vec<_>, usize, usize) = {
+			let mut index = self.index.write();
+			let deleted = index.maintain(self.timestamp());
+			(deleted, index.entries.len(), index.expired.len())
+		};
 		let deleted: Vec<_> =
 			deleted.into_iter().map(|hash| (col::EXPIRED, hash.to_vec(), None)).collect();
-		let count = deleted.len() as u64;
+		let deleted_count = deleted.len() as u64;
 		if let Err(e) = self.db.commit(deleted) {
 			log::warn!(target: LOG_TARGET, "Error writing to the statement database: {:?}", e);
 		} else {
-			self.metrics.report(|metrics| metrics.statements_pruned.inc_by(count));
+			self.metrics.report(|metrics| metrics.statements_pruned.inc_by(deleted_count));
 		}
 		log::trace!(
 			target: LOG_TARGET,
 			"Completed store maintenance. Purged: {}, Active: {}, Expired: {}",
-			count,
-			self.index.read().entries.len(),
-			self.index.read().expired.len()
+			deleted_count,
+			active_count,
+			expired_count
 		);
 	}
 
@@ -764,7 +763,7 @@ impl StatementStore for Store {
 	fn statements(&self) -> Result<Vec<(Hash, Statement)>> {
 		let index = self.index.read();
 		let mut result = Vec::with_capacity(index.entries.len());
-		for h in self.index.read().entries.keys() {
+		for h in index.entries.keys() {
 			let encoded = self.db.get(col::STATEMENTS, h).map_err(|e| Error::Db(e.to_string()))?;
 			if let Some(encoded) = encoded {
 				if let Ok(statement) = Statement::decode(&mut encoded.as_slice()) {
```
