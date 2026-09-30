# [?] Fix a crash when a peer is disconnected during request_epochs. (#1593)

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2020-06-29
Source: https://github.com/Conflux-Chain/conflux-rust/commit/7825ab067b5f6f3d0ed6da53b53a0549f0486f36
Type: security-commit

## Details
Fix a crash when a peer is disconnected during request_epochs. (#1593)

* Fix a crash when a peer is disconnected during request_epochs.

## Patch
### core/src/sync/synchronization_protocol_handler.rs
```diff
@@ -822,13 +822,16 @@ impl SynchronizationProtocolHandler {
             let until = {
                 let max_to_send = EPOCH_SYNC_MAX_INFLIGHT
                     - self.request_manager.num_epochs_in_flight();
+                let maybe_peer_info = self.syn.get_peer_info(&peer.unwrap());
+                if maybe_peer_info.is_err() {
+                    // The peer is disconnected after we chose it.
+                    // `latest_requested` is not updated, so we just continue to
+                    // try another peer.
+                    continue;
+                }
 
-                let best_of_this_peer = self
-                    .syn
-                    .get_peer_info(&peer.unwrap())
-                    .unwrap()
-                    .read()
-                    .best_epoch;
+                let best_of_this_peer =
+                    maybe_peer_info.unwrap().read().best_epoch;
 
                 let until = from + cmp::min(EPOCH_SYNC_BATCH_SIZE, max_to_send);
                 cmp::min(until, best_of_this_peer + 1)
```
