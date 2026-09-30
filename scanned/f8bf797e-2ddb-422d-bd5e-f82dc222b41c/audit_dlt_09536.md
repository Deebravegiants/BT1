# [?] Merge pull request #3539 from peilun-conflux/fix-hello-peercaps-dos

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-06-06
Source: https://github.com/Conflux-Chain/conflux-rust/commit/853322b8122097c6c2ba0575b1e78937a1d3dbb8
Type: security-commit

## Details
Merge pull request #3539 from peilun-conflux/fix-hello-peercaps-dos

net: bound HELLO peer protocol list to fix O(n²) DoS

## Patch
### crates/network/src/session.rs
```diff
@@ -23,6 +23,7 @@ use rlp::{Rlp, RlpStream};
 use serde::Deserialize;
 use serde_derive::Serialize;
 use std::{
+    collections::HashSet,
     convert::TryFrom,
     fmt,
     net::SocketAddr,
@@ -92,6 +93,9 @@ pub struct SessionDataWithDisconnectInfo {
 
 // id for Hello packet
 const PACKET_HELLO: u8 = 0x80;
+// A HELLO packet can be ~16MB; cap the advertised protocol count so a peer
+// can't pack it with millions of entries (real peers send a handful).
+const MAX_PEER_PROTOCOLS_IN_HELLO: usize = 64;
 // id for Disconnect packet
 const PACKET_DISCONNECT: u8 = 0x01;
 // id for protocol packet
@@ -426,19 +430,36 @@ impl Session {
             )));
         }
 
+        // `take(N + 1)` parses at most N+1 item headers (the rlp offset cache
+        // makes each O(1)), so an oversized list is rejected without walking
+        // it.
+        let peer_caps_count = rlp
+            .at(1)?
+            .iter()
+            .take(MAX_PEER_PROTOCOLS_IN_HELLO + 1)
+            .count();
+        if peer_caps_count > MAX_PEER_PROTOCOLS_IN_HELLO {
+            debug!(
+                "Too many protocols in hello: {}, remote = {}",
+                peer_caps_count, remote_network_id
+            );
+            return Err(self.send_disconnect(DisconnectReason::Custom(
+                "Invalid protocol list: too many protocols.".into(),
+            )));
+        }
+
         let mut peer_caps: Vec<ProtocolInfo> = rlp.list_at(1)?;
-        for i in 1..peer_caps.len() {
-            for j in 0..i {
-                if peer_caps[j].protocol == peer_caps[i].protocol {
-                    debug!(
-                        "Invalid protocol list from hello. Duplication: {:?},\
-                         remote = {}",
-                        peer_caps[i].protocol, remote_network_id
-                    );
-                    bail!(self.send_disconnect(DisconnectReason::Custom(
-                        "Invalid protocol list: duplication.".into()
-                    )))
-                }
+        let mut seen_protocols = HashSet::with_capacity(peer_caps.len());
+        for cap in &peer_caps {
+            if !seen_protocols.insert(cap.protocol) {
+                debug!(
+                    "Invalid protocol list from hello. Duplication: {:?}, \
+                     remote = {}",
+                    cap.protocol, remote_network_id
+                );
+                return Err(self.send_disconnect(DisconnectReason::Custom(
+                    "Invalid protocol list: duplication.".into(),
+                )));
             }
         }
 
```
