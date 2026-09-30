# [?] fix: deflake //rs/tests/nested/nns_recovery:nr_broken_dfinity_node by allowing panic (#10041)

## Summary
Severity: Unknown
Chain: Internet Computer
Component: dfinity/ic
Published: 2026-04-28
Source: https://github.com/dfinity/ic/commit/c0e7ce860f5aecf3fafcc742dae0d91dc00aadd9
Type: security-commit

## Details
fix: deflake //rs/tests/nested/nns_recovery:nr_broken_dfinity_node by allowing panic (#10041)

The test performs a `systemctl restart ic-replica` which causes a
SIGTERM to be sent to the replica process which sometimes causes the
sandbox_execution_controller to panic with:
"Sandboxed_execution_controller reply channel closed unexpectedly" which
we now allow in all tests.

## Patch
### rs/canister_sandbox/src/replica_controller/allowed_panics.rs
```diff
@@ -1,5 +1,9 @@
 //! This module contains panics that are allowed by default to occur in logs in system-tests.
 
+pub(crate) fn panic_sandboxed_execution_controller_reply_channel_closed() -> ! {
+    panic!("Sandboxed_execution_controller reply channel closed unexpectedly")
+}
+
 pub(crate) fn panic_launcher_exited_due_to_signal(pid: u32) -> ! {
     panic!(
         "Error from launcher process, pid {pid} exited due to signal! In test environments (e.g., PocketIC), you can safely ignore this message."
```

### rs/canister_sandbox/src/replica_controller/sandboxed_execution_controller.rs
```diff
@@ -1,3 +1,4 @@
+use super::allowed_panics::panic_sandboxed_execution_controller_reply_channel_closed;
 use crate::compiler_sandbox::WasmCompilerProxy;
 use crate::controller_launcher_service::ControllerLauncherService;
 use crate::launcher_service::LauncherService;
@@ -1028,7 +1029,7 @@ impl WasmExecutor for SandboxedExecutionController {
         // Wait for completion.
         let result = rx
             .recv()
-            .expect("Sandboxed_execution_controller reply channel closed unexpectedly");
+            .unwrap_or_else(|_| panic_sandboxed_execution_controller_reply_channel_closed());
         drop(wait_timer);
         let _finish_timer = self
             .metrics
```
