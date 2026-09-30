# [?] fix(api-client): don't panic on wrong peer_id

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2025-03-05
Source: https://github.com/fedimint/fedimint/commit/34eb3daa572a1ab6a9f1fb9c7382e2016923970e
Type: security-commit

## Details
fix(api-client): don't panic on wrong peer_id

It actually crashed the client on the api version discovery
thread when `fedimint-cli --our-id` was used.

Since we don't have e2e testing of every single scenario
everywhere, we should take it easy with panics, IMO.

## Patch
### fedimint-api-client/src/api/mod.rs
```diff
@@ -1076,7 +1076,7 @@ impl ReconnectClientConnections {
         let res = self
             .connections
             .get(&peer)
-            .unwrap_or_else(|| panic!("Could not find client connection for peer {peer}"))
+            .ok_or_else(|| PeerError::InvalidPeerId { peer_id: peer })?
             .connection()
             .await
             .context("Failed to connect to peer")
```
