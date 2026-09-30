# [?] Fix: Consensus Worker thread join to prevent shutdown crash

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-03-26
Source: https://github.com/Conflux-Chain/conflux-rust/commit/f8541c05817f904bf0816e505614b0dd8c1582e4
Type: security-commit

## Details
Fix: Consensus Worker thread join to prevent shutdown crash

## Patch
### Cargo.lock
```diff
@@ -2624,6 +2624,7 @@ dependencies = [
  "delegate 0.4.2",
  "diem-config",
  "diem-crypto",
+ "diem-metrics",
  "diem-types",
  "dir",
  "fallible-iterator",
@@ -2731,6 +2732,7 @@ dependencies = [
  "env_logger",
  "executor",
  "jsonrpsee",
+ "libc",
  "log",
  "log4rs",
  "malloc_size_of",
```

### bins/conflux/Cargo.toml
```diff
@@ -42,6 +42,7 @@ bls-signatures = { workspace = true }
 cfx-executor = { workspace = true }
 cfx-execute-helper = { workspace = true }
 cfx-mallocator-utils = { workspace = true }
+libc = { workspace = true }
 
 # [target.'cfg(not(target_env = "msvc"))'.dependencies]
 # tikv-jemallocator = { workspace = true }
```

### bins/conflux/src/main.rs
```diff
@@ -130,7 +130,17 @@ Current Version: {}
         NodeType::Unknown => return Err("Unknown node type".into()),
     };
     info!("Conflux client started");
-    shutdown_handler::run(client_handle, exit);
+    let graceful = shutdown_handler::run(client_handle, exit);
+
+    if !graceful {
+        eprintln!("Unclean shutdown, force exiting to avoid static destructor issues.");
+        // Use _exit() to skip C++ static destructors (e.g. RocksDB's
+        // PeriodicWorkScheduler) which may have already been invalidated
+        // by background threads during shutdown.
+        unsafe {
+            libc::_exit(1);
+        }
+    }
 
     Ok(())
 }
```

### crates/cfxcore/core/src/sync/synchronization_graph.rs
```diff
@@ -15,8 +15,7 @@ use std::{
 };
 
 use cfx_parameters::consensus_internal::ELASTICITY_MULTIPLIER;
-use futures::executor::block_on;
-use parking_lot::RwLock;
+use parking_lot::{Mutex, RwLock};
 use slab::Slab;
 use tokio::sync::mpsc::error::TryRecvError;
 use unexpected::{Mismatch, OutOfBounds};
@@ -985,6 +984,30 @@ impl SynchronizationGraphInner {
     }
 }
 
+/// Manages the lifecycle of the consensus worker thread.
+/// On drop, unsubscribes from the channel (closing the sender) so the worker's
+/// `recv_blocking()` returns `None` and the loop exits naturally, then joins.
+struct ConsensusWorkerHandle {
+    thread: Mutex<Option<thread::JoinHandle<()>>>,
+    /// Channel + subscription ID for unsubscribe-based shutdown.
+    new_block_hashes: Arc<Channel<H256>>,
+    worker_subscription_id: u64,
+}
+
+impl ConsensusWorkerHandle {
+    fn stop(&self) {
+        self.new_block_hashes
+            .unsubscribe(self.worker_subscription_id);
+        if let Some(handle) = self.thread.lock().take() {
+            handle.join().expect("Consensus Worker should not panic");
+        }
+    }
+}
+
+impl Drop for ConsensusWorkerHandle {
+    fn drop(&mut self) { self.stop(); }
+}
+
 pub struct SynchronizationGraph {
     pub inner: Arc<RwLock<SynchronizationGraphInner>>,
     pub consensus: SharedConsensusGraph,
@@ -1007,6 +1030,10 @@ pub struct SynchronizationGraph {
     pub future_blocks: FutureBlockContainer,
 
     machine: Arc<Machine>,
+
+    /// Handle to the consensus worker thread; joined on drop.
+    #[allow(unused)]
+    consensus_worker_handle: ConsensusWorkerHandle,
 }
 
 impl MallocSizeOf for SynchronizationGraph {
@@ -1055,26 +1082,18 @@ impl SynchronizationGraph {
                 pos_verifier.clone(),
             ),
         ));
-        let sync_graph = SynchronizationGraph {
-            inner: inner.clone(),
-            future_blocks: FutureBlockContainer::new(
-                sync_config.future_block_buffer_capacity,
-            ),
-            data_man: data_man.clone(),
-            pow: pow.clone(),
-            verification_config,
-            sync_config,
-            consensus: consensus.clone(),
-            statistics: statistics.clone(),
-            consensus_unprocessed_count: consensus_unprocessed_count.clone(),
-            new_block_hashes: notifications.new_block_hashes.clone(),
-            machine,
-        };
+        let worker_subscription_id = consensus_receiver.id;
+
+        // Clone Arcs before moving them into the worker thread closure.
+        let worker_data_man = data_man.clone();
+        let worker_consensus = consensus.clone();
+        let worker_unprocessed_count = consensus_unprocessed_count.clone();
 
         // It receives `BLOCK_GRAPH_READY` blocks in order and handles them in
         // `ConsensusGraph`
-        thread::Builder::new()
+        let handle = thread::Builder::new()
             .name("Consensus Worker".into())
+            // TODO: extract it in a seperated file
             .spawn(move || {
                 // The Consensus Worker will prioritize blocks based on its parent epoch number while respecting the topological order. This has the following two benefits:
                 //
@@ -1090,13 +1109,13 @@ impl SynchronizationGraph {
                     // Only block when we have processed all received blocks.
                     let mut blocking = priority_queue.is_empty();
                     'inner: loop {
-                        // Use blocking `recv` for the first element, and then drain the receiver
-                        // with non-blocking `try_recv`.
+                        // Use blocking `recv_blocking` for the first element, and then
+                        // drain the receiver with non-blocking `try_recv`.
                         let maybe_item = if blocking {
                             blocking = false;
-                            match block_on(consensus_receiver.recv()) {
+                            match consensus_receiver.recv_blocking() {
                                 Some(item) => Ok(item),
-                                None => break 'outer,
+                                None => break 'outer, // channel closed (unsubscribed)
                             }
                         } else {
                             consensus_receiver.try_recv()
@@ -1106,11 +1125,11 @@ impl SynchronizationGraph {
                             // FIXME: We need to investigate why duplicate hash may send to the consensus worker
                             Ok(hash) => if !reverse_map.contains_key(&hash) {
                                 debug!("Worker thread receive: block = {}", hash);
-                                let header = data_man.block_header_by_hash(&hash).expect("Header must exist before sending to the consensus worker!");
+                                let header = worker_data_man.block_header_by_hash(&hash).expect("Header must exist before sending to the consensus worker!");
 
                                 // start pos with an era advance.
-                                if !pos_started && pos_verifier.is_enabled_at_height(header.height() + consensus.config().inner_conf.era_epoch_count) {
-                                    if let Err(e) = pos_verifier.initialize(consensus.clone()) {
+                                if !pos_started && pos_verifier.is_enabled_at_height(header.height() + worker_consensus.config().inner_conf.era_epoch_count) {
+                                    if let Err(e) = pos_verifier.initialize(worker_consensus.clone()) {
                                         info!("PoS cannot be started at the expected height: e={}", e);
                                     } else {
                                         pos_started = true;
@@ -1137,7 +1156,7 @@ impl SynchronizationGraph {
                                 }
                                 reverse_map.insert(hash.clone(), Vec::new());
                                 if cnt == 0 {
-                                    let epoch_number = consensus.get_block_epoch_number(parent_hash).unwrap_or(0);
+                                    let epoch_number = worker_consensus.get_block_epoch_number(parent_hash).unwrap_or(0);
                                     priority_queue.push((epoch_number, hash));
                                 } else {
                                     counter_map.insert(hash, cnt);
@@ -1157,20 +1176,43 @@ impl SynchronizationGraph {
                             *cnt_tuple -= 1;
                             if *cnt_tuple == 0 {
                                 counter_map.remove(&succ);
-                                let header_succ = data_man.block_header_by_hash(&succ).expect("Header must exist before sending to the consensus worker!");
+                                let header_succ = worker_data_man.block_header_by_hash(&succ).expect("Header must exist before sending to the consensus worker!");
                                 let parent_succ = header_succ.parent_hash();
-                                let epoch_number = consensus.get_block_epoch_number(parent_succ).unwrap_or(0);
+                                let epoch_number = worker_consensus.get_block_epoch_number(parent_succ).unwrap_or(0);
                                 priority_queue.push((epoch_number, succ));
                             }
                         }
-                        consensus.on_new_block(
+                        worker_consensus.on_new_block(
                             &hash,
                         );
-                        consensus_unprocessed_count.fetch_sub(1, Ordering::SeqCst);
+                        worker_unprocessed_count.fetch_sub(1, Ordering::SeqCst);
                     }
                 }
             })
             .expect("Cannot fail");
+
+        let consensus_worker_handle = ConsensusWorkerHandle {
+            thread: Mutex::new(Some(handle)),
+            new_block_hashes: notifications.new_block_hashes.clone(),
+            worker_subscription_id,
+        };
+
+        let sync_graph = SynchronizationGraph {
+            inner: inner.clone(),
+            future_blocks: FutureBlockContainer::new(
+                sync_config.future_block_buffer_capacity,
+            ),
+            data_man: data_man.clone(),
+            pow: pow.clone(),
+            verification_config,
+            sync_config,
+            consensus: consensus.clone(),
+            statistics: statistics.clone(),
+            consensus_unprocessed_count: consensus_unprocessed_count.clone(),
+            new_block_hashes: notifications.new_block_hashes.clone(),
+            machine,
+            consensus_worker_handle,
+        };
         sync_graph
     }
 
```

### crates/client/Cargo.toml
```diff
@@ -48,6 +48,7 @@ tempfile = { workspace = true }
 rustc-hex = { workspace = true }
 threadpool = { workspace = true }
 metrics = { workspace = true }
+diem-metrics = { workspace = true }
 delegate = { workspace = true }
 itertools = { workspace = true }
 order-stat = { workspace = true }
```

### crates/client/src/common/shutdown_handler.rs
```diff
@@ -31,6 +31,10 @@ pub fn run(
 
 /// Returns whether the shutdown is considered clean.
 pub fn shutdown(this: Box<dyn ClientTrait>) -> bool {
+    // Signal metrics reporter threads to stop before dropping components.
+    metrics::stop();
+    diem_metrics::stop();
+
     let (ledger_db, maybe_pos_handler, maybe_blockgen) =
         this.take_out_components_for_shutdown();
     drop(this);
```

### crates/pos/common/metrics/src/lib.rs
```diff
@@ -79,9 +79,16 @@ use std::{
     fs::{create_dir_all, File, OpenOptions},
     io::Write,
     path::Path,
+    sync::atomic::{AtomicBool, Ordering},
     thread, time,
 };
 
+static STOPPED: AtomicBool = AtomicBool::new(false);
+
+/// Signal all diem metrics reporter threads to stop.
+pub fn stop() { STOPPED.store(true, Ordering::Relaxed); }
+pub fn is_stopped() -> bool { STOPPED.load(Ordering::Relaxed) }
+
 pub static NUM_METRICS: Lazy<IntCounterVec> = Lazy::new(|| {
     register_int_counter_vec!(
         "diem_metrics",
@@ -197,13 +204,19 @@ pub fn dump_all_metrics_to_file_periodically<P: AsRef<Path>>(
 ) {
     let mut file = get_metrics_file(dir_path, file_name);
     thread::spawn(move || loop {
+        if is_stopped() {
+            return;
+        }
         let mut buffer = get_all_metrics_as_serialized_string()
             .expect("Error gathering metrics");
         if !buffer.is_empty() {
             buffer.push(b'\n');
             file.write_all(&buffer).expect("Error writing metrics");
         }
         thread::sleep(time::Duration::from_millis(interval));
+        if is_stopped() {
+            return;
+        }
     });
 }
 
```

### crates/util/metrics/src/lib.rs
```diff
@@ -22,7 +22,7 @@ pub use self::{
     histogram::{Histogram, Sample},
     lock::{Lock, MutexExtensions, RwLockExtensions},
     meter::{register_meter, register_meter_with_group, Meter, MeterTimer},
-    metrics::{initialize, is_enabled, Metric, MetricsConfiguration},
+    metrics::{initialize, is_enabled, stop, Metric, MetricsConfiguration},
     queue::{register_queue, register_queue_with_group, Queue},
     registry::{
         GroupingRegistry, Registry, DEFAULT_GROUPING_REGISTRY, DEFAULT_REGISTRY,
```

### crates/util/metrics/src/metrics.rs
```diff
@@ -16,14 +16,20 @@ use std::{
     time::Duration,
 };
 
-pub static ORDER: Ordering = Ordering::Relaxed;
+pub const ORDER: Ordering = Ordering::Relaxed;
 
 static ENABLED: AtomicBool = AtomicBool::new(false);
+static STOPPED: AtomicBool = AtomicBool::new(false);
 
 pub fn is_enabled() -> bool { ENABLED.load(ORDER) }
 
 pub fn enable() { ENABLED.store(true, ORDER); }
 
+/// Signal all metrics reporter threads to stop.
+pub fn stop() { STOPPED.store(true, ORDER); }
+
+pub fn is_stopped() -> bool { STOPPED.load(ORDER) }
+
 pub trait Metric:
     Send + Sync + Reportable + InfluxdbReportable + PrometheusReportable
 {
```

### crates/util/metrics/src/report.rs
```diff
@@ -7,7 +7,7 @@ use crate::{
     gauge::{Gauge, GaugeUsize},
     histogram::Histogram,
     meter::{Meter, StandardMeter},
-    metrics::is_enabled,
+    metrics::{is_enabled, is_stopped},
     registry::{DEFAULT_GROUPING_REGISTRY, DEFAULT_REGISTRY},
 };
 use lazy_static::lazy_static;
@@ -37,10 +37,16 @@ pub fn report_async<R: 'static + Reporter>(reporter: R, interval: Duration) {
     }
 
     thread::spawn(move || loop {
+        if is_stopped() {
+            return;
+        }
         // sleep random time on different nodes to reduce competition.
         thread::sleep(
             interval.mul_f64(0.5 + rand::rng().random_range(0.0..1.0)),
         );
+        if is_stopped() {
+            return;
+        }
 
         let start = Instant::now();
 
```

### integration_tests/test_framework/test_node.py
```diff
@@ -278,8 +278,7 @@ def stop_node(self, expected_stderr='', kill=False, wait=True):
         # Check that stderr is as expected
         self.stderr.seek(0)
         stderr = self.stderr.read().decode('utf-8').strip()
-        # TODO: Check how to avoid `pthread lock: Invalid argument`.
-        if stderr != expected_stderr and stderr != "pthread lock: Invalid argument" and "pthread_mutex_lock" not in stderr:
+        if stderr != expected_stderr:
             if self.return_code is None:
                 self.log.info("Process is still running")
             else:
```

### tests/test_framework/test_node.py
```diff
@@ -276,8 +276,7 @@ def stop_node(self, expected_stderr='', kill=False, wait=True):
         # Check that stderr is as expected
         self.stderr.seek(0)
         stderr = self.stderr.read().decode('utf-8').strip()
-        # TODO: Check how to avoid `pthread lock: Invalid argument`.
-        if stderr != expected_stderr and stderr != "pthread lock: Invalid argument" and "pthread_mutex_lock" not in stderr:
+        if stderr != expected_stderr:
             if self.return_code is None:
                 self.log.info("Process is still running")
             else:
```
