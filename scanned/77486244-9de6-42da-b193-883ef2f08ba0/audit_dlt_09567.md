# [?] Fix a race condition in light node connection.

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2023-09-28
Source: https://github.com/Conflux-Chain/conflux-rust/commit/778d53ceca6aff2504f8b972e6366d07de7679d2
Type: security-commit

## Details
Fix a race condition in light node connection.

## Patch
### core/src/light_protocol/common/peers.rs
```diff
@@ -63,6 +63,16 @@ where T: Default
             .or_insert(Arc::new(RwLock::new(T::default())));
     }
 
+    pub fn insert_with<F>(&self, peer: NodeId, f: F)
+    where F: FnOnce(&mut T) {
+        let peer_lock = {
+            let mut peers = self.0.write();
+            let entry = peers.entry(peer);
+            entry.or_insert(Arc::new(RwLock::new(T::default()))).clone()
+        };
+        f(&mut peer_lock.write());
+    }
+
     pub fn is_empty(&self) -> bool { self.0.read().is_empty() }
 
     pub fn contains(&self, peer: &NodeId) -> bool {
```

### core/src/light_protocol/provider.rs
```diff
@@ -1061,17 +1061,15 @@ impl NetworkProtocolHandler for Provider {
         );
 
         // insert handshaking peer, wait for StatusPing
-        self.peers.insert(*node_id);
-        self.peers.get(node_id).unwrap().write().protocol_version =
-            peer_protocol_version;
-
-        let peer = self.peers.get(node_id).expect("peer not found");
-        if let Some(ref file) = self.throttling_config_file {
-            peer.write().throttling =
-                TokenBucketManager::load(file, Some("light_protocol"))
-                    .expect("invalid throttling configuration file");
-        }
-        peer.write().last_heartbeat = Instant::now();
+        self.peers.insert_with(*node_id, |peer| {
+            if let Some(ref file) = self.throttling_config_file {
+                peer.throttling =
+                    TokenBucketManager::load(file, Some("light_protocol"))
+                        .expect("invalid throttling configuration file");
+            }
+            peer.protocol_version = peer_protocol_version;
+            peer.last_heartbeat = Instant::now();
+        });
     }
 
     fn on_peer_disconnected(&self, _io: &dyn NetworkContext, peer: &NodeId) {
```
