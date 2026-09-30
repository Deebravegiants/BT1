# [?] fix(server): panic when there are no peers

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2024-05-01
Source: https://github.com/fedimint/fedimint/commit/3e56784e041a4a6de0aa2cd05a1ce1d4009c071e
Type: security-commit

## Details
fix(server): panic when there are no peers

## Patch
### fedimint-server/src/net/peers.rs
```diff
@@ -341,7 +341,12 @@ where
     }
 
     async fn receive(&mut self) -> Cancellable<(PeerId, T)> {
-        // TODO: optimize, don't throw away remaining futures
+        // if all peers banned (or just solo-federation), just hang here as there's
+        // never going to be any message. This avoids panic on `select_all` with
+        // no futures.
+        if self.connections.is_empty() {
+            std::future::pending().await
+        }
 
         let futures_non_banned = self.connections.iter_mut().map(|(&peer, connection)| {
             let receive_future = async move {
```

### fedimint-server/src/net/peers_reliable.rs
```diff
@@ -253,6 +253,13 @@ where
     }
 
     async fn receive(&mut self) -> Cancellable<(PeerId, T)> {
+        // if all peers banned (or just solo-federation), just hang here as there's
+        // never going to be any message. This avoids panic on `select_all` with
+        // no futures.
+        if self.connections.is_empty() {
+            std::future::pending().await
+        }
+
         // TODO: optimize, don't throw away remaining futures
 
         let futures_non_banned = self.connections.iter_mut().map(|(&peer, connection)| {
```
