# [?] fix(connectionmanager): don't panic on wakeup send during shutdown (#989) (#1029)

## Summary
Severity: Unknown
Chain: Kaspa
Component: kaspanet/rusty-kaspa
Published: 2026-06-15
Source: https://github.com/kaspanet/rusty-kaspa/commit/1fe3697b4ebf5d5ceac33fbe3b73b8d3348b3325
Type: security-commit

## Details
fix(connectionmanager): don't panic on wakeup send during shutdown (#989) (#1029)

`force_next_iteration.send(()).unwrap()` panics when the event-loop receiver has
already been dropped (e.g. on shutdown). `add_connection_request` is reachable
from the `AddPeer` RPC handler, so an `AddPeer` racing with daemon shutdown can
panic the gRPC/wRPC handler task.

The wakeup is fire-and-forget: if the loop is gone the wakeup is moot (the loop
is exiting anyway, and a 30s ticker drives it otherwise), so ignore the send
error instead of unwrapping. Applies to both the constructor wakeup (lib.rs:74)
and the per-request wakeup (lib.rs:109).

## Patch
### components/connectionmanager/src/lib.rs
```diff
@@ -71,7 +71,9 @@ impl ConnectionManager {
             default_port,
         });
         manager.clone().start_event_loop(rx);
-        manager.force_next_iteration.send(()).unwrap();
+        // Fire-and-forget wakeup: if the event loop is already gone the wakeup is moot, so ignore
+        // a send error rather than panicking (the receiver is dropped on shutdown).
+        let _ = manager.force_next_iteration.send(());
         manager
     }
 
@@ -106,7 +108,11 @@ impl ConnectionManager {
     pub async fn add_connection_request(&self, address: SocketAddr, is_permanent: bool) {
         // If the request already exists, it resets the attempts count and overrides the `is_permanent` setting.
         self.connection_requests.lock().await.insert(address, ConnectionRequest::new(is_permanent));
-        self.force_next_iteration.send(()).unwrap(); // We force the next iteration of the connection loop.
+        // Force the next iteration of the connection loop. This is a fire-and-forget wakeup, so if
+        // the event loop receiver was already dropped (e.g. during shutdown) the send is a no-op
+        // rather than a panic. add_connection_request is reachable from the AddPeer RPC handler,
+        // which can race with shutdown.
+        let _ = self.force_next_iteration.send(());
     }
 
     pub async fn stop(&self) {
```
