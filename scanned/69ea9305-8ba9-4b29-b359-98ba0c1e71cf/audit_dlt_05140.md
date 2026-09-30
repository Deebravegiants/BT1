# [?] Fix race condition in async `UtxoFuture` resolution

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2026-01-28
Source: https://github.com/lightningdevkit/rust-lightning/commit/114f6b56864304cfeadc6f54fdc5abc2e8768d46
Type: security-commit

## Details
Fix race condition in async `UtxoFuture` resolution

Previously, we refactored the `GossipVerifier` to not require holding a
circular reference. As part of this, we moved to a model where the
`UtxoFuture`s are now polled by the background processor which checks
for completion through `get_and_clear_pending_msg_events`.

However, as part of this refactor we introduced race-condition: as we
only held `Weak` references in `PendingChecksContext` and the
`UtxoFuture` was directly dropped by the `GossipVerifier` after calling
`resolve`, the actual data was dropped with the future and gone when the
background processor attempted to retrieve and apply it via
`check_resolved_futures`.

Here, we fix this issue by simply holding on to the `state` `Arc`s in a
separate `pending_states` `Vec` that is only pruned in
`check_resolved_futures`, ensuring any completed results are collected
first.

Signed-off-by: Elias Rohrer <dev@tnull.de>

## Patch
### lightning/src/routing/utxo.rs
```diff
@@ -166,6 +166,7 @@ impl UtxoFuture {
 }
 
 struct PendingChecksContext {
+	pending_states: Vec<Arc<Mutex<UtxoMessages>>>,
 	channels: HashMap<u64, Weak<Mutex<UtxoMessages>>>,
 	nodes: HashMap<NodeId, Vec<Weak<Mutex<UtxoMessages>>>>,
 }
@@ -180,6 +181,7 @@ impl PendingChecks {
 	pub(super) fn new() -> Self {
 		PendingChecks {
 			internal: Mutex::new(PendingChecksContext {
+				pending_states: Vec::new(),
 				channels: new_hash_map(),
 				nodes: new_hash_map(),
 			}),
@@ -413,6 +415,20 @@ impl PendingChecks {
 							// handle the result in-line.
 							handle_result(res)
 						} else {
+							// To avoid cases where we drop the resolved data before it can be
+							// collected by `check_resolved_futures`, we here track all pending
+							// states at least until the next call of `check_resolved_futures`.
+							let pending_states = &mut pending_checks.pending_states;
+							if pending_states
+								.iter()
+								.find(|s| Arc::ptr_eq(s, &future.state))
+								.is_none()
+							{
+								// We're not already tracking the future state, keep the `Arc`
+								// around.
+								pending_states.push(Arc::clone(&future.state));
+							}
+
 							Self::check_replace_previous_entry(
 								msg,
 								full_msg,
@@ -574,6 +590,21 @@ impl PendingChecks {
 		let mut completed_states = Vec::new();
 		{
 			let mut lck = self.internal.lock().unwrap();
+			lck.pending_states.retain(|state| {
+				if state.lock().unwrap().complete.is_some() {
+					// We're done, collect the result and clean up.
+					completed_states.push(Arc::clone(&state));
+					false
+				} else {
+					if Arc::strong_count(state) == 1 {
+						// The future has been dropped.
+						false
+					} else {
+						// It's still inflight.
+						true
+					}
+				}
+			});
 			lck.channels.retain(|_, state| {
 				if let Some(state) = state.upgrade() {
 					if state.lock().unwrap().complete.is_some() {
@@ -1069,8 +1100,12 @@ mod tests {
 		assert!(network_graph.pending_checks.too_many_checks_pending());
 
 		// Once the future is drop'd (by resetting the `utxo_ret` value) the "too many checks" flag
-		// should reset to false.
+		// should not yet reset to false.
 		*chain_source.utxo_ret.lock().unwrap() = UtxoResult::Sync(Err(UtxoLookupError::UnknownTx));
+		assert!(network_graph.pending_checks.too_many_checks_pending());
+
+		// .. but it should once we called check_resolved_futures clearing the `pending_states`.
+		network_graph.pending_checks.check_resolved_futures(&network_graph);
 		assert!(!network_graph.pending_checks.too_many_checks_pending());
 	}
 }
```
