# [?] fix: catch panics of named tasks (#22386)

## Summary
Severity: Unknown
Chain: Ethereum
Component: paradigmxyz/reth
Published: 2026-02-19
Source: https://github.com/paradigmxyz/reth/commit/b6bcd7e6bda28c4d5798f7535e7bab499aebbc2f
Type: security-commit

## Details
fix: catch panics of named tasks (#22386)

## Patch
### crates/tasks/src/worker_map.rs
```diff
@@ -5,7 +5,7 @@
 //! named task, like a 1-thread thread pool keyed by name.
 
 use dashmap::DashMap;
-use std::thread;
+use std::{panic::AssertUnwindSafe, thread};
 use tokio::sync::{mpsc, oneshot};
 
 type BoxedTask = Box<dyn FnOnce() + Send + 'static>;
@@ -26,7 +26,7 @@ impl WorkerThread {
             .name(name.to_string())
             .spawn(move || {
                 while let Some(task) = rx.blocking_recv() {
-                    task();
+                    let _ = std::panic::catch_unwind(AssertUnwindSafe(task));
                 }
             })
             .unwrap_or_else(|e| panic!("failed to spawn worker thread {name:?}: {e}"));
```
