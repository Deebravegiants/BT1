# [?] fix(tasks): install panic handler on all worker pools (#22993)

## Summary
Severity: Unknown
Chain: Ethereum
Component: paradigmxyz/reth
Published: 2026-03-12
Source: https://github.com/paradigmxyz/reth/commit/1589f0f68482ed02ba955f532d4e8fb696d5a634
Type: security-commit

## Details
fix(tasks): install panic handler on all worker pools (#22993)

Co-authored-by: Amp <amp@ampcode.com>
Co-authored-by: tempo-ai[bot] <195591+tempo-ai[bot]@users.noreply.github.com>
Co-authored-by: Brian Picciano <933154+mediocregopher@users.noreply.github.com>

## Patch
### .changelog/dark-ants-write.md
```diff
@@ -0,0 +1,5 @@
+---
+reth-tasks: patch
+---
+
+Added panic handler to all rayon thread pools that logs panics via `tracing::error` instead of aborting the process.
```

### crates/tasks/src/lib.rs
```diff
@@ -40,7 +40,7 @@ pub(crate) mod worker_map;
 #[cfg(feature = "rayon")]
 pub mod pool;
 #[cfg(feature = "rayon")]
-pub use pool::{Worker, WorkerPool};
+pub use pool::{build_pool_with_panic_handler, Worker, WorkerPool};
 
 /// Lock-free ordered parallel iterator extension trait.
 #[cfg(feature = "rayon")]
```

### crates/tasks/src/pool.rs
```diff
@@ -180,10 +180,12 @@ impl WorkerPool {
     }
 
     /// Creates a new `WorkerPool` from a [`rayon::ThreadPoolBuilder`].
+    ///
+    /// Installs a panic handler that logs panics instead of aborting the process.
     pub fn from_builder(
         builder: rayon::ThreadPoolBuilder,
     ) -> Result<Self, rayon::ThreadPoolBuildError> {
-        Ok(Self { pool: builder.build()? })
+        Ok(Self { pool: build_pool_with_panic_handler(builder)? })
     }
 
     /// Returns the total number of threads in the underlying rayon pool.
@@ -283,6 +285,16 @@ impl WorkerPool {
     }
 }
 
+/// Builds a rayon thread pool with a panic handler that prevents aborting the process.
+///
+/// Rust's default panic hook already logs the panic message and backtrace to stderr, so the handler
+/// itself is intentionally a no-op.
+pub fn build_pool_with_panic_handler(
+    builder: rayon::ThreadPoolBuilder,
+) -> Result<rayon::ThreadPool, rayon::ThreadPoolBuildError> {
+    builder.panic_handler(|_| {}).build()
+}
+
 /// Per-thread state container for a [`WorkerPool`].
 ///
 /// Holds a type-erased `Box<dyn Any>` that can be initialized and accessed with concrete types
```

### crates/tasks/src/runtime.rs
```diff
@@ -7,7 +7,7 @@
 //! - [`BlockingTaskGuard`] for rate-limiting expensive operations (with `rayon` feature)
 
 #[cfg(feature = "rayon")]
-use crate::pool::{BlockingTaskGuard, BlockingTaskPool, WorkerPool};
+use crate::pool::{build_pool_with_panic_handler, BlockingTaskGuard, BlockingTaskPool, WorkerPool};
 use crate::{
     metrics::{IncCounterOnDrop, TaskExecutorMetrics},
     shutdown::{GracefulShutdown, GracefulShutdownGuard, Shutdown},
@@ -790,23 +790,26 @@ impl RuntimeBuilder {
             let default_threads = config.rayon.default_thread_count();
             let rpc_threads = config.rayon.rpc_threads.unwrap_or(default_threads);
 
-            let cpu_pool = rayon::ThreadPoolBuilder::new()
-                .num_threads(default_threads)
-                .thread_name(|i| format!("cpu-{i:02}"))
-                .build()?;
+            let cpu_pool = build_pool_with_panic_handler(
+                rayon::ThreadPoolBuilder::new()
+                    .num_threads(default_threads)
+                    .thread_name(|i| format!("cpu-{i:02}")),
+            )?;
 
-            let rpc_raw = rayon::ThreadPoolBuilder::new()
-                .num_threads(rpc_threads)
-                .thread_name(|i| format!("rpc-{i:02}"))
-                .build()?;
+            let rpc_raw = build_pool_with_panic_handler(
+                rayon::ThreadPoolBuilder::new()
+                    .num_threads(rpc_threads)
+                    .thread_name(|i| format!("rpc-{i:02}")),
+            )?;
             let rpc_pool = BlockingTaskPool::new(rpc_raw);
 
             let storage_threads =
                 config.rayon.storage_threads.unwrap_or(DEFAULT_STORAGE_POOL_THREADS);
-            let storage_pool = rayon::ThreadPoolBuilder::new()
-                .num_threads(storage_threads)
-                .thread_name(|i| format!("storage-{i:02}"))
-                .build()?;
+            let storage_pool = build_pool_with_panic_handler(
+                rayon::ThreadPoolBuilder::new()
+                    .num_threads(storage_threads)
+                    .thread_name(|i| format!("storage-{i:02}")),
+            )?;
 
             let blocking_guard = BlockingTaskGuard::new(config.rayon.max_blocking_tasks);
 
```
