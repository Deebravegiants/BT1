# [?] Fix crash during initialization of event monitor when node is down (#895)

## Summary
Severity: Unknown
Chain: Cosmos
Component: informalsystems/hermes
Published: 2021-05-06
Source: https://github.com/informalsystems/hermes/commit/37f05c9b9899dacfb449ebb2d6b9f20898086b23
Type: security-commit

## Details
Fix crash during initialization of event monitor when node is down (#895)

* Introduce error type for event monitor

* Do not crash if chain runtime fails to subscribe to events

* Gracefully handle runtime init error in `start-multi` command

* Improve worker error context

* Fix chain id in error message if spawning chain runtime fails

* Print channel error when one arises

* Refactor event monitor loop a little bit

* Update changelog

## Patch
### CHANGELOG.md
```diff
@@ -31,6 +31,7 @@ Jongwhan Lee (@leejw51crypto) ([#878]).
   - Fix pagination in gRPC query for clients ([#811])
   - Fix relayer crash when hermes starts in the same time as packets are being sent ([#851])
   - Fix missing port information in `hermes query channels` ([#840])
+  - Fix crash during initialization of event monitor when node is down ([#863])
 
 - [ibc-relayer-cli]
   - Fix for `ft-transfer` mismatching arguments ([#869])
@@ -51,6 +52,7 @@ Jongwhan Lee (@leejw51crypto) ([#878]).
 [#851]: https://github.com/informalsystems/ibc-rs/issues/851
 [#854]: https://github.com/informalsystems/ibc-rs/issues/854
 [#861]: https://github.com/informalsystems/ibc-rs/issues/861
+[#863]: https://github.com/informalsystems/ibc-rs/issues/863
 [#869]: https://github.com/informalsystems/ibc-rs/issues/869
 [#878]: https://github.com/informalsystems/ibc-rs/issues/878
 
```

### relayer-cli/src/commands/start_multi.rs
```diff
@@ -85,8 +85,26 @@ fn start_all_connections(config: &Config) -> Result<Output, BoxError> {
                 conn.a_chain, conn.b_chain
             );
 
-            let chain_a = registry.get_or_spawn(&conn.a_chain)?;
-            let chain_b = registry.get_or_spawn(&conn.b_chain)?;
+            let chain_a = registry.get_or_spawn(&conn.a_chain);
+            let chain_b = registry.get_or_spawn(&conn.b_chain);
+
+            let (chain_a, chain_b) = match (chain_a, chain_b) {
+                (Ok(a), Ok(b)) => (a, b),
+                (Err(err), _) => {
+                    error!(
+                        "failed to initialize runtime for chain '{}': {}",
+                        conn.a_chain, err
+                    );
+                    continue;
+                }
+                (_, Err(err)) => {
+                    error!(
+                        "failed to initialize runtime for chain '{}': {}",
+                        conn.b_chain, err
+                    );
+                    continue;
+                }
+            };
 
             s.spawn(|_| {
                 let supervisor = Supervisor::spawn(chain_a, chain_b).unwrap();
```

### relayer/src/chain/cosmos.rs
```diff
@@ -374,9 +374,11 @@ impl Chain for CosmosSdkChain {
             self.config.id.clone(),
             self.config.websocket_addr.clone(),
             rt,
-        )?;
+        )
+        .map_err(Kind::EventMonitor)?;
+
+        event_monitor.subscribe().map_err(Kind::EventMonitor)?;
 
-        event_monitor.subscribe().unwrap();
         let monitor_thread = thread::spawn(move || event_monitor.run());
 
         Ok((event_receiver, Some(monitor_thread)))
```

### relayer/src/chain/runtime.rs
```diff
@@ -2,36 +2,38 @@ use std::{sync::Arc, thread};
 
 use crossbeam_channel as channel;
 use tokio::runtime::Runtime as TokioRuntime;
+use tracing::error;
 
-use ibc::ics02_client::client_consensus::AnyConsensusStateWithHeight;
-use ibc::ics02_client::events::UpdateClient;
-use ibc::ics02_client::misbehaviour::AnyMisbehaviour;
 use ibc::ics04_channel::channel::IdentifiedChannelEnd;
 use ibc::{
     events::IbcEvent,
     ics02_client::{
-        client_consensus::{AnyConsensusState, ConsensusState},
+        client_consensus::{AnyConsensusState, AnyConsensusStateWithHeight, ConsensusState},
         client_state::{AnyClientState, ClientState},
+        events::UpdateClient,
         header::{AnyHeader, Header},
+        misbehaviour::AnyMisbehaviour,
+    },
+    ics03_connection::{connection::ConnectionEnd, version::Version},
+    ics04_channel::{
+        channel::ChannelEnd,
+        packet::{PacketMsgType, Sequence},
     },
-    ics03_connection::connection::ConnectionEnd,
-    ics03_connection::version::Version,
-    ics04_channel::channel::ChannelEnd,
-    ics04_channel::packet::{PacketMsgType, Sequence},
     ics23_commitment::commitment::CommitmentPrefix,
     ics24_host::identifier::{ChannelId, ClientId, ConnectionId, PortId},
     proofs::Proofs,
     query::QueryTxRequest,
     signer::Signer,
     Height,
 };
-use ibc_proto::ibc::core::channel::v1::QueryChannelsRequest;
-use ibc_proto::ibc::core::client::v1::QueryConsensusStatesRequest;
+
 use ibc_proto::ibc::core::{
     channel::v1::{
-        PacketState, QueryNextSequenceReceiveRequest, QueryPacketAcknowledgementsRequest,
-        QueryPacketCommitmentsRequest, QueryUnreceivedAcksRequest, QueryUnreceivedPacketsRequest,
+        PacketState, QueryChannelsRequest, QueryNextSequenceReceiveRequest,
+        QueryPacketAcknowledgementsRequest, QueryPacketCommitmentsRequest,
+        QueryUnreceivedAcksRequest, QueryUnreceivedPacketsRequest,
     },
+    client::v1::QueryConsensusStatesRequest,
     commitment::v1::MerkleProof,
 };
 
@@ -91,10 +93,10 @@ impl<C: Chain + Send + 'static> ChainRuntime<C> {
         let light_client = chain.init_light_client()?;
 
         // Start the event monitor
-        let (event_receiver, event_monitor_thread) = chain.init_event_monitor(rt.clone())?;
+        let (event_batch_rx, event_monitor_thread) = chain.init_event_monitor(rt.clone())?;
 
         // Instantiate & spawn the runtime
-        let (handle, runtime_thread) = Self::init(chain, light_client, event_receiver, rt);
+        let (handle, runtime_thread) = Self::init(chain, light_client, event_batch_rx, rt);
 
         let threads = Threads {
             chain_runtime: runtime_thread,
@@ -153,12 +155,13 @@ impl<C: Chain + Send + 'static> ChainRuntime<C> {
         loop {
             channel::select! {
                 recv(self.event_receiver) -> event_batch => {
-                    if let Ok(event_batch) = event_batch {
-                        self.event_bus
-                            .broadcast(Arc::new(event_batch))
-                            .map_err(|e| Kind::Channel.context(e))?;
-                    } else {
-                        // TODO: Handle error
+                    match event_batch {
+                        Ok(event_batch) => {
+                            self.event_bus
+                                .broadcast(Arc::new(event_batch))
+                                .map_err(|e| Kind::Channel.context(e))?;
+                        },
+                        Err(e) => error!("received error via event bus: {}", e),
                     }
                 },
                 recv(self.request_receiver) -> event => {
@@ -296,7 +299,7 @@ impl<C: Chain + Send + 'static> ChainRuntime<C> {
                             self.query_txs(request, reply_to)?
                         },
 
-                        Err(_e) => todo!(), // TODO: Handle error?
+                        Err(e) => error!("received error via chain request channel: {}", e),
                     }
                 },
             }
```

### relayer/src/error.rs
```diff
@@ -34,6 +34,10 @@ pub enum Kind {
     #[error("Websocket error to endpoint {0}")]
     Websocket(tendermint_rpc::Url),
 
+    /// Event monitor error
+    #[error("Event monitor")]
+    EventMonitor(crate::event::monitor::Error),
+
     /// GRPC error (typically raised by the GRPC client or the GRPC requester)
     #[error("GRPC error")]
     Grpc,
```

### relayer/src/event/monitor.rs
```diff
@@ -1,19 +1,40 @@
 use std::sync::Arc;
 
-use anomaly::BoxError;
 use crossbeam_channel as channel;
 use futures::stream::StreamExt;
 use futures::{stream::select_all, Stream};
 use itertools::Itertools;
 use tendermint_rpc::{query::EventType, query::Query, SubscriptionClient, WebSocketClient};
+use thiserror::Error;
 use tokio::runtime::Runtime as TokioRuntime;
 use tokio::task::JoinHandle;
-use tracing::{debug, error, info};
+use tracing::{debug, error, info, warn};
 
-use ibc::{events::IbcEvent, ics24_host::identifier::ChainId};
+use ibc::{events::IbcEvent, ics02_client::height::Height, ics24_host::identifier::ChainId};
 
-use crate::error::{Error, Kind};
-use ibc::ics02_client::height::Height;
+#[derive(Debug, Clone, Error)]
+pub enum Error {
+    #[error("failed to create WebSocket client driver: {0}")]
+    ClientCreationFailed(tendermint_rpc::Error),
+
+    #[error("failed to terminate previous WebSocket client driver: {0}")]
+    ClientTerminationFailed(Arc<tokio::task::JoinError>),
+
+    #[error("failed to run previous WebSocket client driver to completion: {0}")]
+    ClientCompletionFailed(tendermint_rpc::Error),
+
+    #[error("failed to subscribe to events via WebSocket client: {0}")]
+    ClientSubscriptionFailed(tendermint_rpc::Error),
+
+    #[error("failed to collect events over WebSocket subscription: {0}")]
+    NextEventBatchFailed(tendermint_rpc::Error),
+
+    #[error("failed to extract IBC events: {0}")]
+    CollectEventsFailed(String),
+
+    #[error("failed to send event batch through channel")]
+    ChannelSendFailed,
+}
 
 /// A batch of events from a chain at a specific height
 #[derive(Clone, Debug)]
@@ -70,11 +91,9 @@ impl EventMonitor {
         let (tx, rx) = channel::unbounded();
 
         let ws_addr = node_addr.clone();
-        let (websocket_client, websocket_driver) = rt.block_on(async move {
-            WebSocketClient::new(ws_addr.clone())
-                .await
-                .map_err(|e| Kind::Websocket(ws_addr).context(e))
-        })?;
+        let (websocket_client, websocket_driver) = rt
+            .block_on(async move { WebSocketClient::new(ws_addr.clone()).await })
+            .map_err(Error::ClientCreationFailed)?;
 
         let websocket_driver_handle = rt.spawn(websocket_driver.run());
 
@@ -112,27 +131,38 @@ impl EventMonitor {
     }
 
     /// Clear the current subscriptions, and subscribe again to all queries.
-    pub fn subscribe(&mut self) -> Result<(), BoxError> {
+    pub fn subscribe(&mut self) -> Result<(), Error> {
         let mut subscriptions = vec![];
 
         for query in &self.event_queries {
+            debug!("subscribing to query: {}", query);
+
             let subscription = self
                 .rt
-                .block_on(self.websocket_client.subscribe(query.clone()))?;
+                .block_on(self.websocket_client.subscribe(query.clone()))
+                .map_err(Error::ClientSubscriptionFailed)?;
 
             subscriptions.push(subscription);
         }
 
         self.subscriptions = Box::new(select_all(subscriptions));
 
+        debug!("subscribed to all queries");
+
         Ok(())
     }
 
-    fn try_reconnect(&mut self) -> Result<(), BoxError> {
+    fn try_reconnect(&mut self) -> Result<(), Error> {
+        warn!(
+            "trying to reconnect to WebSocket endpoint: {}",
+            self.node_addr
+        );
+
         // Try to reconnect
         let (mut websocket_client, websocket_driver) = self
             .rt
-            .block_on(WebSocketClient::new(self.node_addr.clone()))?;
+            .block_on(WebSocketClient::new(self.node_addr.clone()))
+            .map_err(Error::ClientCreationFailed)?;
 
         let mut websocket_driver_handle = self.rt.spawn(websocket_driver.run());
 
@@ -144,89 +174,89 @@ impl EventMonitor {
             &mut websocket_driver_handle,
         );
 
-        debug!("Reconnected");
+        warn!("reconnected to WebSocket endpoint: {}", self.node_addr);
 
         // Shut down previous client
-        debug!("Gracefully shutting down previous client");
+        debug!("gracefully shutting down previous client");
 
         if let Err(e) = websocket_client.close() {
-            error!("Previous websocket client closing failure {}", e);
+            error!("previous websocket client closing failure {}", e);
         }
 
-        self.rt.block_on(websocket_driver_handle).map_err(|e| {
-            tendermint_rpc::Error::client_internal_error(format!(
-                "failed to terminate previous WebSocket client driver: {}",
-                e
-            ))
-        })??;
+        let result = self
+            .rt
+            .block_on(websocket_driver_handle)
+            .map_err(|e| Error::ClientTerminationFailed(Arc::new(e)))?;
 
-        Ok(())
+        debug!("previous client successfully shutdown");
+
+        result.map_err(Error::ClientCompletionFailed)
     }
 
     /// Try to resubscribe to events
-    fn try_resubscribe(&mut self) -> Result<(), BoxError> {
+    fn try_resubscribe(&mut self) -> Result<(), Error> {
+        warn!("trying to resubscribe to events");
+
         self.subscribe()
     }
 
     /// Event monitor loop
     pub fn run(mut self) {
-        info!(chain.id = %self.chain_id, "running listener");
+        info!(chain.id = %self.chain_id, "starting event monitor");
 
         loop {
             match self.collect_events() {
-                Ok(_) => continue,
-                Err(err) => {
-                    debug!("Web socket error: {}", err);
+                Ok(batches) => self.process_batches(batches).unwrap_or_else(|e| {
+                    error!("failed to process event batch: {}", e);
+                }),
+                Err(e) => {
+                    error!("failed to collect events: {}", e);
 
                     // Try to reconnect
                     self.try_reconnect().unwrap_or_else(|e| {
-                        debug!("Error on reconnecting: {}", e);
-                        panic!("Abort during reconnection");
+                        error!("error on reconnecting: {}", e);
                     });
 
                     // Try to resubscribe
                     self.try_resubscribe().unwrap_or_else(|e| {
-                        debug!("Error on reconnecting: {}", e);
-                        panic!("Abort during reconnection");
+                        error!("error on reconnecting: {}", e);
                     });
                 }
             }
         }
     }
 
     /// Collect the IBC events from the subscriptions
-    fn collect_events(&mut self) -> Result<(), BoxError> {
-        let event = self.rt.block_on(self.subscriptions.next());
-
-        match event {
-            Some(Ok(event)) => {
-                match crate::event::rpc::get_all_events(&self.chain_id, event.clone()) {
-                    Ok(ibc_events) => {
-                        let events_by_height = ibc_events.into_iter().into_group_map();
-
-                        for (height, events) in events_by_height {
-                            let batch = EventBatch {
-                                chain_id: self.chain_id.clone(),
-                                height,
-                                events,
-                            };
-                            self.tx_batch.send(batch)?;
-                        }
-                    }
-                    Err(err) => {
-                        error!(
-                            "Error {} when extracting IBC events from {:?}: ",
-                            err, event
-                        );
-                    }
-                }
-            }
-            Some(Err(err)) => {
-                error!("Error on collecting events from subscriptions: {}", err);
-            }
-            None => (), // no events available
+    fn process_batches(&self, batches: Vec<EventBatch>) -> Result<(), Error> {
+        for batch in batches {
+            self.tx_batch
+                .send(batch)
+                .map_err(|_| Error::ChannelSendFailed)?;
         }
 
         Ok(())
     }
+
+    /// Collect the IBC events from the subscriptions
+    fn collect_events(&mut self) -> Result<Vec<EventBatch>, Error> {
+        if let Some(event) = self.rt.block_on(self.subscriptions.next()) {
+            let event = event.map_err(Error::NextEventBatchFailed)?;
+            let ibc_events = crate::event::rpc::get_all_events(&self.chain_id, event)
+                .map_err(Error::CollectEventsFailed)?;
+
+            let events_by_height = ibc_events.into_iter().into_group_map();
+            let batches = events_by_height
+                .into_iter()
+                .map(|(height, events)| EventBatch {
+                    chain_id: self.chain_id.clone(),
+                    height,
+                    events,
+                })
+                .collect();
+
+            Ok(batches)
+        } else {
+            Ok(vec![])
+        }
+    }
 }
```

### relayer/src/link.rs
```diff
@@ -31,37 +31,40 @@ use ibc_proto::ibc::core::channel::v1::{
     QueryPacketCommitmentsRequest, QueryUnreceivedAcksRequest, QueryUnreceivedPacketsRequest,
 };
 
-use crate::chain::handle::ChainHandle;
 use crate::channel::{Channel, ChannelError, ChannelSide};
 use crate::connection::ConnectionError;
 use crate::error::Error;
 use crate::event::monitor::EventBatch;
 use crate::foreign_client::{ForeignClient, ForeignClientError};
 use crate::relay::MAX_ITER;
+use crate::{chain::handle::ChainHandle, transfer::PacketError};
 use ibc::events::VecIbcEvents;
 
 #[derive(Debug, Error)]
 pub enum LinkError {
     #[error("failed with underlying error: {0}")]
     Failed(String),
 
+    #[error("failed with underlying error: {0}")]
+    Generic(#[from] Error),
+
     #[error("failed to construct packet proofs for chain {0} with error: {1}")]
     PacketProofsConstructor(ChainId, Error),
 
     #[error("failed during query to chain id {0} with underlying error: {1}")]
     QueryError(ChainId, Error),
 
-    #[error("ConnectionError: {0}:")]
+    #[error("connection error: {0}:")]
     ConnectionError(#[from] ConnectionError),
 
-    #[error("ChannelError:  {0}:")]
+    #[error("channel error:  {0}:")]
     ChannelError(#[from] ChannelError),
 
-    #[error("Failed during a client operation: {0}:")]
+    #[error("failed during a client operation: {0}:")]
     ClientError(ForeignClientError),
 
-    #[error("PacketError: {0}:")]
-    PacketError(#[from] Error),
+    #[error("packet error: {0}:")]
+    PacketError(#[from] PacketError),
 
     #[error("clearing of old packets failed")]
     OldPacketClearingFailed,
```

### relayer/src/supervisor.rs
```diff
@@ -7,7 +7,7 @@ use std::{
 
 use anomaly::BoxError;
 use crossbeam_channel::{Receiver, Sender};
-use tracing::{debug, error, info, trace, warn};
+use tracing::{debug, error, error_span, info, trace, warn};
 
 use ibc::events::VecIbcEvents;
 use ibc::ics02_client::client_state::{ClientState, IdentifiedAnyClientState};
@@ -25,12 +25,13 @@ use ibc::{
     ics24_host::identifier::{ChainId, ChannelId, PortId},
     Height,
 };
+
 use ibc_proto::ibc::core::channel::v1::QueryChannelsRequest;
 
-use crate::foreign_client::{ForeignClient, ForeignClientError, MisbehaviourResults};
 use crate::{
     chain::handle::ChainHandle,
     event::monitor::EventBatch,
+    foreign_client::{ForeignClient, ForeignClientError, MisbehaviourResults},
     link::{Link, LinkParameters},
 };
 use ibc::ics03_connection::connection::IdentifiedConnectionEnd;
@@ -402,15 +403,19 @@ impl Worker {
 
     /// Run the worker event loop.
     fn run(self, object: Object) {
-        let result = match object.clone() {
+        let span = error_span!("worker loop", worker = %self);
+        let _guard = span.enter();
+
+        let result = match object {
             Object::UnidirectionalChannelPath(path) => self.run_uni_chan_path(path),
             Object::Client(client) => self.run_client(client),
         };
 
         if let Err(e) = result {
-            error!("[{}] worker error: {}", object.short_name(), e);
+            error!("worker error: {}", e);
         }
-        info!("[{}] worker exits", object.short_name());
+
+        info!("worker exits");
     }
 
     fn run_client_misbehaviour(
@@ -447,16 +452,17 @@ impl Worker {
         );
 
         info!(
-            "[{}] running client worker initial misbehaviour detection for {}",
-            self, client
+            "running client worker & initial misbehaviour detection for {}",
+            client
         );
         // initial check for evidence of misbehaviour for all updates
         let skip_misbehaviour = self.run_client_misbehaviour(&client, None);
 
         info!(
-            "[{}] running client worker loop (misbehaviour and refresh) for {}",
-            self, client
+            "running client worker (misbehaviour and refresh) for {}",
+            client
         );
+
         loop {
             thread::sleep(Duration::from_millis(600));
             // Run client refresh, exit only if expired or frozen
@@ -505,8 +511,8 @@ impl Worker {
             if let Ok(cmd) = self.rx.try_recv() {
                 match cmd {
                     WorkerCmd::IbcEvents { batch } => {
+                        // Update scheduled batches.
                         link.a_to_b.update_schedule(batch)?;
-                        // Refresh the scheduled batches and execute any outstanding ones.
                     }
                     WorkerCmd::NewBlock {
                         height,
```
