# [?] net: bound peer protocol list in HELLO to prevent O(n^2) DoS

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-06-02
Source: https://github.com/Conflux-Chain/conflux-rust/commit/1d388fb676046259381af288ddd9e6138a5fa321
Type: security-commit

## Details
net: bound peer protocol list in HELLO to prevent O(n^2) DoS

A HELLO packet can be up to ~16MB (the 3-byte length prefix in
connection.rs), and `read_hello` decoded the peer-supplied `peer_caps`
list without any length bound, then scanned it for duplicate protocols
with an O(n^2) nested loop. Since `read_hello` runs inline on the single
network event-loop poll thread, one ~16MB packet (~2.8M entries) could
stall all inbound P2P processing for the whole node for minutes to hours.

Bound the advertised protocol count before decoding via
`iter().take(N + 1).count()` (constant-time thanks to the rlp offset
cache), rejecting peers that advertise more than a sane maximum, and
replace the O(n^2) duplicate scan with an O(n) HashSet. Real peers
advertise only a handful of protocols (cfx, clp, hsb).

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

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
