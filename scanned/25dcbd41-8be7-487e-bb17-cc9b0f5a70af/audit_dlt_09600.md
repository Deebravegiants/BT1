# [?] Fix unsigned underflow in `request_epochs`. (#1529)

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2020-06-11
Source: https://github.com/Conflux-Chain/conflux-rust/commit/9706ab1be2d5a6328b2a7450d68779ff24d729e4
Type: security-commit

## Details
Fix unsigned underflow in `request_epochs`. (#1529)

## Patch
### core/src/sync/synchronization_protocol_handler.rs
```diff
@@ -767,7 +767,7 @@ impl SynchronizationProtocolHandler {
         // `my_best_epoch` is missing, either because received
         // epoch_set is wrong or we have too many epochs with
         // blocks not received.
-        if latest_requested_epoch - my_best_epoch >= EPOCH_SYNC_MAX_GAP {
+        if latest_requested_epoch >= my_best_epoch + EPOCH_SYNC_MAX_GAP {
             if latest_request_time.elapsed()
                 < Duration::from_secs(EPOCH_SYNC_RESTART_TIMEOUT_S)
             {
@@ -780,7 +780,7 @@ impl SynchronizationProtocolHandler {
 
         while self.request_manager.num_epochs_in_flight()
             < EPOCH_SYNC_MAX_INFLIGHT
-            && latest_requested_epoch - my_best_epoch < EPOCH_SYNC_MAX_GAP
+            && latest_requested_epoch < my_best_epoch + EPOCH_SYNC_MAX_GAP
             && (latest_requested_epoch < median_peer_epoch
                 || median_peer_epoch == 0)
         {
```
