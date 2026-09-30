# [?] Use `block_in_place()` to avoid potential deadlock in `debug_inspect_unspent_allowance()`

## Summary
Severity: Unknown
Chain: Casper
Component: casper-network/casper-node
Published: 2022-11-24
Source: https://github.com/casper-network/casper-node/commit/a7bfbc96595526db80f7cc5d0b76958740bdd11c
Type: security-commit

## Details
Use `block_in_place()` to avoid potential deadlock in `debug_inspect_unspent_allowance()`

## Patch
### node/src/components/network/limiter.rs
```diff
@@ -6,12 +6,11 @@
 use std::{
     collections::{HashMap, HashSet},
     sync::{Arc, RwLock},
-    thread,
     time::{Duration, Instant},
 };
 
 use prometheus::Counter;
-use tokio::sync::Mutex;
+use tokio::{runtime::Handle, sync::Mutex, task};
 use tracing::{error, trace};
 
 use casper_types::{EraId, PublicKey};
@@ -113,15 +112,9 @@ impl Limiter {
     }
 
     pub(super) fn debug_inspect_unspent_allowance(&self) -> Option<i64> {
-        // Calling `blocking_lock()` from withing an async runtime will cause Tokio to panic with
-        // "Cannot start a runtime from within a runtime..." message. To avoid that we do the
-        // blocking call in a dedicated thread. It's a workaround that has a slight performance
-        // cost, but it's only invoked when using the `net-info` command of the Diagnostics Port,
-        // hence it's assumed to be rare.
-        let resources = Arc::clone(&self.data.resources);
-        thread::spawn(move || Some(resources.blocking_lock().available))
-            .join()
-            .unwrap_or(None)
+        Some(task::block_in_place(move || {
+            Handle::current().block_on(async move { self.data.resources.lock().await.available })
+        }))
     }
 
     pub(super) fn debug_inspect_validators(
```
