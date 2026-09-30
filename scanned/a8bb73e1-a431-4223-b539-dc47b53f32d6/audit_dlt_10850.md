# [?] Fix network panic (#2990)

## Summary
Severity: Unknown
Chain: Starcoin
Component: starcoinorg/starcoin
Published: 2021-10-27
Source: https://github.com/starcoinorg/starcoin/commit/2fa585749447371c2b1a6b17936ce4fc4c5b6a83
Type: security-commit

## Details
Fix network panic (#2990)

## Patch
### network-p2p/peerset/src/lib.rs
```diff
@@ -520,9 +520,6 @@ impl Peerset {
                 let before = peer_reputation.reputation();
                 let after = reput_tick(before);
                 trace!(target: "peerset", "Fleeting {}: {} -> {}", peer_id, before, after);
-                if after < BANNED_THRESHOLD {
-                    self.message_queue.push_back(Message::Banned(peer_id))
-                }
                 peer_reputation.set_reputation(after);
                 drop(peer_reputation);
                 // If the peer has no connection to it,
@@ -533,6 +530,9 @@ impl Peerset {
                         peersstate::Peer::NotConnected(peer) => {
                             if peer.last_connected_or_discovered() + FORGET_AFTER < now {
                                 peer.forget_peer();
+                                if after < BANNED_THRESHOLD {
+                                    self.message_queue.push_back(Message::Banned(peer_id))
+                                }
                             }
                         }
                         peersstate::Peer::Unknown(_) => {
```

### network-p2p/src/protocol.rs
```diff
@@ -491,8 +491,7 @@ impl Protocol {
                 );
             }
             self.peerset_handle.report_peer(who, rep::GENESIS_MISMATCH);
-            self.behaviour.disconnect_peer(&who, set_id);
-            return CustomMessageOutcome::Banned(who);
+            return CustomMessageOutcome::None;
         }
         if status.version < MIN_VERSION || CURRENT_VERSION < status.min_supported_version {
             log!(
@@ -501,8 +500,7 @@ impl Protocol {
                 "Peer {:?} using unsupported protocol version {}", who, status.version
             );
             self.peerset_handle.report_peer(who, rep::BAD_PROTOCOL);
-            self.behaviour.disconnect_peer(&who, set_id);
-            return CustomMessageOutcome::Banned(who);
+            return CustomMessageOutcome::None;
         }
         debug!(target: "network-p2p", "Connected {}", who);
         let peer = Peer {
```

### network-p2p/src/protocol/generic_proto/behaviour.rs
```diff
@@ -1235,8 +1235,6 @@ impl NetworkBehaviour for GenericProto {
             let mut entry = if let Entry::Occupied(entry) = self.peers.entry((*peer_id, set_id)) {
                 entry
             } else {
-                error!(target: "sub-libp2p", "inject_connection_closed: State mismatch in the custom protos handler");
-                debug_assert!(false);
                 return;
             };
             match mem::replace(entry.get_mut(), PeerState::Poisoned) {
```

### network-p2p/src/request_responses.rs
```diff
@@ -348,7 +348,9 @@ impl NetworkBehaviour for RequestResponsesBehaviour {
         endpoint: &ConnectedPoint,
     ) {
         for (p, _) in self.protocols.values_mut() {
-            NetworkBehaviour::inject_connection_closed(p, peer_id, conn, endpoint)
+            if p.is_connected(peer_id) {
+                NetworkBehaviour::inject_connection_closed(p, peer_id, conn, endpoint)
+            }
         }
     }
 
```
