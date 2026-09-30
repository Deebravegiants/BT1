# [?] fix(state-dumper): Fix crash and unkillability on SIGINT (#12892)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2025-02-10
Source: https://github.com/near/nearcore/commit/3ea200f7def5ee3bb10c29f3e0088aa1bf9274cf
Type: security-commit

## Details
fix(state-dumper): Fix crash and unkillability on SIGINT (#12892)

When the state dumper was rewritten, we left the old
actix::Arbiter::new() to start a new thread. This is not because it
makes any sense in the new code, but just because of an oversight. Turns
out the continued usage of an Arbiter in that way was actually not
correct, because when Arbiter::stop() is called, it will exit without
regard for the tasks we spawned. Then we get a crash when
dump_shard_state() drops its `future_spawner` argument, because it's the
last Arc reference to that tokio runtime.

We can fix it by just removing the `dump_future_runner` field of
`StateSyncDumper` and just running the dumper task with the
`future_spawner` we already have, since there's nothing special about w
respect to the other tasks. Then we can make sure to wait for the dumper
to actually exit by waiting for the tasks to finish like in
`check_parts_upload()`, and then blocking until it's done in
`RunCmd::run()`

---------

Co-authored-by: Razvan Barbascu <r.barbascu@gmail.com>

## Patch
### integration-tests/src/test_loop/builder.rs
```diff
@@ -2,7 +2,6 @@ use std::collections::{HashMap, HashSet};
 use std::sync::{Arc, Mutex};
 use tempfile::TempDir;
 
-use near_async::futures::FutureSpawner;
 use near_async::messaging::{noop, IntoMultiSender, IntoSender, LateBoundSender};
 use near_async::test_loop::sender::TestLoopSender;
 use near_async::test_loop::TestLoopV2;
@@ -751,7 +750,6 @@ impl TestLoopBuilder {
         let resharding_actor =
             ReshardingActor::new(runtime_adapter.store().clone(), &chain_genesis);
 
-        let future_spawner = self.test_loop.future_spawner();
         let state_sync_dumper = StateSyncDumper {
             clock: self.test_loop.clock(),
             client_config,
@@ -760,10 +758,6 @@ impl TestLoopBuilder {
             shard_tracker,
             runtime: runtime_adapter,
             validator: validator_signer,
-            dump_future_runner: Box::new(move |future| {
-                future_spawner.spawn_boxed("state_sync_dumper", future);
-                Box::new(|| {})
-            }),
             future_spawner: Arc::new(self.test_loop.future_spawner()),
             handle: None,
         };
```

### integration-tests/src/tests/client/state_dump.rs
```diff
@@ -1,6 +1,6 @@
 use assert_matches::assert_matches;
 
-use near_async::futures::ActixFutureSpawner;
+use near_async::futures::ActixArbiterHandleFutureSpawner;
 use near_async::time::{Clock, Duration};
 use near_chain::near_chain_primitives::error::QueryError;
 use near_chain::{ChainGenesis, ChainStoreAccess, Provenance};
@@ -58,6 +58,8 @@ fn slow_test_state_dump() {
         Some(Arc::new(EmptyValidatorSigner::new("test0".parse().unwrap()))),
         "validator_signer",
     );
+
+    let arbiter = actix::Arbiter::new();
     let mut state_sync_dumper = StateSyncDumper {
         clock: Clock::real(),
         client_config: config,
@@ -66,8 +68,7 @@ fn slow_test_state_dump() {
         shard_tracker,
         runtime,
         validator,
-        dump_future_runner: StateSyncDumper::arbiter_dump_future_runner(),
-        future_spawner: Arc::new(ActixFutureSpawner),
+        future_spawner: Arc::new(ActixArbiterHandleFutureSpawner(arbiter.handle())),
         handle: None,
     };
     state_sync_dumper.start().unwrap();
@@ -164,6 +165,7 @@ fn run_state_sync_with_dumped_parts(
         iteration_delay: Some(Duration::ZERO),
         credentials_file: None,
     });
+    let arbiter = actix::Arbiter::new();
     let mut state_sync_dumper = StateSyncDumper {
         clock: Clock::real(),
         client_config: config.clone(),
@@ -172,8 +174,7 @@ fn run_state_sync_with_dumped_parts(
         shard_tracker,
         runtime,
         validator,
-        dump_future_runner: StateSyncDumper::arbiter_dump_future_runner(),
-        future_spawner: Arc::new(ActixFutureSpawner),
+        future_spawner: Arc::new(ActixArbiterHandleFutureSpawner(arbiter.handle())),
         handle: None,
     };
     state_sync_dumper.start().unwrap();
```

### integration-tests/src/tests/client/sync_state_nodes.rs
```diff
@@ -345,7 +345,7 @@ fn ultra_slow_test_sync_state_dump() {
             let nearcore::NearNode {
                 view_client: view_client1,
                 // State sync dumper should be kept in the scope to avoid dropping it, which stops the state dumper loop.
-                state_sync_dumper: _dumper,
+                mut state_sync_dumper,
                 ..
             } = start_with_config(dir1.path(), near1).expect("start_with_config");
 
@@ -360,6 +360,7 @@ fn ultra_slow_test_sync_state_dump() {
                     let genesis2 = genesis.clone();
 
                     match view_client1.send(GetBlock::latest().with_span_context()).await {
+                        // FIXME: this is not the right check after the sync hash was moved to sync the current epoch's state
                         Ok(Ok(b)) if b.header.height >= genesis.config.epoch_length + 2 => {
                             let mut view_client2_holder2 = view_client2_holder2.write().unwrap();
                             let mut arbiters_holder2 = arbiters_holder2.write().unwrap();
@@ -433,6 +434,7 @@ fn ultra_slow_test_sync_state_dump() {
             })
             .await
             .unwrap();
+            state_sync_dumper.stop_and_await();
             System::current().stop();
         });
         drop(_dump_dir);
```

### nearcore/src/lib.rs
```diff
@@ -439,7 +439,6 @@ pub fn start_with_config_and_synchronization(
         shard_tracker: shard_tracker.clone(),
         runtime,
         validator: config.validator_signer.clone(),
-        dump_future_runner: StateSyncDumper::arbiter_dump_future_runner(),
         future_spawner: state_sync_spawner,
         handle: None,
     };
```

### nearcore/src/state_sync.rs
```diff
@@ -1,9 +1,8 @@
 use crate::metrics;
 
-use actix_rt::Arbiter;
 use anyhow::Context;
 use borsh::BorshSerialize;
-use futures::future::{select_all, BoxFuture};
+use futures::future::select_all;
 use futures::{FutureExt, StreamExt};
 use near_async::futures::{respawn_for_parallelism, FutureSpawner};
 use near_async::time::{Clock, Duration, Interval};
@@ -29,7 +28,7 @@ use rand::thread_rng;
 use std::collections::{HashMap, HashSet};
 use std::i64;
 use std::sync::atomic::{AtomicBool, AtomicI64, Ordering};
-use std::sync::{Arc, RwLock};
+use std::sync::{Arc, Condvar, Mutex, RwLock};
 use tokio::sync::oneshot;
 use tokio::sync::Semaphore;
 
@@ -49,9 +48,8 @@ pub struct StateSyncDumper {
     /// Lock the value of mutable validator signer for the duration of a request to ensure consistency.
     /// Please note that the locked value should not be stored anywhere or passed through the thread boundary.
     pub validator: MutableValidatorSigner,
-    pub dump_future_runner: Box<dyn Fn(BoxFuture<'static, ()>) -> Box<dyn FnOnce()>>,
     pub future_spawner: Arc<dyn FutureSpawner>,
-    pub handle: Option<StateSyncDumpHandle>,
+    pub handle: Option<Arc<StateSyncDumpHandle>>,
 }
 
 impl StateSyncDumper {
@@ -93,7 +91,7 @@ impl StateSyncDumper {
         };
 
         let chain_id = self.client_config.chain_id.clone();
-        let keep_running = Arc::new(AtomicBool::new(true));
+        let handle = Arc::new(StateSyncDumpHandle::new());
 
         let chain = Chain::new_for_view_client(
             self.clock.clone(),
@@ -111,7 +109,8 @@ impl StateSyncDumper {
                 tracing::debug!(target: "state_sync_dump", ?shard_id, "Dropped existing progress");
             }
         }
-        let handle = (self.dump_future_runner)(
+        self.future_spawner.spawn_boxed(
+            "state_sync_dump",
             do_state_sync_dump(
                 self.clock.clone(),
                 chain,
@@ -122,36 +121,34 @@ impl StateSyncDumper {
                 external,
                 dump_config.iteration_delay.unwrap_or(Duration::seconds(10)),
                 self.validator.clone(),
-                keep_running.clone(),
+                handle.clone(),
                 self.future_spawner.clone(),
             )
             .boxed(),
         );
 
-        self.handle = Some(StateSyncDumpHandle { handle: Some(handle), keep_running });
+        self.handle = Some(handle);
         Ok(())
     }
 
-    pub fn arbiter_dump_future_runner() -> Box<dyn Fn(BoxFuture<'static, ()>) -> Box<dyn FnOnce()>>
-    {
-        Box::new(|future| {
-            let arbiter = Arbiter::new();
-            assert!(arbiter.spawn(future));
-            Box::new(move || {
-                arbiter.stop();
-            })
-        })
-    }
-
     pub fn stop(&mut self) {
         self.handle.take();
     }
+
+    // Tell the dumper to stop and wait until it's finished
+    pub fn stop_and_await(&mut self) {
+        let Some(handle) = self.handle.take() else {
+            return;
+        };
+        handle.stop_and_await();
+    }
 }
 
-/// Holds arbiter handles controlling the lifetime of the spawned threads.
+/// Cancels the dumper when dropped and allows waiting for the dumper task to finish
 pub struct StateSyncDumpHandle {
-    pub handle: Option<Box<dyn FnOnce()>>,
-    keep_running: Arc<AtomicBool>,
+    keep_running: AtomicBool,
+    task_running: Mutex<bool>,
+    await_task: Condvar,
 }
 
 impl Drop for StateSyncDumpHandle {
@@ -161,10 +158,34 @@ impl Drop for StateSyncDumpHandle {
 }
 
 impl StateSyncDumpHandle {
-    fn stop(&mut self) {
+    fn new() -> Self {
+        Self {
+            keep_running: AtomicBool::new(true),
+            task_running: Mutex::new(true),
+            await_task: Condvar::new(),
+        }
+    }
+
+    // Tell the dumper to stop
+    fn stop(&self) {
         tracing::warn!(target: "state_sync_dump", "Stopping state dumper");
         self.keep_running.store(false, Ordering::Relaxed);
-        self.handle.take().unwrap()()
+    }
+
+    // Tell the dumper to stop and wait until it's finished
+    fn stop_and_await(&self) {
+        self.stop();
+        let mut running = self.task_running.lock().unwrap();
+        while *running {
+            running = self.await_task.wait(running).unwrap();
+        }
+    }
+
+    // Called by the dumper when it's finished, and wakes up any threads waiting on it
+    fn task_finished(&self) {
+        let mut running = self.task_running.lock().unwrap();
+        *running = false;
+        self.await_task.notify_all();
     }
 }
 
@@ -262,6 +283,39 @@ impl DumpState {
             }
         }
     }
+
+    /// Waits until all part upload tasks are done for some shard.
+    async fn await_parts_upload(&mut self) -> (ShardId, anyhow::Result<()>) {
+        let ((shard_id, result), _, _still_going) =
+            futures::future::select_all(self.dump_state.iter_mut().map(|(shard_id, s)| {
+                async {
+                    let r = (&mut s.upload_parts).await.unwrap();
+                    (*shard_id, r)
+                }
+                .boxed()
+            }))
+            .await;
+
+        drop(_still_going);
+
+        self.dump_state.remove(&shard_id);
+        (shard_id, result)
+    }
+
+    /// Sets the `canceled` variable to true and waits for all tasks to exit
+    async fn cancel(&mut self) {
+        self.canceled.store(true, Ordering::Relaxed);
+        for (_shard_id, d) in self.dump_state.iter() {
+            // Set it to -1 to tell the existing tasks not to set the metrics anymore
+            d.parts_dumped.store(-1, Ordering::SeqCst);
+        }
+        while !self.dump_state.is_empty() {
+            let (shard_id, result) = self.await_parts_upload().await;
+            if let Err(error) = result {
+                tracing::error!(target: "state_sync_dump", epoch_id = ?&self.epoch_id, %shard_id, ?error, "Shard dump failed after cancellation");
+            }
+        }
+    }
 }
 
 // Represents the state of the current epoch's state part dump
@@ -887,17 +941,7 @@ impl StateDumper {
         let CurrentDump::InProgress(dump) = &mut self.current_dump else {
             return std::future::pending().await;
         };
-        let ((shard_id, result), _, _still_going) =
-            futures::future::select_all(dump.dump_state.iter_mut().map(|(shard_id, s)| {
-                async {
-                    let r = (&mut s.upload_parts).await.unwrap();
-                    (*shard_id, r)
-                }
-                .boxed()
-            }))
-            .await;
-
-        drop(_still_going);
+        let (shard_id, result) = dump.await_parts_upload().await;
 
         match result {
             Ok(()) => {
@@ -918,7 +962,7 @@ impl StateDumper {
                 }),
             )
             .context("failed setting state dump progress")?;
-        dump.dump_state.remove(&shard_id);
+
         if dump.dump_state.is_empty() {
             self.current_dump = CurrentDump::Done(dump.epoch_id);
         }
@@ -942,7 +986,7 @@ impl StateDumper {
         let Some(sync_header) = self.latest_sync_header()? else {
             return Ok(());
         };
-        match &self.current_dump {
+        match &mut self.current_dump {
             CurrentDump::InProgress(dump) => {
                 if &dump.epoch_id == sync_header.epoch_id() {
                     return Ok(());
@@ -951,11 +995,7 @@ impl StateDumper {
                     target: "state_sync_dump", "Canceling existing dump of state for epoch {} upon new epoch {}",
                     &dump.epoch_id.0, &sync_header.epoch_id().0,
                 );
-                dump.canceled.store(true, Ordering::Relaxed);
-                for (_shard_id, d) in dump.dump_state.iter() {
-                    // Set it to -1 to tell the existing tasks not to set the metrics anymore
-                    d.parts_dumped.store(-1, Ordering::SeqCst);
-                }
+                dump.cancel().await;
             }
             CurrentDump::Done(epoch_id) => {
                 if epoch_id == sync_header.epoch_id() {
@@ -992,7 +1032,7 @@ async fn state_sync_dump(
     external: ExternalConnection,
     iteration_delay: Duration,
     validator: MutableValidatorSigner,
-    keep_running: Arc<AtomicBool>,
+    keep_running: &AtomicBool,
     future_spawner: Arc<dyn FutureSpawner>,
 ) -> anyhow::Result<()> {
     tracing::info!(target: "state_sync_dump", "Running StateSyncDump loop");
@@ -1034,6 +1074,10 @@ async fn state_sync_dump(
         }
     }
 
+    if let CurrentDump::InProgress(mut dump) = dumper.current_dump {
+        tracing::debug!(target: "state_sync_dump", "Awaiting upload task cancellation");
+        dump.cancel().await;
+    }
     tracing::debug!(target: "state_sync_dump", "Stopped state dump thread");
     Ok(())
 }
@@ -1048,7 +1092,7 @@ async fn do_state_sync_dump(
     external: ExternalConnection,
     iteration_delay: Duration,
     validator: MutableValidatorSigner,
-    keep_running: Arc<AtomicBool>,
+    handle: Arc<StateSyncDumpHandle>,
     future_spawner: Arc<dyn FutureSpawner>,
 ) {
     if let Err(error) = state_sync_dump(
@@ -1061,11 +1105,12 @@ async fn do_state_sync_dump(
         external,
         iteration_delay,
         validator,
-        keep_running,
+        &handle.keep_running,
         future_spawner,
     )
     .await
     {
         tracing::error!(target: "state_sync_dump", ?error, "State dumper failed");
     }
+    handle.task_finished();
 }
```

### neard/src/cli.rs
```diff
@@ -583,7 +583,7 @@ impl RunCmd {
             if let Some(handle) = cold_store_loop_handle {
                 handle.stop()
             }
-            state_sync_dumper.stop();
+            state_sync_dumper.stop_and_await();
             resharding_handle.stop();
             futures::future::join_all(rpc_servers.iter().map(|(name, server)| async move {
                 server.stop(true).await;
```
