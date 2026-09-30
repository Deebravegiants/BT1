# [?] Fix a possible panic in PoS peer connecting.

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2022-10-13
Source: https://github.com/Conflux-Chain/conflux-rust/commit/e6eef7e3368ea015d0c3ca931dc2d0fa87d910e0
Type: security-commit

## Details
Fix a possible panic in PoS peer connecting.

## Patch
### core/src/pos/protocol/sync_protocol.rs
```diff
@@ -566,12 +566,17 @@ impl NetworkProtocolHandler for HotStuffSynchronizationProtocol {
 
         if add_new_peer {
             self.peers.insert(peer_hash.clone(), *node_id, None);
-            let peer_state =
-                self.peers.get(&peer_hash).expect("peer not found");
-            let mut peer_state = peer_state.write();
-            peer_state.id = *node_id;
-            peer_state.peer_hash = peer_hash;
-            self.request_manager.on_peer_connected(node_id);
+            if let Some(state) = self.peers.get(&peer_hash) {
+                let mut state = state.write();
+                state.id = *node_id;
+                state.peer_hash = peer_hash;
+                self.request_manager.on_peer_connected(node_id);
+            } else {
+                warn!(
+                    "PeerState is missing for peer: peer_hash={:?}",
+                    peer_hash
+                );
+            }
         } else {
             io.disconnect_peer(
                 node_id,
```
