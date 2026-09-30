# [?] Fix network_eventloop crash and fix OOM during sync. (#1252)

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2020-04-13
Source: https://github.com/Conflux-Chain/conflux-rust/commit/a22ad65b1cb0a8c148380a2484a4ce5f5570aba5
Type: security-commit

## Details
Fix network_eventloop crash and fix OOM during sync. (#1252)

## Patch
### client/src/configuration.rs
```diff
@@ -151,6 +151,7 @@ build_config! {
         (max_outgoing_peers, (usize), 16)
         (max_outgoing_peers_archive, (usize), 0)
         (max_peers_tx_propagation, (usize), 128)
+        (max_unprocessed_block_count, (usize), (512))
         (min_peers_tx_propagation, (usize), 8)
         (received_tx_index_maintain_timeout_ms, (u64), 300_000)
         (request_block_with_public, (bool), false)
@@ -518,6 +519,9 @@ impl Configuration {
             heartbeat_timeout: Duration::from_millis(
                 self.raw_conf.heartbeat_timeout_ms,
             ),
+            max_unprocessed_block_count: self
+                .raw_conf
+                .max_unprocessed_block_count,
         }
     }
 
```

### core/src/sync/message/get_block_txn_response.rs
```diff
@@ -28,7 +28,13 @@ impl Handleable for GetBlockTxnResponse {
     fn handle(self, ctx: &Context) -> Result<(), Error> {
         let _timer = MeterTimer::time_func(BLOCK_TXN_HANDLE_TIMER.as_ref());
 
-        debug!("on_get_blocktxn_response");
+        debug!("on_get_blocktxn_response, hash={:?}", self.block_hash);
+
+        if ctx.manager.is_block_queue_full() {
+            warn!("recover_public_queue is full, discard GetBlockTxnResponse");
+            return Ok(());
+        }
+
         let resp_hash = self.block_hash;
         let req = ctx.match_request(self.request_id)?;
         let delay = req.delay;
```

### core/src/sync/message/get_blocks_response.rs
```diff
@@ -38,6 +38,14 @@ impl Handleable for GetBlocksResponse {
                 .collect::<Vec<H256>>()
         );
 
+        // TODO Check block size in advance to avoid attacks trying to cause
+        // OOM. TODO Add throttling on the requesting side to avoid
+        // wasting bandwidth.
+        if ctx.manager.is_block_queue_full() {
+            warn!("recover_public_queue is full, discard GetBlocksResponse");
+            return Ok(());
+        }
+
         for block in &self.blocks {
             debug!("transaction received by block: ratio=1");
             debug!(
```

### core/src/sync/message/get_compact_blocks_response.rs
```diff
@@ -44,6 +44,11 @@ impl Handleable for GetCompactBlocksResponse {
             self.blocks.len()
         );
 
+        if ctx.manager.is_block_queue_full() {
+            warn!("recover_public_queue is full, discard GetCompactBlocksResponse");
+            return Ok(());
+        }
+
         let req = ctx.match_request(self.request_id)?;
         let delay = req.delay;
         let mut to_relay_blocks = Vec::new();
```

### core/src/sync/synchronization_protocol_handler.rs
```diff
@@ -100,6 +100,8 @@ impl<T> AsyncTaskQueue<T> {
     }
 
     fn pop(&self) -> Option<T> { self.tasks.lock().pop_front() }
+
+    fn len(&self) -> usize { self.tasks.lock().len() }
 }
 
 pub struct RecoverPublicTask {
@@ -282,6 +284,7 @@ pub struct ProtocolConfiguration {
     pub timeout_observing_period_s: u64,
     pub max_allowed_timeout_in_observing_period: u64,
     pub demote_peer_for_timeout: bool,
+    pub max_unprocessed_block_count: usize,
 }
 
 impl SynchronizationProtocolHandler {
@@ -1448,6 +1451,11 @@ impl SynchronizationProtocolHandler {
         self.graph.remove_expire_blocks(timeout);
         self.relay_blocks(io, need_to_relay)
     }
+
+    pub fn is_block_queue_full(&self) -> bool {
+        self.recover_public_queue.len()
+            >= self.protocol_config.max_unprocessed_block_count
+    }
 }
 
 impl NetworkProtocolHandler for SynchronizationProtocolHandler {
```

### network/src/service.rs
```diff
@@ -1096,7 +1096,7 @@ impl NetworkServiceInner {
             }
 
             for (protocol, data) in messages {
-                io.handle(
+                if let Err(e) = io.handle(
                     stream,
                     0, /* We only have one handler for the execution
                         * event_loop,
@@ -1107,8 +1107,9 @@ impl NetworkServiceInner {
                         node_id: session_node_id.as_ref().unwrap().clone(),
                         data,
                     },
-                )
-                .expect("Fail to send NetworkIoMessage::HandleNetworkWork");
+                ) {
+                    warn!("Error occurs, discard protocol message: err={}", e);
+                }
             }
         }
     }
```

### util/io/src/service_mio.rs
```diff
@@ -581,7 +581,10 @@ where Message: Send + Sync + 'static
     /// Send low level io message
     pub fn send_io(&self, message: IoMessage<Message>) -> Result<(), IoError> {
         if let Some(ref channel) = self.channel {
-            channel.send(message)?
+            if let Err(e) = channel.send(message) {
+                warn!("Error sending message to eventloop channel, err={}", e);
+                return Err(e.into());
+            }
         }
         Ok(())
     }
@@ -638,6 +641,7 @@ where Message: Send + Sync + 'static
         debug!("start IoService");
         let mut config = EventLoopBuilder::new();
         config.messages_per_tick(1024);
+        config.notify_capacity(20960);
         let mut event_loop = config.build().expect("Error creating event loop");
         let channel = event_loop.channel();
         let handlers = Arc::new(RwLock::new(Slab::with_capacity(MAX_HANDLERS)));
```
