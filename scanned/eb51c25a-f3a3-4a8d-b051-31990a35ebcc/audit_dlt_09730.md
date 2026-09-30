# [?] fix(client): don't panic in ClientHandle::drop outside a tokio runtime

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-08-25
Source: https://github.com/fedimint/fedimint/commit/db5b9c4b5953092b12ce7ff7b343d17541970925
Type: security-commit

## Details
fix(client): don't panic in ClientHandle::drop outside a tokio runtime

Drop called tokio's Handle::current(), which panics when the last handle
is dropped on a thread without a runtime context. Since this fires inside
a destructor, it commonly happens while already unwinding from another
panic and escalates to a process abort, e.g. devimint teardown aborts
orphaning child daemons.

Use Handle::try_current() and take the existing non-blocking shutdown
fallback when no runtime is available; destructors must never panic.

Fixes #9053.

Assisted-by: Claude Fable 5 (claude-fable-5)

## Patch
### fedimint-client/src/client/handle.rs
```diff
@@ -164,20 +164,31 @@ impl Drop for ClientHandle {
             return;
         }
 
-        // We can't use block_on in single-threaded mode or wasm
+        // We can't use block_on in single-threaded mode, on wasm, or on a thread
+        // without a runtime context, e.g. when the last handle is dropped while
+        // unwinding from a panic. Destructors must never panic, so all these
+        // cases fall back to a non-blocking partial shutdown.
+        #[cfg(not(target_family = "wasm"))]
+        let runtime_handle = RuntimeHandle::try_current();
         #[cfg(target_family = "wasm")]
         let can_block = false;
         #[cfg(not(target_family = "wasm"))]
-        // nosemgrep: ban-raw-block-on
-        let can_block = RuntimeHandle::current().runtime_flavor() != RuntimeFlavor::CurrentThread;
+        let can_block = runtime_handle
+            .as_ref()
+            .is_ok_and(|handle| handle.runtime_flavor() != RuntimeFlavor::CurrentThread);
         if !can_block {
             let inner = self.inner.take().expect("Must have inner client set");
             inner.executor.stop_executor();
-            if cfg!(target_family = "wasm") {
-                error!(target: LOG_CLIENT, "Automatic client shutdown is not possible on wasm, call ClientHandle::shutdown manually.");
+            #[cfg(target_family = "wasm")]
+            let reason = "on wasm";
+            #[cfg(not(target_family = "wasm"))]
+            // `can_block` is false, so an existing runtime must be current-thread flavored.
+            let reason = if runtime_handle.is_ok() {
+                "on current thread runtime"
             } else {
-                error!(target: LOG_CLIENT, "Automatic client shutdown is not possible on current thread runtime, call ClientHandle::shutdown manually.");
-            }
+                "without a runtime"
+            };
+            error!(target: LOG_CLIENT, "Automatic client shutdown is not possible {reason}, call ClientHandle::shutdown manually.");
             return;
         }
 
```
