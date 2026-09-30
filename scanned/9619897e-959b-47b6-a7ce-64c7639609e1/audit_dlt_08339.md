# [?] fix deadlock on nested DropHelper (#15322)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2024-11-20
Source: https://github.com/aptos-labs/aptos-core/commit/e2af7c46384d06aad4a4ea8eec9a244f4d902aa2
Type: security-commit

## Details
fix deadlock on nested DropHelper (#15322)

## Patch
### Cargo.lock
```diff
@@ -1375,6 +1375,7 @@ dependencies = [
  "aptos-metrics-core",
  "derive_more",
  "once_cell",
+ "rayon",
  "threadpool",
 ]
 
```

### crates/aptos-drop-helper/Cargo.toml
```diff
@@ -18,3 +18,6 @@ aptos-metrics-core = { workspace = true }
 derive_more = { workspace = true }
 once_cell = { workspace = true }
 threadpool = { workspace = true }
+
+[dev-dependencies]
+rayon = { workspace = true }
```

### crates/aptos-drop-helper/src/async_concurrent_dropper.rs
```diff
@@ -1,7 +1,10 @@
 // Copyright © Aptos Foundation
 // SPDX-License-Identifier: Apache-2.0
 
-use crate::metrics::{GAUGE, TIMER};
+use crate::{
+    metrics::{GAUGE, TIMER},
+    IN_ANY_DROP_POOL,
+};
 use aptos_infallible::Mutex;
 use aptos_metrics_core::{IntGaugeHelper, TimerHelper};
 use std::sync::{
@@ -42,12 +45,25 @@ impl AsyncConcurrentDropper {
         rx
     }
 
+    pub fn max_tasks(&self) -> usize {
+        self.num_tasks_tracker.max_tasks
+    }
+
+    pub fn num_threads(&self) -> usize {
+        self.thread_pool.max_count()
+    }
+
     pub fn wait_for_backlog_drop(&self, no_more_than: usize) {
         let _timer = TIMER.timer_with(&[self.name, "wait_for_backlog_drop"]);
         self.num_tasks_tracker.wait_for_backlog_drop(no_more_than);
     }
 
     fn schedule_drop_impl<V: Send + 'static>(&self, v: V, notif_sender_opt: Option<Sender<()>>) {
+        if IN_ANY_DROP_POOL.get() {
+            Self::do_drop(v, notif_sender_opt);
+            return;
+        }
+
         let _timer = TIMER.timer_with(&[self.name, "enqueue_drop"]);
         self.num_tasks_tracker.inc();
 
@@ -57,15 +73,23 @@ impl AsyncConcurrentDropper {
         self.thread_pool.execute(move || {
             let _timer = TIMER.timer_with(&[name, "real_drop"]);
 
-            drop(v);
+            IN_ANY_DROP_POOL.with(|flag| {
+                flag.set(true);
+            });
 
-            if let Some(sender) = notif_sender_opt {
-                sender.send(()).ok();
-            }
+            Self::do_drop(v, notif_sender_opt);
 
             num_tasks_tracker.dec();
         })
     }
+
+    fn do_drop<V: Send + 'static>(v: V, notif_sender_opt: Option<Sender<()>>) {
+        drop(v);
+
+        if let Some(sender) = notif_sender_opt {
+            sender.send(()).ok();
+        }
+    }
 }
 
 struct NumTasksTracker {
@@ -111,10 +135,12 @@ impl NumTasksTracker {
 
 #[cfg(test)]
 mod tests {
-    use crate::AsyncConcurrentDropper;
+    use crate::{AsyncConcurrentDropper, DropHelper, DEFAULT_DROPPER};
+    use rayon::prelude::*;
     use std::{sync::Arc, thread::sleep, time::Duration};
     use threadpool::ThreadPool;
 
+    #[derive(Clone, Default)]
     struct SlowDropper;
 
     impl Drop for SlowDropper {
@@ -197,4 +223,25 @@ mod tests {
         s.wait_for_backlog_drop(0);
         assert!(now.elapsed() < Duration::from_millis(600));
     }
+
+    #[test]
+    fn test_nested_drops() {
+        #[derive(Clone, Default)]
+        struct Nested {
+            _inner: DropHelper<SlowDropper>,
+        }
+
+        // pump 2 x max_tasks to the drop queue
+        let num_items = DEFAULT_DROPPER.max_tasks() * 2;
+        let items = vec![DropHelper::new(Nested::default()); num_items];
+        let drop_thread = std::thread::spawn(move || {
+            items.into_par_iter().for_each(drop);
+        });
+
+        // expect no deadlock and the whole thing to be dropped in full concurrency (with some leeway)
+        sleep(Duration::from_millis(
+            200 + 200 * num_items as u64 / DEFAULT_DROPPER.num_threads() as u64,
+        ));
+        assert!(drop_thread.is_finished(), "Drop queue deadlocked.");
+    }
 }
```

### crates/aptos-drop-helper/src/lib.rs
```diff
@@ -4,12 +4,16 @@
 use crate::async_concurrent_dropper::AsyncConcurrentDropper;
 use derive_more::{Deref, DerefMut};
 use once_cell::sync::Lazy;
-use std::mem::ManuallyDrop;
+use std::{cell::Cell, mem::ManuallyDrop};
 
 pub mod async_concurrent_dropper;
 pub mod async_drop_queue;
 mod metrics;
 
+thread_local! {
+    static IN_ANY_DROP_POOL: Cell<bool> = const { Cell::new(false) };
+}
+
 pub static DEFAULT_DROPPER: Lazy<AsyncConcurrentDropper> =
     Lazy::new(|| AsyncConcurrentDropper::new("default", 32, 8));
 
```
