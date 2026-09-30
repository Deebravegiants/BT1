# [?] chain head listener: Fix race condition

## Summary
Severity: Unknown
Chain: The Graph
Component: graphprotocol/graph-node
Published: 2021-04-11
Source: https://github.com/graphprotocol/graph-node/commit/1fde43723a5ec0111cce794e0744fc380ea0c05b
Type: security-commit

## Details
chain head listener: Fix race condition

## Patch
### chain/ethereum/src/block_stream.rs
```diff
@@ -148,7 +148,7 @@ where
     S: SubgraphStore,
     C: ChainStore,
 {
-    pub async fn new(
+    pub fn new(
         subgraph_store: Arc<S>,
         chain_store: Arc<C>,
         eth_adapter: Arc<dyn EthereumAdapter>,
@@ -166,7 +166,7 @@ where
         BlockStream {
             state: BlockStreamState::BeginReconciliation,
             consecutive_err_count: 0,
-            chain_head_update_stream: chain_store.chain_head_updates().await,
+            chain_head_update_stream: chain_store.chain_head_updates(),
             ctx: BlockStreamContext {
                 subgraph_store,
                 chain_store,
@@ -797,7 +797,7 @@ where
 {
     type Stream = BlockStream<S, B::ChainStore>;
 
-    async fn build(
+    fn build(
         &self,
         logger: Logger,
         deployment_id: SubgraphDeploymentId,
@@ -851,7 +851,6 @@ where
             logger,
             metrics,
         )
-        .await
     }
 }
 
```

### core/src/subgraph/instance_manager.rs
```diff
@@ -501,7 +501,6 @@ where
                 ctx.inputs.include_calls_in_blocks,
                 ctx.block_stream_metrics.clone(),
             )
-            .await
             .map_err(CancelableError::Error)
             .cancelable(&block_stream_canceler, || CancelableError::Cancel)
             .compat();
```

### graph/src/components/ethereum/stream.rs
```diff
@@ -10,12 +10,10 @@ pub enum BlockStreamEvent {
 
 pub trait BlockStream: Stream<Item = BlockStreamEvent, Error = Error> {}
 
-#[async_trait]
-
 pub trait BlockStreamBuilder: Clone + Send + Sync + 'static {
     type Stream: BlockStream + Send + 'static;
 
-    async fn build(
+    fn build(
         &self,
         logger: Logger,
         deployment_id: SubgraphDeploymentId,
```

### graph/src/components/store.rs
```diff
@@ -1277,7 +1277,7 @@ pub trait ChainStore: Send + Sync + 'static {
     fn attempt_chain_head_update(&self, ancestor_count: BlockNumber) -> Result<Vec<H256>, Error>;
 
     /// Subscribe to chain head updates.
-    async fn chain_head_updates(&self) -> ChainHeadUpdateStream;
+    fn chain_head_updates(&self) -> ChainHeadUpdateStream;
 
     /// Get the current head block pointer for this chain.
     /// Any changes to the head block pointer will be to a block with a larger block number, never
```

### graph/src/lib.rs
```diff
@@ -31,6 +31,7 @@ pub use task_spawn::{
 };
 
 pub use bytes;
+pub use parking_lot;
 pub use prometheus;
 pub use semver;
 pub use stable_hash;
```

### mock/src/block_stream.rs
```diff
@@ -44,11 +44,10 @@ impl MockBlockStreamBuilder {
     }
 }
 
-#[async_trait]
 impl BlockStreamBuilder for MockBlockStreamBuilder {
     type Stream = MockBlockStream;
 
-    async fn build(
+    fn build(
         &self,
         _logger: Logger,
         _deployment_id: SubgraphDeploymentId,
```

### mock/src/store.rs
```diff
@@ -33,7 +33,7 @@ mock! {
 
         fn attempt_chain_head_update(&self, ancestor_count: BlockNumber) -> Result<Vec<H256>, Error>;
 
-        async fn chain_head_updates(&self) -> ChainHeadUpdateStream;
+        fn chain_head_updates(&self) -> ChainHeadUpdateStream;
 
         fn chain_head_ptr(&self) -> Result<Option<EthereumBlockPointer>, Error>;
 
```

### store/postgres/src/chain_head_listener.rs
```diff
@@ -1,8 +1,9 @@
+use graph::parking_lot::Mutex;
 use std::collections::BTreeMap;
 
 use diesel::RunQueryDsl;
 use lazy_static::lazy_static;
-use tokio::sync::{mpsc::Receiver, watch, RwLock};
+use tokio::sync::{mpsc::Receiver, watch};
 
 use crate::{
     connection_pool::ConnectionPool,
@@ -37,7 +38,7 @@ impl Watcher {
 
 pub struct ChainHeadUpdateListener {
     /// Update watchers keyed by network.
-    watchers: Arc<RwLock<BTreeMap<String, Watcher>>>,
+    watchers: Arc<Mutex<BTreeMap<String, Watcher>>>,
     _listener: NotificationListener,
 }
 
@@ -56,7 +57,7 @@ impl ChainHeadUpdateListener {
         // Create a Postgres notification listener for chain head updates
         let (mut listener, receiver) =
             NotificationListener::new(&logger, postgres_url, CHANNEL_NAME.clone());
-        let watchers = Arc::new(RwLock::new(BTreeMap::new()));
+        let watchers = Arc::new(Mutex::new(BTreeMap::new()));
 
         Self::listen(
             logger,
@@ -81,7 +82,7 @@ impl ChainHeadUpdateListener {
         metrics: Arc<BlockIngestorMetrics>,
         listener: &mut NotificationListener,
         mut receiver: Receiver<JsonNotification>,
-        watchers: Arc<RwLock<BTreeMap<String, Watcher>>>,
+        watchers: Arc<Mutex<BTreeMap<String, Watcher>>>,
     ) {
         // Process chain head updates in a dedicated task
         graph::spawn(async move {
@@ -106,7 +107,7 @@ impl ChainHeadUpdateListener {
                     .set_chain_head_number(&update.network_name, *&update.head_block_number as i64);
 
                 // If there are subscriptions for this network, notify them.
-                if let Some(watcher) = watchers.read().await.get(&update.network_name) {
+                if let Some(watcher) = watchers.lock().get(&update.network_name) {
                     watcher.send()
                 }
             }
@@ -116,23 +117,14 @@ impl ChainHeadUpdateListener {
         listener.start();
     }
 
-    pub async fn subscribe(&self, network_name: String) -> ChainHeadUpdateStream {
-        let update_receiver = {
-            let existing = {
-                let watchers = self.watchers.read().await;
-                watchers.get(&network_name).map(|w| w.receiver.clone())
-            };
-
-            if let Some(watcher) = existing {
-                watcher
-            } else {
-                // This is the first subscription for this network, a write lock is required.
-                let watcher = Watcher::new();
-                let receiver = watcher.receiver.clone();
-                self.watchers.write().await.insert(network_name, watcher);
-                receiver
-            }
-        };
+    pub fn subscribe(&self, network_name: String) -> ChainHeadUpdateStream {
+        let update_receiver = self
+            .watchers
+            .lock()
+            .entry(network_name)
+            .or_insert_with(|| Watcher::new())
+            .receiver
+            .clone();
 
         Box::new(
             WatchStream::new(update_receiver)
```

### store/postgres/src/chain_store.rs
```diff
@@ -1235,10 +1235,9 @@ impl ChainStoreTrait for ChainStore {
         Ok(missing)
     }
 
-    async fn chain_head_updates(&self) -> ChainHeadUpdateStream {
+    fn chain_head_updates(&self) -> ChainHeadUpdateStream {
         self.chain_head_update_listener
             .subscribe(self.chain.to_owned())
-            .await
     }
 
     fn chain_head_ptr(&self) -> Result<Option<EthereumBlockPointer>, Error> {
```
