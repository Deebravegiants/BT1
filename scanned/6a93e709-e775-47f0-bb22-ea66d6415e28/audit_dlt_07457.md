# [?] Fix panic when peer is mid-handshake

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2024-01-18
Source: https://github.com/lightningdevkit/rust-lightning/commit/c7465bdb3e138def94f77848671567b24991345b
Type: security-commit

## Details
Fix panic when peer is mid-handshake

Peer::their_node_id is set to Some during the handshake process.
However, df3ab2ee2753e7f9ec02ddf1c8a51db77c50e35d accesses the field
unconditionally, causing a panic. This may be triggered if a gossip
message is received mid-handshake from another peer or if the user calls
broadcast_node_announcement during this time. The latter tends to be
executed on a timer.

Ensure that Peer::their_node_id is only accessed once the handshake is
complete.

## Patch
### lightning/src/ln/peer_handler.rs
```diff
@@ -1835,13 +1835,13 @@ impl<Descriptor: SocketDescriptor, CM: Deref, RM: Deref, OM: Deref, L: Deref, CM
 
 				for (_, peer_mutex) in peers.iter() {
 					let mut peer = peer_mutex.lock().unwrap();
-					let logger = WithContext::from(&self.logger, Some(peer.their_node_id.unwrap().0), None);
 					if !peer.handshake_complete() ||
 							!peer.should_forward_channel_announcement(msg.contents.short_channel_id) {
 						continue
 					}
 					debug_assert!(peer.their_node_id.is_some());
 					debug_assert!(peer.channel_encryptor.is_ready_for_encryption());
+					let logger = WithContext::from(&self.logger, Some(peer.their_node_id.unwrap().0), None);
 					if peer.buffer_full_drop_gossip_broadcast() {
 						log_gossip!(logger, "Skipping broadcast message to {:?} as its outbound buffer is full", peer.their_node_id);
 						continue;
@@ -1863,13 +1863,13 @@ impl<Descriptor: SocketDescriptor, CM: Deref, RM: Deref, OM: Deref, L: Deref, CM
 
 				for (_, peer_mutex) in peers.iter() {
 					let mut peer = peer_mutex.lock().unwrap();
-					let logger = WithContext::from(&self.logger, Some(peer.their_node_id.unwrap().0), None);
 					if !peer.handshake_complete() ||
 							!peer.should_forward_node_announcement(msg.contents.node_id) {
 						continue
 					}
 					debug_assert!(peer.their_node_id.is_some());
 					debug_assert!(peer.channel_encryptor.is_ready_for_encryption());
+					let logger = WithContext::from(&self.logger, Some(peer.their_node_id.unwrap().0), None);
 					if peer.buffer_full_drop_gossip_broadcast() {
 						log_gossip!(logger, "Skipping broadcast message to {:?} as its outbound buffer is full", peer.their_node_id);
 						continue;
@@ -1891,13 +1891,13 @@ impl<Descriptor: SocketDescriptor, CM: Deref, RM: Deref, OM: Deref, L: Deref, CM
 
 				for (_, peer_mutex) in peers.iter() {
 					let mut peer = peer_mutex.lock().unwrap();
-					let logger = WithContext::from(&self.logger, Some(peer.their_node_id.unwrap().0), None);
 					if !peer.handshake_complete() ||
 							!peer.should_forward_channel_announcement(msg.contents.short_channel_id)  {
 						continue
 					}
 					debug_assert!(peer.their_node_id.is_some());
 					debug_assert!(peer.channel_encryptor.is_ready_for_encryption());
+					let logger = WithContext::from(&self.logger, Some(peer.their_node_id.unwrap().0), None);
 					if peer.buffer_full_drop_gossip_broadcast() {
 						log_gossip!(logger, "Skipping broadcast message to {:?} as its outbound buffer is full", peer.their_node_id);
 						continue;
```
