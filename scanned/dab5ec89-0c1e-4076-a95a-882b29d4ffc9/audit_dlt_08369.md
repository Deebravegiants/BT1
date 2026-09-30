# [?] [State Sync] Fix potential storage race condition with consensus.

## Summary
Severity: Unknown
Chain: Move
Component: move-language/move
Published: 2021-01-26
Source: https://github.com/move-language/move/commit/4be5722b9e9388c7386b80a29f70e38b38b74b67
Type: security-commit

## Details
[State Sync] Fix potential storage race condition with consensus.

Closes: #7365

## Patch
### state-sync/src/coordinator.rs
```diff
@@ -933,6 +933,19 @@ impl<T: ExecutorProxyTrait> StateSyncCoordinator<T> {
     /// * Verifies and stores chunk in response
     /// * Triggers post-commit actions based on new local state after successful chunk processing in above step
     async fn process_chunk_response(&mut self, peer: &PeerNetworkId, response: GetChunkResponse) {
+        // Part 0: ensure consensus isn't running, otherwise we might get a race with storage writes.
+        if self.is_consensus_executing() {
+            error!(LogSchema::event_log(
+                LogEntry::ProcessChunkResponse,
+                LogEvent::ConsensusIsRunning
+            )
+            .peer(peer)
+            .error(&format_err!(
+                "Received a chunk response but consensus is now running so we cannot process it!"
+            )));
+            return;
+        }
+
         let new_txns = response.txn_list_with_proof.transactions.clone();
         // Part 1: check response, validate and store chunk
         // any errors thrown here should be for detecting actual bad chunks
@@ -943,7 +956,6 @@ impl<T: ExecutorProxyTrait> StateSyncCoordinator<T> {
                     .peer(peer)
                     .error(&e)
             );
-
             counters::APPLY_CHUNK_COUNT
                 .with_label_values(&[
                     &peer.raw_network_id().to_string(),
@@ -1128,16 +1140,23 @@ impl<T: ExecutorProxyTrait> StateSyncCoordinator<T> {
             .execute_chunk(txn_list_with_proof, target, intermediate_end_of_epoch_li)
     }
 
+    /// Returns true if consensus is currently executing and state sync should
+    /// therefore not write to storage. Reads are still permitted (e.g., to
+    /// handle chunk requests).
+    fn is_consensus_executing(&mut self) -> bool {
+        self.is_initialized() && self.role == RoleType::Validator && self.sync_request.is_none()
+    }
+
     /// Ensures that state sync is making progress:
     /// * kick-starts initial sync process (= initialization syncing to waypoint)
     /// * issue a new request if too much time passed since requesting highest_synced_version + 1.
     fn check_progress(&mut self) {
         if self.request_manager.no_available_peers() {
             return;
         }
-        if self.role == RoleType::Validator && self.sync_request.is_none() && self.is_initialized()
-        {
-            return;
+
+        if self.is_consensus_executing() {
+            return; // No need to send out chunk requests: consensus is executing.
         }
 
         // check that we made progress in fulfilling consensus sync request
```

### state-sync/src/logging.rs
```diff
@@ -125,6 +125,7 @@ pub enum LogEvent {
     ChunkRequestInfo,
 
     // ProcessChunkResponse events
+    ConsensusIsRunning,
     Received,
     SendChunkRequestFail,
     ApplyChunkSuccess,
```
