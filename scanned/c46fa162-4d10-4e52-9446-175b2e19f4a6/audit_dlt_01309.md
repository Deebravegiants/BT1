# [?] Correct a dial race condition (#2992)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2022-02-07
Source: https://github.com/sigp/lighthouse/commit/675c7b7e26dd0fd1cddc4bac04b99f7b9d7dd584
Type: security-commit

## Details
Correct a dial race condition (#2992)

## Issue Addressed

On a network with few nodes, it is possible that the same node can be found from a subnet discovery and a normal peer discovery at the same time.

The network behaviour loads these peers into events and processes them when it has the chance. It can happen that the same peer can enter the event queue more than once and then attempt to be dialed twice. 

This PR shifts the registration of nodes in the peerdb as being dialed before they enter the NetworkBehaviour queue, preventing multiple attempts of the same peer being entered into the queue and avoiding the race condition.

## Patch
### beacon_node/lighthouse_network/src/behaviour/mod.rs
```diff
@@ -812,7 +812,11 @@ impl<TSpec: EthSpec> Behaviour<TSpec> {
         for peer_id in peers_to_dial {
             debug!(self.log, "Dialing cached ENR peer"; "peer_id" => %peer_id);
             // Remove the ENR from the cache to prevent continual re-dialing on disconnects
+
             self.discovery.remove_cached_enr(&peer_id);
+            // For any dial event, inform the peer manager
+            let enr = self.discovery_mut().enr_of_peer(&peer_id);
+            self.peer_manager.inject_dialing(&peer_id, enr);
             self.internal_events
                 .push_back(InternalBehaviourMessage::DialPeer(peer_id));
         }
@@ -1096,6 +1100,9 @@ impl<TSpec: EthSpec> NetworkBehaviourEventProcess<DiscoveryEvent> for Behaviour<
                 let to_dial_peers = self.peer_manager.peers_discovered(results);
                 for peer_id in to_dial_peers {
                     debug!(self.log, "Dialing discovered peer"; "peer_id" => %peer_id);
+                    // For any dial event, inform the peer manager
+                    let enr = self.discovery_mut().enr_of_peer(&peer_id);
+                    self.peer_manager.inject_dialing(&peer_id, enr);
                     self.internal_events
                         .push_back(InternalBehaviourMessage::DialPeer(peer_id));
                 }
@@ -1147,9 +1154,6 @@ impl<TSpec: EthSpec> Behaviour<TSpec> {
         if let Some(event) = self.internal_events.pop_front() {
             match event {
                 InternalBehaviourMessage::DialPeer(peer_id) => {
-                    // For any dial event, inform the peer manager
-                    let enr = self.discovery_mut().enr_of_peer(&peer_id);
-                    self.peer_manager.inject_dialing(&peer_id, enr);
                     // Submit the event
                     let handler = self.new_handler();
                     return Poll::Ready(NBAction::Dial {
```
