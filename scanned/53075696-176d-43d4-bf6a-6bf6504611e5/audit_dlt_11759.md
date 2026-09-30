# [?] Merge pull request #3275 from ProvableHQ/copilot/fix-deadlock-in-processexclusiveguard

## Summary
Severity: Unknown
Chain: Aleo
Component: AleoNet/snarkVM-test
Published: 2026-05-25
Source: https://github.com/AleoNet/snarkVM-test/commit/2cbe677f775f7f76eefc1554356024abf7ae7f2a
Type: security-commit

## Details
Merge pull request #3275 from ProvableHQ/copilot/fix-deadlock-in-processexclusiveguard

Fail fast on nested `Process::lock()` calls from `ProcessExclusiveGuard`

## Patch
### synthesizer/process/src/lib.rs
```diff
@@ -134,6 +134,12 @@ impl<'a, N: Network> std::ops::Deref for ProcessExclusiveGuard<'a, N> {
 }
 
 impl<'a, N: Network> ProcessExclusiveGuard<'a, N> {
+    /// Panics, since this guard already holds the process lock.
+    #[inline]
+    pub fn lock(&self) -> ! {
+        panic!("Attempted to lock `Process` from `ProcessExclusiveGuard`; this would deadlock")
+    }
+
     /// Adds a new stack to the process.
     /// If the program already exists, then the existing stack is replaced and the original stack is returned.
     /// Note. This method assumes that the provided stack is valid.
```

### synthesizer/process/src/tests/test_upgrade.rs
```diff
@@ -19,6 +19,7 @@
 use crate::{Process, Stack};
 use console::network::{MainnetV0, prelude::*};
 use snarkvm_synthesizer_program::{Program, StackTrait};
+use std::{panic, sync::mpsc, thread, time::Duration};
 
 type CurrentNetwork = MainnetV0;
 
@@ -60,6 +61,26 @@ function foo:
     Ok(())
 }
 
+#[test]
+fn test_nested_process_lock_fails_loudly() -> Result<()> {
+    let (sender, receiver) = mpsc::channel();
+
+    thread::spawn(move || {
+        let process = Process::<CurrentNetwork>::load().expect("Failed to load process");
+        let result = panic::catch_unwind(panic::AssertUnwindSafe(|| {
+            let guard = process.lock();
+            guard.lock();
+        }));
+        sender.send(result.is_err()).expect("Failed to send test result");
+    });
+
+    assert!(
+        receiver.recv_timeout(Duration::from_secs(5)).expect("Failed to receive test result"),
+        "Expected nested process lock to panic instead of deadlocking"
+    );
+    Ok(())
+}
+
 #[test]
 fn test_upgrade_without_constructor() -> Result<()> {
     // Sample the default process.
```
