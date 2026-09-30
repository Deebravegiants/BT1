# [?] Prevent race condition when updating the workers after config reload (#1173)

## Summary
Severity: Unknown
Chain: Cosmos
Component: informalsystems/hermes
Published: 2021-07-12
Source: https://github.com/informalsystems/hermes/commit/ce363918aad43c84367e6f5f0d07e2682e5fd831
Type: security-commit

## Details
Prevent race condition when updating the workers after config reload (#1173)

This PR fixes a bug where the supervisor would attempt to shutdown a worker
that had already been shutdown and replaced with a new worker. As the new worker was not
instructed to shutdown, the supervisor would hang waiting for it to exit.

In more details:

- Say we have a packet worker A for object O between ibc-0 and ibc-1
- After updating the config of ibc-0, we trigger a config reload
- The supervisor first shuts down worker A, and waits for its event loop to exit
- Worker A exits, and sends a `Stopped(O)` message to the supervisor
- The supervisor now spawns a new worker B for object O
- The supervisor now processes the `Stopped(O)` message previously sent by worker A,
   and waits for the worker associated with object O, ie. now worker B, to finish
- As worker B has never been instructed to shutdown, nor should it, the supervisor hangs
  waiting for it to exit.

This PR solves this issue by:
- introducing unique identifiers for each worker (currently an incrementing `u64`)
- sending the worker id alongside the object in the `Stopped` message
- only acting on worker `ID` when receiving a `Stopped(ID, OBJECT)` message

Additionally, the `SIGUSR1` signal will now also show the worker's ids when dumping the supervisor state.

## Patch
### relayer/src/supervisor.rs
```diff
@@ -1,5 +1,5 @@
 use std::{
-    collections::{BTreeMap, HashMap},
+    collections::HashMap,
     sync::{Arc, RwLock},
     time::Duration,
 };
@@ -412,19 +412,9 @@ impl Supervisor {
     /// Dump the state of the supervisor into a [`SupervisorState`] value,
     /// and send it back through the given channel.
     fn dump_state(&self, reply_to: Sender<SupervisorState>) -> CmdEffect {
-        let mut chains = self.registry.chains().map(|c| c.id()).collect_vec();
-        chains.sort();
-
-        let workers = self
-            .workers
-            .objects()
-            .cloned()
-            .into_group_map_by(|o| o.object_type())
-            .into_iter()
-            .update(|(_, os)| os.sort_by_key(Object::short_name))
-            .collect::<BTreeMap<_, _>>();
-
-        let _ = reply_to.try_send(SupervisorState::new(chains, workers));
+        let chains = self.registry.chains().map(|c| c.id()).collect_vec();
+        let state = SupervisorState::new(chains, self.workers.objects());
+        let _ = reply_to.try_send(state);
 
         CmdEffect::Nothing
     }
@@ -533,8 +523,8 @@ impl Supervisor {
     /// Process the given [`WorkerMsg`] sent by a worker.
     fn handle_worker_msg(&mut self, msg: WorkerMsg) {
         match msg {
-            WorkerMsg::Stopped(object) => {
-                self.workers.remove_stopped(&object);
+            WorkerMsg::Stopped(id, object) => {
+                self.workers.remove_stopped(id, object);
             }
         }
     }
```

### relayer/src/supervisor/dump_state.rs
```diff
@@ -5,16 +5,43 @@ use itertools::Itertools;
 use serde::{Deserialize, Serialize};
 use tracing::info;
 
-use crate::object::{Object, ObjectType};
+use crate::{
+    object::{Object, ObjectType},
+    worker::WorkerId,
+};
+
+#[derive(Clone, Debug, Serialize, Deserialize)]
+pub struct WorkerDesc {
+    pub id: WorkerId,
+    pub object: Object,
+}
+
+impl WorkerDesc {
+    pub fn new(id: WorkerId, object: Object) -> Self {
+        Self { id, object }
+    }
+}
 
 #[derive(Clone, Debug, Default, Serialize, Deserialize)]
 pub struct SupervisorState {
     pub chains: Vec<ChainId>,
-    pub workers: BTreeMap<ObjectType, Vec<Object>>,
+    pub workers: BTreeMap<ObjectType, Vec<WorkerDesc>>,
 }
 
 impl SupervisorState {
-    pub fn new(chains: Vec<ChainId>, workers: BTreeMap<ObjectType, Vec<Object>>) -> Self {
+    pub fn new<'a>(
+        mut chains: Vec<ChainId>,
+        workers: impl Iterator<Item = (WorkerId, &'a Object)>,
+    ) -> Self {
+        chains.sort();
+
+        let workers = workers
+            .map(|(id, o)| WorkerDesc::new(id, o.clone()))
+            .into_group_map_by(|desc| desc.object.object_type())
+            .into_iter()
+            .update(|(_, os)| os.sort_by_key(|desc| desc.object.short_name()))
+            .collect::<BTreeMap<_, _>>();
+
         Self { chains, workers }
     }
 
@@ -31,8 +58,8 @@ impl fmt::Display for SupervisorState {
         writeln!(f, "* Chains: {}", self.chains.iter().join(", "))?;
         for (tpe, objects) in &self.workers {
             writeln!(f, "* {:?} workers:", tpe)?;
-            for object in objects {
-                writeln!(f, "  - {}", object.short_name())?;
+            for desc in objects {
+                writeln!(f, "  - {} (id: {})", desc.object.short_name(), desc.id)?;
             }
         }
 
```

### relayer/src/worker.rs
```diff
@@ -1,6 +1,7 @@
 use std::fmt;
 
 use crossbeam_channel::Sender;
+use serde::{Deserialize, Serialize};
 use tracing::{debug, error, info};
 
 use crate::{chain::handle::ChainHandlePair, config::Config, object::Object, telemetry::Telemetry};
@@ -28,17 +29,37 @@ pub use channel::ChannelWorker;
 mod uni_chan_path;
 pub use uni_chan_path::PacketWorker;
 
+#[derive(Copy, Clone, Debug, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
+#[serde(transparent)]
+pub struct WorkerId(u64);
+
+impl WorkerId {
+    pub fn new(id: u64) -> Self {
+        Self(id)
+    }
+
+    pub fn next(self) -> Self {
+        Self(self.0 + 1)
+    }
+}
+
+impl fmt::Display for WorkerId {
+    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
+        write!(f, "{}", self.0)
+    }
+}
+
 #[derive(Clone, Debug, PartialEq, Eq)]
 pub enum WorkerMsg {
-    Stopped(Object),
+    Stopped(WorkerId, Object),
 }
 
 /// A worker processes batches of events associated with a given [`Object`].
 pub enum Worker {
-    Client(ClientWorker),
-    Connection(ConnectionWorker),
-    Channel(ChannelWorker),
-    Packet(PacketWorker),
+    Client(WorkerId, ClientWorker),
+    Connection(WorkerId, ConnectionWorker),
+    Channel(WorkerId, ChannelWorker),
+    Packet(WorkerId, PacketWorker),
 }
 
 impl fmt::Display for Worker {
@@ -51,6 +72,7 @@ impl Worker {
     /// Spawn a worker which relays events pertaining to an [`Object`] between two `chains`.
     pub fn spawn(
         chains: ChainHandlePair,
+        id: WorkerId,
         object: Object,
         msg_tx: Sender<WorkerMsg>,
         telemetry: Telemetry,
@@ -60,46 +82,53 @@ impl Worker {
 
         debug!("spawning worker for object {}", object.short_name(),);
 
-        let worker = match object {
-            Object::Client(client) => {
-                Self::Client(ClientWorker::new(client, chains, cmd_rx, telemetry))
-            }
-            Object::Connection(connection) => {
-                Self::Connection(ConnectionWorker::new(connection, chains, cmd_rx, telemetry))
-            }
-            Object::Channel(channel) => {
-                Self::Channel(ChannelWorker::new(channel, chains, cmd_rx, telemetry))
-            }
-            Object::Packet(path) => Self::Packet(PacketWorker::new(
-                path,
-                chains,
-                cmd_rx,
-                telemetry,
-                config.global.clear_packets_interval,
-            )),
+        let worker = match &object {
+            Object::Client(client) => Self::Client(
+                id,
+                ClientWorker::new(client.clone(), chains, cmd_rx, telemetry),
+            ),
+            Object::Connection(connection) => Self::Connection(
+                id,
+                ConnectionWorker::new(connection.clone(), chains, cmd_rx, telemetry),
+            ),
+            Object::Channel(channel) => Self::Channel(
+                id,
+                ChannelWorker::new(channel.clone(), chains, cmd_rx, telemetry),
+            ),
+            Object::Packet(path) => Self::Packet(
+                id,
+                PacketWorker::new(
+                    path.clone(),
+                    chains,
+                    cmd_rx,
+                    telemetry,
+                    config.global.clear_packets_interval,
+                ),
+            ),
         };
 
         let thread_handle = std::thread::spawn(move || worker.run(msg_tx));
-        WorkerHandle::new(cmd_tx, thread_handle)
+        WorkerHandle::new(id, object, cmd_tx, thread_handle)
     }
 
     /// Run the worker event loop.
     fn run(self, msg_tx: Sender<WorkerMsg>) {
+        let id = self.id();
         let object = self.object();
-        let name = object.short_name();
+        let name = format!("{}#{}", object.short_name(), id);
 
         let result = match self {
-            Self::Client(w) => w.run(),
-            Self::Connection(w) => w.run(),
-            Self::Channel(w) => w.run(),
-            Self::Packet(w) => w.run(),
+            Self::Client(_, w) => w.run(),
+            Self::Connection(_, w) => w.run(),
+            Self::Channel(_, w) => w.run(),
+            Self::Packet(_, w) => w.run(),
         };
 
         if let Err(e) = result {
             error!("[{}] worker aborted with error: {}", name, e);
         }
 
-        if let Err(e) = msg_tx.send(WorkerMsg::Stopped(object)) {
+        if let Err(e) = msg_tx.send(WorkerMsg::Stopped(id, object)) {
             error!(
                 "[{}] failed to notify supervisor that worker stopped: {}",
                 name, e
@@ -109,21 +138,30 @@ impl Worker {
         info!("[{}] worker stopped", name);
     }
 
+    fn id(&self) -> WorkerId {
+        match self {
+            Self::Client(id, _) => *id,
+            Self::Connection(id, _) => *id,
+            Self::Channel(id, _) => *id,
+            Self::Packet(id, _) => *id,
+        }
+    }
+
     fn chains(&self) -> &ChainHandlePair {
         match self {
-            Self::Client(w) => &w.chains(),
-            Self::Connection(w) => w.chains(),
-            Self::Channel(w) => w.chains(),
-            Self::Packet(w) => w.chains(),
+            Self::Client(_, w) => &w.chains(),
+            Self::Connection(_, w) => w.chains(),
+            Self::Channel(_, w) => w.chains(),
+            Self::Packet(_, w) => w.chains(),
         }
     }
 
     fn object(&self) -> Object {
         match self {
-            Worker::Client(w) => w.object().clone().into(),
-            Worker::Connection(w) => w.object().clone().into(),
-            Worker::Channel(w) => w.object().clone().into(),
-            Worker::Packet(w) => w.object().clone().into(),
+            Worker::Client(_, w) => w.object().clone().into(),
+            Worker::Connection(_, w) => w.object().clone().into(),
+            Worker::Channel(_, w) => w.object().clone().into(),
+            Worker::Packet(_, w) => w.object().clone().into(),
         }
     }
 }
```

### relayer/src/worker/client.rs
```diff
@@ -85,16 +85,17 @@ impl ClientWorker {
             }
 
             if let Ok(cmd) = self.cmd_rx.try_recv() {
-                if self.process_cmd(cmd, &client) {
-                    break;
-                }
+                match self.process_cmd(cmd, &client) {
+                    Next::Continue => continue,
+                    Next::Abort => break,
+                };
             }
         }
 
         Ok(())
     }
 
-    fn process_cmd(&self, cmd: WorkerCmd, client: &ForeignClient) -> bool {
+    fn process_cmd(&self, cmd: WorkerCmd, client: &ForeignClient) -> Next {
         match cmd {
             WorkerCmd::IbcEvents { batch } => {
                 trace!("[{}] worker received batch: {:?}", client, batch);
@@ -117,10 +118,10 @@ impl ClientWorker {
                     }
                 }
 
-                false
+                Next::Continue
             }
-            WorkerCmd::Shutdown => true,
-            WorkerCmd::NewBlock { .. } => false,
+            WorkerCmd::Shutdown => Next::Abort,
+            WorkerCmd::NewBlock { .. } => Next::Continue,
         }
     }
 
@@ -153,3 +154,8 @@ impl ClientWorker {
         &self.client
     }
 }
+
+pub enum Next {
+    Abort,
+    Continue,
+}
```

### relayer/src/worker/handle.rs
```diff
@@ -11,25 +11,40 @@ use ibc::{
     events::IbcEvent, ics02_client::events::NewBlock, ics24_host::identifier::ChainId, Height,
 };
 
-use crate::event::monitor::EventBatch;
+use crate::{event::monitor::EventBatch, object::Object};
 
-use super::WorkerCmd;
+use super::{WorkerCmd, WorkerId};
 
 /// Handle to a [`Worker`], for sending [`WorkerCmd`]s to it.
 pub struct WorkerHandle {
+    id: WorkerId,
+    object: Object,
     tx: Sender<WorkerCmd>,
     thread_handle: JoinHandle<()>,
 }
 
 impl fmt::Debug for WorkerHandle {
     fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
-        f.debug_struct("WorkerHandle").finish()
+        f.debug_struct("WorkerHandle")
+            .field("id", &self.id)
+            .field("object", &self.object)
+            .finish_non_exhaustive()
     }
 }
 
 impl WorkerHandle {
-    pub fn new(tx: Sender<WorkerCmd>, thread_handle: JoinHandle<()>) -> Self {
-        Self { tx, thread_handle }
+    pub fn new(
+        id: WorkerId,
+        object: Object,
+        tx: Sender<WorkerCmd>,
+        thread_handle: JoinHandle<()>,
+    ) -> Self {
+        Self {
+            id,
+            object,
+            tx,
+            thread_handle,
+        }
     }
 
     /// Send a batch of events to the worker.
@@ -45,7 +60,6 @@ impl WorkerHandle {
             events,
         };
 
-        trace!("supervisor sends {:?}", batch);
         self.tx.send(WorkerCmd::IbcEvents { batch })?;
         Ok(())
     }
@@ -64,6 +78,19 @@ impl WorkerHandle {
 
     /// Wait for the worker thread to finish.
     pub fn join(self) -> thread::Result<()> {
-        self.thread_handle.join()
+        trace!(worker = %self.object.short_name(), "worker::handle: waiting for worker loop to end");
+        let res = self.thread_handle.join();
+        trace!(worker = %self.object.short_name(), "worker::handle: waiting for worker loop to end: done");
+        res
+    }
+
+    /// Get the worker's id.
+    pub fn id(&self) -> WorkerId {
+        self.id
+    }
+
+    /// Get a reference to the worker's object.
+    pub fn object(&self) -> &Object {
+        &self.object
     }
 }
```

### relayer/src/worker/map.rs
```diff
@@ -3,7 +3,7 @@ use std::collections::HashMap;
 use crossbeam_channel::Sender;
 
 use ibc::ics24_host::identifier::ChainId;
-use tracing::{debug, warn};
+use tracing::{debug, trace, warn};
 
 use crate::{
     chain::handle::{ChainHandle, ChainHandlePair},
@@ -13,12 +13,13 @@ use crate::{
     telemetry::Telemetry,
 };
 
-use super::{Worker, WorkerHandle, WorkerMsg};
+use super::{Worker, WorkerHandle, WorkerId, WorkerMsg};
 
 /// Manage the lifecycle of [`Worker`]s associated with [`Object`]s.
 #[derive(Debug)]
 pub struct WorkerMap {
     workers: HashMap<Object, WorkerHandle>,
+    latest_worker_id: WorkerId,
     msg_tx: Sender<WorkerMsg>,
     telemetry: Telemetry,
 }
@@ -29,6 +30,7 @@ impl WorkerMap {
     pub fn new(msg_tx: Sender<WorkerMsg>, telemetry: Telemetry) -> Self {
         Self {
             workers: HashMap::new(),
+            latest_worker_id: WorkerId::new(0),
             msg_tx,
             telemetry,
         }
@@ -41,13 +43,46 @@ impl WorkerMap {
 
     /// Remove the [`Worker`] associated with the given [`Object`] from
     /// the map and wait for its thread to terminate.
-    pub fn remove_stopped(&mut self, object: &Object) -> bool {
-        if let Some(handle) = self.workers.remove(object) {
-            telemetry!(self.telemetry.worker(metric_type(object), -1));
-            let _ = handle.join();
-            true
-        } else {
-            false
+    pub fn remove_stopped(&mut self, id: WorkerId, object: Object) -> bool {
+        match self.workers.remove(&object) {
+            Some(handle) if handle.id() == id => {
+                telemetry!(self.telemetry.worker(metric_type(&object), -1));
+
+                let id = handle.id();
+
+                trace!(
+                    worker.id = %id, worker.object = %object.short_name(),
+                    "waiting for worker loop to end"
+                );
+
+                let _ = handle.join();
+
+                trace!(
+                    worker.id = %id, worker.object = %object.short_name(),
+                    "worker loop has ended"
+                );
+
+                true
+            }
+            Some(handle) => {
+                debug!(
+                    worker.object = %object.short_name(),
+                    "ignoring attempt to remove worker with outdated id {} (current: {})",
+                    id, handle.id()
+                );
+
+                self.workers.insert(object, handle);
+
+                false
+            }
+            None => {
+                debug!(
+                    worker.object = %object.short_name(),
+                    "ignoring attempt to remove unknown worker",
+                );
+
+                false
+            }
         }
     }
 
@@ -117,13 +152,20 @@ impl WorkerMap {
 
         Worker::spawn(
             ChainHandlePair { a: src, b: dst },
+            self.next_worker_id(),
             object.clone(),
             self.msg_tx.clone(),
             self.telemetry.clone(),
             config,
         )
     }
 
+    fn next_worker_id(&mut self) -> WorkerId {
+        let id = self.latest_worker_id.next();
+        self.latest_worker_id = id;
+        id
+    }
+
     /// List the [`Object`]s for which there is an associated worker
     /// for the given chain.
     pub fn objects_for_chain(&self, chain_id: &ChainId) -> Vec<Object> {
@@ -141,7 +183,7 @@ impl WorkerMap {
 
             match handle.shutdown() {
                 Ok(()) => {
-                    debug!(object = %object.short_name(), "waiting for worker to exit");
+                    trace!(object = %object.short_name(), "waiting for worker to exit");
                     let _ = handle.join();
                 }
                 Err(e) => {
@@ -152,8 +194,10 @@ impl WorkerMap {
     }
 
     /// Get an iterator over the worker map's objects.
-    pub fn objects(&self) -> impl Iterator<Item = &Object> {
-        self.workers.keys()
+    pub fn objects(&self) -> impl Iterator<Item = (WorkerId, &Object)> {
+        self.workers
+            .iter()
+            .map(|(object, handle)| (handle.id(), object))
     }
 }
 
```
