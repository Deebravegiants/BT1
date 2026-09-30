# [?] grandpa: fix race condition (#3542)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/substrate
Published: 2019-09-11
Source: https://github.com/paritytech/substrate/commit/c8e1120944fa0a547ea84ba5907ad878e7203dfc
Type: security-commit

## Details
grandpa: fix race condition (#3542)

* grandpa: ignore result of voter command send

* grandpa: avoid race condition on environment::finalize_block

## Patch
### core/finality-grandpa/src/environment.rs
```diff
@@ -871,6 +871,11 @@ pub(crate) fn finalize_block<B, Block: BlockT<Hash=H256>, E, RA>(
 	E: CallExecutor<Block, Blake2Hasher> + Send + Sync,
 	RA: Send + Sync,
 {
+	// NOTE: lock must be held through writing to DB to avoid race. this lock
+	//       also implicitly synchronizes the check for last finalized number
+	//       below.
+	let mut authority_set = authority_set.inner().write();
+
 	let status = client.info().chain;
 	if number <= status.finalized_number && client.hash(number)? == Some(hash) {
 		// This can happen after a forced change (triggered by the finality tracker when finality is stalled), since
@@ -885,9 +890,6 @@ pub(crate) fn finalize_block<B, Block: BlockT<Hash=H256>, E, RA>(
 		return Ok(());
 	}
 
-	// lock must be held through writing to DB to avoid race
-	let mut authority_set = authority_set.inner().write();
-
 	// FIXME #1483: clone only when changed
 	let old_authority_set = authority_set.clone();
 	// holds the old consensus changes in case it is changed below, needed for
```

### core/finality-grandpa/src/import.rs
```diff
@@ -590,9 +590,8 @@ where
 				info!(target: "finality", "Imported justification for block #{} that triggers \
 					command {}, signaling voter.", number, command);
 
-				if let Err(e) = self.send_voter_commands.unbounded_send(command) {
-					return Err(ConsensusError::ClientImport(e.to_string()).into());
-				}
+				// send the command to the voter
+				let _ = self.send_voter_commands.unbounded_send(command);
 			},
 			Err(CommandOrError::Error(e)) => {
 				return Err(match e {
```
