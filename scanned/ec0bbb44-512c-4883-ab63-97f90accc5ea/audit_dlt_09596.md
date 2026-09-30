# [?] Fix underflow in handshake_count. (#1724)

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2020-07-28
Source: https://github.com/Conflux-Chain/conflux-rust/commit/d05ab6f3297927d5cc9f0b0948759ecea28f095d
Type: security-commit

## Details
Fix underflow in handshake_count. (#1724)

* Fix underflow in handshake_count.

* Allow delayed block body deleting.

## Patch
### core/src/sync/synchronization_protocol_handler.rs
```diff
@@ -879,8 +879,9 @@ impl SynchronizationProtocolHandler {
             }
 
             let until = {
-                let max_to_send = EPOCH_SYNC_MAX_INFLIGHT
-                    - self.request_manager.num_epochs_in_flight();
+                let max_to_send = EPOCH_SYNC_MAX_INFLIGHT.saturating_sub(
+                    self.request_manager.num_epochs_in_flight(),
+                );
                 let maybe_peer_info = self.syn.get_peer_info(&peer.unwrap());
                 if maybe_peer_info.is_err() {
                     // The peer is disconnected after we chose it.
```

### network/src/service.rs
```diff
@@ -832,7 +832,7 @@ impl NetworkServiceInner {
             .filter(|id| !self.sessions.contains_node(id) && *id != self_id)
             .take(min(
                 max_handshakes_per_round,
-                self.config.max_handshakes - handshake_count,
+                self.config.max_handshakes.saturating_sub(handshake_count),
             ))
         {
             self.connect_peer(&id, io);
```

### tests/full_node_tests/remove_old_eras_test.py
```diff
@@ -61,7 +61,7 @@ def run_test(self):
         # we expect the first few eras are removed
         self.log.info(f"checking deleted blocks...")
 
-        for epoch in range(0, 6 * ERA_EPOCH_COUNT):
+        for epoch in range(0, 4 * ERA_EPOCH_COUNT):
             archive_block = self.rpc[ARCHIVE_NODE].block_by_epoch(hex(epoch), include_txs=True)
             assert(archive_block != None)
 
```
