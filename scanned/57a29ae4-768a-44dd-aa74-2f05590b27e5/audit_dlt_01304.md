# [?] Correct a race condition when dialing peers (#4056)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2023-03-16
Source: https://github.com/sigp/lighthouse/commit/3d99ce25f83224da2cea20936fc03ff21635460a
Type: security-commit

## Details
Correct a race condition when dialing peers (#4056)

There is a race condition which occurs when multiple discovery queries return at almost the exact same time and they independently contain a useful peer we would like to connect to.

The condition can occur that we can add the same peer to the dial queue, before we get a chance to process the queue. 
This ends up displaying an error to the user: 
```
ERRO Dialing an already dialing peer
```
Although this error is harmless it's not ideal. 

There are two solutions to resolving this:
1. As we decide to dial the peer, we change the state in the peer-db to dialing (before we add it to the queue) which would prevent other requests from adding to the queue. 
2. We prevent duplicates in the dial queue

This PR has opted for 2. because 1. will complicate the code in that we are changing states in non-intuitive places. Although this technically adds a very slight performance cost, its probably a cleaner solution as we can keep the state-changing logic in one place.

## Patch
### Cargo.lock
```diff
@@ -1614,6 +1614,16 @@ dependencies = [
  "tokio-util 0.6.10",
 ]
 
+[[package]]
+name = "delay_map"
+version = "0.3.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "e4355c25cbf99edcb6b4a0e906f6bdc6956eda149e84455bea49696429b2f8e8"
+dependencies = [
+ "futures",
+ "tokio-util 0.7.7",
+]
+
 [[package]]
 name = "deposit_contract"
 version = "0.2.0"
@@ -1812,7 +1822,7 @@ dependencies = [
  "aes 0.7.5",
  "aes-gcm 0.9.4",
  "arrayvec",
- "delay_map",
+ "delay_map 0.1.2",
  "enr",
  "fnv",
  "futures",
@@ -4404,7 +4414,7 @@ dependencies = [
 name = "lighthouse_network"
 version = "0.2.0"
 dependencies = [
- "delay_map",
+ "delay_map 0.3.0",
  "directory",
  "dirs",
  "discv5",
@@ -5021,7 +5031,7 @@ name = "network"
 version = "0.2.0"
 dependencies = [
  "beacon_chain",
- "delay_map",
+ "delay_map 0.3.0",
  "derivative",
  "environment",
  "error-chain",
@@ -7985,6 +7995,7 @@ dependencies = [
  "futures-io",
  "futures-sink",
  "pin-project-lite 0.2.9",
+ "slab",
  "tokio",
  "tracing",
 ]
```

### Dockerfile
```diff
@@ -1,4 +1,4 @@
-FROM rust:1.65.0-bullseye AS builder
+FROM rust:1.66.0-bullseye AS builder
 RUN apt-get update && apt-get -y upgrade && apt-get install -y cmake libclang-dev protobuf-compiler
 COPY . lighthouse
 ARG FEATURES
```

### beacon_node/lighthouse_network/Cargo.toml
```diff
@@ -42,7 +42,7 @@ strum = { version = "0.24.0", features = ["derive"] }
 superstruct = "0.5.0"
 prometheus-client = "0.18.0"
 unused_port = { path = "../../common/unused_port" }
-delay_map = "0.1.1"
+delay_map = "0.3.0"
 void = "1"
 
 [dependencies.libp2p]
```

### beacon_node/lighthouse_network/src/peer_manager/mod.rs
```diff
@@ -13,7 +13,7 @@ use peerdb::{client::ClientKind, BanOperation, BanResult, ScoreUpdateResult};
 use rand::seq::SliceRandom;
 use slog::{debug, error, trace, warn};
 use smallvec::SmallVec;
-use std::collections::VecDeque;
+use std::collections::BTreeMap;
 use std::{
     sync::Arc,
     time::{Duration, Instant},
@@ -77,7 +77,7 @@ pub struct PeerManager<TSpec: EthSpec> {
     /// The target number of peers we would like to connect to.
     target_peers: usize,
     /// Peers queued to be dialed.
-    peers_to_dial: VecDeque<(PeerId, Option<Enr>)>,
+    peers_to_dial: BTreeMap<PeerId, Option<Enr>>,
     /// The number of temporarily banned peers. This is used to prevent instantaneous
     /// reconnection.
     // NOTE: This just prevents re-connections. The state of the peer is otherwise unaffected. A
@@ -308,7 +308,7 @@ impl<TSpec: EthSpec> PeerManager<TSpec> {
     /// proves resource constraining, we should switch to multiaddr dialling here.
     #[allow(clippy::mutable_key_type)]
     pub fn peers_discovered(&mut self, results: HashMap<PeerId, Option<Instant>>) -> Vec<PeerId> {
-        let mut to_dial_peers = Vec::new();
+        let mut to_dial_peers = Vec::with_capacity(4);
 
         let connected_or_dialing = self.network_globals.connected_or_dialing_peers();
         for (peer_id, min_ttl) in results {
@@ -398,7 +398,7 @@ impl<TSpec: EthSpec> PeerManager<TSpec> {
 
     // A peer is being dialed.
     pub fn dial_peer(&mut self, peer_id: &PeerId, enr: Option<Enr>) {
-        self.peers_to_dial.push_back((*peer_id, enr));
+        self.peers_to_dial.insert(*peer_id, enr);
     }
 
     /// Reports if a peer is banned or not.
@@ -1185,6 +1185,18 @@ impl<TSpec: EthSpec> PeerManager<TSpec> {
 
         // Unban any peers that have served their temporary ban timeout
         self.unban_temporary_banned_peers();
+
+        // Maintains memory by shrinking mappings
+        self.shrink_mappings();
+    }
+
+    // Reduce memory footprint by routinely shrinking associating mappings.
+    fn shrink_mappings(&mut self) {
+        self.inbound_ping_peers.shrink_to(5);
+        self.outbound_ping_peers.shrink_to(5);
+        self.status_peers.shrink_to(5);
+        self.temporary_banned_peers.shrink_to_fit();
+        self.sync_committee_subnets.shrink_to_fit();
     }
 
     // Update metrics related to peer scoring.
```

### beacon_node/lighthouse_network/src/peer_manager/network_behaviour.rs
```diff
@@ -89,7 +89,7 @@ impl<TSpec: EthSpec> NetworkBehaviour for PeerManager<TSpec> {
             self.events.shrink_to_fit();
         }
 
-        if let Some((peer_id, maybe_enr)) = self.peers_to_dial.pop_front() {
+        if let Some((peer_id, maybe_enr)) = self.peers_to_dial.pop_first() {
             self.inject_peer_connection(&peer_id, ConnectingType::Dialing, maybe_enr);
             let handler = self.new_handler();
             return Poll::Ready(NetworkBehaviourAction::Dial {
```

### beacon_node/network/Cargo.toml
```diff
@@ -43,7 +43,7 @@ if-addrs = "0.6.4"
 strum = "0.24.0"
 tokio-util = { version = "0.6.3", features = ["time"] }
 derivative = "2.2.0"
-delay_map = "0.1.1"
+delay_map = "0.3.0"
 ethereum-types = { version = "0.14.1", optional = true }
 operation_pool =  { path = "../operation_pool" }
 execution_layer =  { path = "../execution_layer" }
```

### common/lru_cache/src/time.rs
```diff
@@ -160,6 +160,12 @@ where
         self.map.contains(key)
     }
 
+    /// Shrink the mappings to fit the current size.
+    pub fn shrink_to_fit(&mut self) {
+        self.map.shrink_to_fit();
+        self.list.shrink_to_fit();
+    }
+
     #[cfg(test)]
     #[track_caller]
     fn check_invariant(&self) {
```

### lighthouse/Cargo.toml
```diff
@@ -4,7 +4,7 @@ version = "3.5.1"
 authors = ["Sigma Prime <contact@sigmaprime.io>"]
 edition = "2021"
 autotests = false
-rust-version = "1.65"
+rust-version = "1.66"
 
 [features]
 default = ["slasher-mdbx"]
```
