# [?] [State Sync] Remove unneccessary panics to avoid DOS attacks.

## Summary
Severity: Unknown
Chain: Move
Component: move-language/move
Published: 2021-03-01
Source: https://github.com/move-language/move/commit/486dc12f01ef36d6db1f492f3399425fd22e1b90
Type: security-commit

## Details
[State Sync] Remove unneccessary panics to avoid DOS attacks.

Closes: #7778

## Patch
### state-sync/src/coordinator.rs
```diff
@@ -74,8 +74,6 @@ pub(crate) struct StateSyncCoordinator<T> {
     // An initial waypoint: for as long as the local version is less than a version determined by
     // waypoint a node is not going to be abl
     waypoint: Waypoint,
-    // network senders - (k, v) = (network ID, network sender)
-    network_senders: HashMap<NodeNetworkId, StateSyncSender>,
     // Actor for sending chunk requests
     // Manages to whom and how to send chunk requests
     request_manager: RequestManager,
@@ -123,7 +121,7 @@ impl<T: ExecutorProxyTrait> StateSyncCoordinator<T> {
             node_config.upstream.clone(),
             Duration::from_millis(retry_timeout_val),
             Duration::from_millis(node_config.state_sync.multicast_timeout_ms),
-            network_senders.clone(),
+            network_senders,
         );
 
         Ok(Self {
@@ -134,7 +132,6 @@ impl<T: ExecutorProxyTrait> StateSyncCoordinator<T> {
             role,
             waypoint,
             request_manager,
-            network_senders,
             subscriptions: HashMap::new(),
             sync_request: None,
             target_ledger_info: None,
@@ -870,12 +867,7 @@ impl<T: ExecutorProxyTrait> StateSyncCoordinator<T> {
             .chunk_response(chunk_response.clone())
             .peer(&peer);
         let msg = StateSyncMessage::GetChunkResponse(Box::new(chunk_response));
-
-        let network_sender = self
-            .network_senders
-            .get_mut(&peer.network_id())
-            .expect("missing network sender");
-        let send_result = network_sender.send_to(peer.peer_id(), msg);
+        let send_result = self.request_manager.send_chunk_response(&peer, msg);
         let send_result_label = if send_result.is_err() {
             counters::SEND_FAIL_LABEL
         } else {
```

### state-sync/src/executor_proxy.rs
```diff
@@ -263,12 +263,9 @@ impl ExecutorProxyTrait for ExecutorProxy {
             .configs()
             .iter()
             .filter(|(id, cfg)| {
-                &self
-                    .on_chain_configs
-                    .configs()
-                    .get(id)
-                    .expect("missing on-chain config value in local copy")
-                    != cfg
+                &self.on_chain_configs.configs().get(id).unwrap_or_else(|| {
+                    panic!("Missing on-chain config value in local copy: {}", id)
+                }) != cfg
             })
             .map(|(id, _)| *id)
             .collect::<HashSet<_>>();
```

### state-sync/src/request_manager.rs
```diff
@@ -296,10 +296,7 @@ impl RequestManager {
         let mut failed_peer_sends = vec![];
 
         for peer in peers {
-            let sender = self
-                .network_senders
-                .get_mut(&peer.network_id())
-                .expect("missing network sender for peer");
+            let mut sender = self.get_network_sender(&peer);
             let peer_id = peer.peer_id();
             let send_result = sender.send_to(peer_id, msg.clone());
             let curr_log = log.clone().peer(&peer);
@@ -330,6 +327,27 @@ impl RequestManager {
         }
     }
 
+    fn get_network_sender(&mut self, peer: &PeerNetworkId) -> StateSyncSender {
+        self.network_senders
+            .get_mut(&peer.network_id())
+            .unwrap_or_else(|| {
+                panic!(
+                    "Missing network sender for network: {:?}",
+                    peer.network_id()
+                )
+            })
+            .clone()
+    }
+
+    pub fn send_chunk_response(
+        &mut self,
+        peer: &PeerNetworkId,
+        message: StateSyncMessage,
+    ) -> Result<(), Error> {
+        self.get_network_sender(peer)
+            .send_to(peer.peer_id(), message)
+    }
+
     pub fn add_request(&mut self, version: u64, peers: Vec<PeerNetworkId>) -> ChunkRequestInfo {
         if let Some(prev_request) = self.requests.get_mut(&version) {
             let now = SystemTime::now();
@@ -342,14 +360,9 @@ impl RequestManager {
             prev_request.last_request_time = now;
             prev_request.clone()
         } else {
-            self.requests.insert(
-                version,
-                ChunkRequestInfo::new(version, peers, self.multicast_level),
-            );
-            self.requests
-                .get(&version)
-                .expect("missing chunk request that was just added")
-                .clone()
+            let chunk_request_info = ChunkRequestInfo::new(version, peers, self.multicast_level);
+            self.requests.insert(version, chunk_request_info.clone());
+            chunk_request_info
         }
     }
 
```
