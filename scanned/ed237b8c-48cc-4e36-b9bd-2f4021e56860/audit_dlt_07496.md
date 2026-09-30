# [?] fix(client): panic on executor lock

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2024-11-01
Source: https://github.com/fedimint/fedimint/commit/f123eb48866f7c474f22040ace16c2dc7a3cbdd6
Type: security-commit

## Details
fix(client): panic on executor lock

```
fedimint-test-all-wasm32-unknown-unknown-ci> 00:00:33 thread 'sends_ecash_out_of_band' panicked at fedimint-client/src/sm/executor.rs:814:14:
fedimint-test-all-wasm32-unknown-unknown-ci> 00:00:33 Only locked during startup, no collisions should be possible: TryLockError(())
fedimint-test-all-wasm32-unknown-unknown-ci> 00:00:33 note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
```

https://github.com/fedimint/fedimint/actions/runs/11634629737/job/32402260832?pr=6264

There seem to be no reason to have an async lock there, all the locking
is wrapping only non-blocking/non-async operations anyway.

## Patch
### fedimint-client/src/lib.rs
```diff
@@ -699,8 +699,8 @@ impl ClientHandle {
         self.inner.as_ref().expect("Inner always set")
     }
 
-    pub async fn start_executor(&self) {
-        self.as_inner().start_executor().await;
+    pub fn start_executor(&self) {
+        self.as_inner().start_executor();
     }
 
     /// Shutdown the client.
@@ -1032,12 +1032,12 @@ impl Client {
         Self::get_config_from_db(db).await.is_some()
     }
 
-    pub async fn start_executor(self: &Arc<Self>) {
+    pub fn start_executor(self: &Arc<Self>) {
         debug!(
             "Starting fedimint client executor (version: {})",
             fedimint_build_code_version_env!()
         );
-        self.executor.start_executor(self.context_gen()).await;
+        self.executor.start_executor(self.context_gen());
     }
 
     pub fn federation_id(&self) -> FederationId {
@@ -2652,7 +2652,7 @@ impl ClientBuilder {
             )
             .await?;
         if !stopped {
-            client.as_inner().start_executor().await;
+            client.as_inner().start_executor();
         }
         Ok(client)
     }
@@ -2675,7 +2675,7 @@ impl ClientBuilder {
             )
             .await?;
         if !stopped {
-            client.as_inner().start_executor().await;
+            client.as_inner().start_executor();
         }
 
         Ok(client)
```

### fedimint-client/src/sm/executor.rs
```diff
@@ -22,7 +22,7 @@ use fedimint_logging::LOG_CLIENT_REACTOR;
 use futures::future::{self, select_all};
 use futures::stream::{FuturesUnordered, StreamExt};
 use tokio::select;
-use tokio::sync::{mpsc, oneshot, Mutex};
+use tokio::sync::{mpsc, oneshot};
 use tracing::{debug, error, info, trace, warn, Instrument};
 
 use super::state::StateTransitionFunction;
@@ -59,7 +59,7 @@ pub struct Executor {
 
 struct ExecutorInner {
     db: Database,
-    state: Mutex<ExecutorState>,
+    state: std::sync::RwLock<ExecutorState>,
     module_contexts: BTreeMap<ModuleInstanceId, DynContext>,
     valid_module_ids: BTreeSet<ModuleInstanceId>,
     notifier: Notifier,
@@ -231,8 +231,8 @@ impl Executor {
                 let context = self
                     .inner
                     .state
-                    .lock()
-                    .await
+                    .read()
+                    .unwrap()
                     .gen_context(&state)
                     .expect("executor should be running at this point");
 
@@ -342,9 +342,13 @@ impl Executor {
     ///
     /// ## Panics
     /// If called more than once.
-    pub async fn start_executor(&self, context_gen: ContextGen) {
-        let Some((shutdown_receiver, sm_update_rx)) =
-            self.inner.state.lock().await.start(context_gen.clone())
+    pub fn start_executor(&self, context_gen: ContextGen) {
+        let Some((shutdown_receiver, sm_update_rx)) = self
+            .inner
+            .state
+            .write()
+            .expect("locking can't fail")
+            .start(context_gen.clone())
         else {
             panic!("start_executor was called previously");
         };
@@ -812,10 +816,7 @@ impl ExecutorInner {
 impl ExecutorInner {
     /// See [`Executor::stop_executor`].
     fn stop_executor(&self) -> Option<()> {
-        let mut state = self
-            .state
-            .try_lock()
-            .expect("Only locked during startup, no collisions should be possible");
+        let mut state = self.state.write().expect("Locking can't fail");
 
         state.stop()
     }
@@ -866,7 +867,7 @@ impl ExecutorBuilder {
 
         let inner = Arc::new(ExecutorInner {
             db,
-            state: Mutex::new(ExecutorState::Unstarted { sm_update_rx }),
+            state: std::sync::RwLock::new(ExecutorState::Unstarted { sm_update_rx }),
             module_contexts: self.module_contexts,
             valid_module_ids: self.valid_module_ids,
             notifier,
@@ -1354,7 +1355,7 @@ mod tests {
         const KIND: Option<ModuleKind> = None;
     }
 
-    async fn get_executor() -> (Executor, Sender<u64>, Database) {
+    fn get_executor() -> (Executor, Sender<u64>, Database) {
         let (broadcast, _) = tokio::sync::broadcast::channel(10);
 
         let mut decoder_builder = Decoder::builder();
@@ -1374,9 +1375,7 @@ mod tests {
         );
         let executor =
             executor_builder.build(db.clone(), Notifier::new(db.clone()), TaskGroup::new());
-        executor
-            .start_executor(Arc::new(|_, _| DynGlobalClientContext::new_fake()))
-            .await;
+        executor.start_executor(Arc::new(|_, _| DynGlobalClientContext::new_fake()));
 
         info!("Initialized test executor");
         (executor, broadcast, db)
@@ -1388,7 +1387,7 @@ mod tests {
         const MOCK_INSTANCE_1: ModuleInstanceId = 42;
         const MOCK_INSTANCE_2: ModuleInstanceId = 21;
 
-        let (executor, sender, _db) = get_executor().await;
+        let (executor, sender, _db) = get_executor();
         executor
             .add_state_machines(vec![DynState::from_typed(
                 MOCK_INSTANCE_1,
```

### fedimint-wasm-tests/src/lib.rs
```diff
@@ -148,7 +148,7 @@ mod tests {
     #[wasm_bindgen_test]
     async fn receive() -> Result<()> {
         let client = client(&faucet::invite_code().await?.parse()?).await?;
-        client.start_executor().await;
+        client.start_executor();
         let ln_gateway = get_gateway(&client).await?;
         futures::future::try_join_all(
             (0..10)
@@ -243,7 +243,7 @@ mod tests {
     #[wasm_bindgen_test]
     async fn receive_and_pay() -> Result<()> {
         let client = client(&faucet::invite_code().await?.parse()?).await?;
-        client.start_executor().await;
+        client.start_executor();
         let ln_gateway = get_gateway(&client).await?;
 
         futures::future::try_join_all(
@@ -327,7 +327,7 @@ mod tests {
     #[wasm_bindgen_test]
     async fn test_ecash() -> Result<()> {
         let client = client(&faucet::invite_code().await?.parse()?).await?;
-        client.start_executor().await;
+        client.start_executor();
         let ln_gateway = get_gateway(&client).await?;
 
         futures::future::try_join_all(
@@ -343,7 +343,7 @@ mod tests {
     #[wasm_bindgen_test]
     async fn test_ecash_exact() -> Result<()> {
         let client = client(&faucet::invite_code().await?.parse()?).await?;
-        client.start_executor().await;
+        client.start_executor();
         let ln_gateway = get_gateway(&client).await?;
 
         receive_once(client.clone(), Amount::from_sats(100), ln_gateway).await?;
```
