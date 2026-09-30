# [?] fix(sns/nns): Fix edge case where simultaneous upgrades can cause deadlock (#6127)

## Summary
Severity: Unknown
Chain: Internet Computer
Component: dfinity/ic
Published: 2025-08-05
Source: https://github.com/dfinity/ic/commit/d04967f6f52504dada4ff2b206dcc158941b5bb7
Type: security-commit

## Details
fix(sns/nns): Fix edge case where simultaneous upgrades can cause deadlock (#6127)

In rare cases, when two upgrade proposals are passed at the same time,
SNS and NNS root can attempt to execute them both at the same time,
causing the canister to become permanently stopped, or to upgrade
unsafely (when it is not fully stopped.

This is fixed by adding a lock to prevent simultaneous upgrade attempts
on the same canister. The second upgrade immediately fails, which can be
recovered by making a subsequent proposal if that is desired.

Queuing and other sequencing mechanisms to try the conflicting upgrade
were considered, but the complexity outweighed any benefit, since this
is a rare edge case.

## Patch
### Cargo.lock
```diff
@@ -11135,15 +11135,18 @@ dependencies = [
 name = "ic-nervous-system-root"
 version = "0.9.0"
 dependencies = [
+ "async-trait",
  "candid",
  "dfn_core",
  "ic-cdk 0.17.2",
  "ic-crypto-sha2",
  "ic-management-canister-types-private",
  "ic-nervous-system-clients",
+ "ic-nervous-system-lock",
  "ic-nervous-system-runtime",
  "serde",
  "serde_bytes",
+ "tokio",
 ]
 
 [[package]]
```

### rs/nervous_system/lock/src/lib.rs
```diff
@@ -1,15 +1,13 @@
 //! This makes it easy to implement "fail if another async call is in progress".
 //!
 //! See tests.rs for an example of how to use this.
-use std::{cell::RefCell, fmt::Debug, thread::LocalKey};
+use std::{cell::RefCell, collections::BTreeMap, fmt::Debug, thread::LocalKey};
 
 /// If current_resource_flag is None (the happy case), this does a few things:
 ///
-///     1. Sets current_resource_flag to Some(new_resource_flag).
-///
-///     2. Returns Ok.
-///
-///     3. Returns an object that when dropped sets current_resource_flag (back) to None.
+/// 1. Sets current_resource_flag to Some(new_resource_flag).
+/// 2. Returns Ok.
+/// 3. Returns an object that when dropped sets current_resource_flag (back) to None.
 ///
 /// In the sad case (i.e. current_resource_flag is Some(...)), returns Err(current_resource_flag).
 ///
@@ -62,5 +60,66 @@ impl<ResourceFlag: Debug + Copy + 'static> Drop for ResourceGuard<ResourceFlag>
     }
 }
 
+/// Acquires a named lock from a map of locks. If the lock is already held for the given key,
+/// returns an error with the existing value. Otherwise, acquires the lock and returns a guard
+/// that will release the lock when dropped.
+///
+/// Returns immediately; does not wait for others to release.
+pub fn acquire_for<K, V>(
+    lock_map: &'static LocalKey<RefCell<BTreeMap<K, V>>>,
+    lock_name: K,
+    lock_object: V,
+) -> Result<NamedResourceGuard<K, V>, V>
+where
+    K: Ord + Clone + 'static,
+    V: Clone + 'static,
+{
+    NamedResourceGuard::new(lock_map, lock_name, lock_object)
+}
+
+pub struct NamedResourceGuard<K, V>
+where
+    K: Ord + Clone + 'static,
+    V: Clone + 'static,
+{
+    lock_map: &'static LocalKey<RefCell<BTreeMap<K, V>>>,
+    key: K,
+}
+
+impl<K, V> NamedResourceGuard<K, V>
+where
+    K: Ord + Clone + 'static,
+    V: Clone + 'static,
+{
+    fn new(
+        lock_map: &'static LocalKey<RefCell<BTreeMap<K, V>>>,
+        key: K,
+        value: V,
+    ) -> Result<Self, V> {
+        lock_map.with(|cell| {
+            let mut map = cell.borrow_mut();
+            if let Some(existing) = map.get(&key) {
+                return Err(existing.clone());
+            }
+            map.insert(key.clone(), value);
+            Ok(())
+        })?;
+
+        Ok(NamedResourceGuard { lock_map, key })
+    }
+}
+
+impl<K, V> Drop for NamedResourceGuard<K, V>
+where
+    K: Ord + Clone + 'static,
+    V: Clone + 'static,
+{
+    fn drop(&mut self) {
+        self.lock_map.with(|cell| {
+            cell.borrow_mut().remove(&self.key);
+        });
+    }
+}
+
 #[cfg(test)]
 mod tests;
```

### rs/nervous_system/lock/src/tests.rs
```diff
@@ -1,7 +1,7 @@
-use super::acquire;
+use super::{acquire, acquire_for};
 
 use futures::join;
-use std::{cell::RefCell, time::Duration};
+use std::{cell::RefCell, collections::BTreeMap, time::Duration};
 use tokio::time::sleep;
 
 // Example of how to use acquire.
@@ -57,3 +57,81 @@ async fn test_acquire() {
     // Hit me, baby, one more time!
     assert!(delayed_call(0, 1000).await);
 }
+
+#[derive(Debug, Clone, Copy, PartialEq, Eq)]
+enum FileOperation {
+    Read,
+    Write,
+    Delete,
+}
+
+// Example of how to use acquire_for with named locks for file operations.
+async fn try_file_operation(file_path: String, operation: FileOperation) -> bool {
+    thread_local! {
+        static FILE_LOCKS: RefCell<BTreeMap<String, FileOperation>> = const { RefCell::new(BTreeMap::new()) };
+    }
+    let release_on_drop = acquire_for(&FILE_LOCKS, file_path.clone(), operation);
+    if let Err(existing_operation) = release_on_drop {
+        // Abort. Do not do real work.
+        eprintln!(
+            "File '{}' already has {:?} operation in progress.",
+            file_path, existing_operation
+        );
+        return false;
+    }
+
+    // Do real work here (simulate file I/O).
+    sleep(Duration::from_millis(133)).await;
+    true
+}
+
+async fn delayed_file_operation(
+    pre_flight_delay_ms: u64,
+    file_path: &str,
+    operation: FileOperation,
+) -> bool {
+    sleep(Duration::from_millis(pre_flight_delay_ms)).await;
+    try_file_operation(file_path.to_string(), operation).await
+}
+
+#[tokio::test]
+async fn test_acquire_for_named_locks() {
+    // Test that different files can be operated on simultaneously
+    let results = join!(
+        delayed_file_operation(0, "/tmp/file1.txt", FileOperation::Read), // Read file1
+        delayed_file_operation(0, "/tmp/file2.txt", FileOperation::Write), // Write file2 (different file)
+        delayed_file_operation(67, "/tmp/file1.txt", FileOperation::Write), // Write file1 (should fail - same file)
+        delayed_file_operation(67, "/tmp/file2.txt", FileOperation::Delete), // Delete file2 (should fail - same file)
+        delayed_file_operation(200, "/tmp/file1.txt", FileOperation::Delete), // Delete file1 (should succeed after read completes)
+        delayed_file_operation(200, "/tmp/file3.txt", FileOperation::Read), // Read file3 (different file)
+    );
+
+    // First operations on each file should succeed, overlapping ones should fail
+    assert_eq!(results, (true, true, false, false, true, true));
+}
+
+#[tokio::test]
+async fn test_acquire_for_same_operation_different_targets() {
+    // Test that the same operation type can run on different files simultaneously
+    let results = join!(
+        delayed_file_operation(0, "/var/log/app1.log", FileOperation::Write), // Write to app1.log
+        delayed_file_operation(0, "/var/log/app2.log", FileOperation::Write), // Write to app2.log (same operation, different file)
+        delayed_file_operation(0, "/var/log/app3.log", FileOperation::Write), // Write to app3.log (same operation, different file)
+        delayed_file_operation(67, "/var/log/app1.log", FileOperation::Write), // Write to app1.log again (should fail - same file)
+    );
+
+    // All different files should succeed, same file should fail
+    assert_eq!(results, (true, true, true, false));
+}
+
+#[tokio::test]
+async fn test_acquire_for_mixed_targets_and_operations() {
+    // Test mixed operations on different files to ensure they don't interfere
+    let results = join!(
+        delayed_file_operation(0, "/home/user/config.json", FileOperation::Read),
+        delayed_file_operation(0, "/tmp/cache.dat", FileOperation::Delete),
+        delayed_file_operation(0, "/home/user/config.json", FileOperation::Write), // Should fail - same file
+    );
+
+    assert_eq!(results, (true, true, false));
+}
```

### rs/nervous_system/root/BUILD.bazel
```diff
@@ -6,6 +6,7 @@ DEPENDENCIES = [
     # Keep sorted.
     "//rs/crypto/sha2",
     "//rs/nervous_system/clients",
+    "//rs/nervous_system/lock",
     "//rs/nervous_system/runtime",
     "//rs/rust_canisters/dfn_core",
     "//rs/types/management_canister_types",
@@ -15,9 +16,15 @@ DEPENDENCIES = [
     "@crate_index//:serde_bytes",
 ]
 
-MACRO_DEPENDENCIES = []
+MACRO_DEPENDENCIES = [
+    # Keep sorted.
+    "@crate_index//:async-trait",
+]
 
-DEV_DEPENDENCIES = []
+DEV_DEPENDENCIES = [
+    # Keep sorted.
+    "@crate_index//:tokio",
+]
 
 MACRO_DEV_DEPENDENCIES = []
 
```

### rs/nervous_system/root/Cargo.toml
```diff
@@ -15,6 +15,11 @@ ic-cdk = { workspace = true }
 ic-crypto-sha2 = { path = "../../crypto/sha2" }
 ic-management-canister-types-private = { path = "../../types/management_canister_types" }
 ic-nervous-system-clients = { path = "../clients" }
+ic-nervous-system-lock = { path = "../lock" }
 ic-nervous-system-runtime = { path = "../runtime" }
 serde = { workspace = true }
 serde_bytes = { workspace = true }
+
+[dev-dependencies]
+async-trait = { workspace = true }
+tokio = { workspace = true, features = ["test-util"] }
\ No newline at end of file
```

### rs/nervous_system/root/src/change_canister.rs
```diff
@@ -14,8 +14,10 @@ use ic_nervous_system_clients::{
         canister_status, CanisterStatusResultFromManagementCanister, CanisterStatusType,
     },
 };
+use ic_nervous_system_lock::acquire_for;
 use ic_nervous_system_runtime::Runtime;
 use serde::Serialize;
+use std::{cell::RefCell, collections::BTreeMap};
 
 /// The structure allows reconstructing a potentially large WASM from chunks needed to upgrade or
 /// reinstall some target canister.
@@ -218,13 +220,31 @@ pub struct StopOrStartCanisterRequest {
     pub action: CanisterAction,
 }
 
+// Thread-local storage for per-canister locks
+// Key: CanisterId, Value: ChangeCanisterRequest (for debugging/logging)
+thread_local! {
+    static CANISTER_CHANGE_LOCKS: RefCell<BTreeMap<CanisterId, ChangeCanisterRequest>> =
+        const {RefCell::new(BTreeMap::new()) };
+}
+
 pub async fn change_canister<Rt>(request: ChangeCanisterRequest) -> Result<(), String>
 where
     Rt: Runtime,
 {
     let canister_id = request.canister_id;
     let stop_before_installing = request.stop_before_installing;
 
+    // Try to acquire lock for this canister - fail immediately if locked
+    let _guard = match acquire_for(&CANISTER_CHANGE_LOCKS, canister_id, request.clone()) {
+        Ok(guard) => guard,
+        Err(conflicting_request) => {
+            return Err(format!(
+                "Canister {} is currently locked by another change operation. Conflicting request: {:?}",
+                canister_id, conflicting_request
+            ));
+        }
+    };
+
     if stop_before_installing {
         let stop_result = stop_canister::<Rt>(canister_id).await;
         if stop_result.is_err() {
@@ -395,3 +415,108 @@ where
         None => serializer.serialize_none(),
     }
 }
+
+#[cfg(test)]
+mod tests {
+    use super::*;
+    use async_trait::async_trait;
+    use candid::utils::{ArgumentDecoder, ArgumentEncoder};
+    use dfn_core::api::CanisterId;
+    use std::future::Future;
+
+    // Mock runtime that returns errors for all inter-canister calls
+    // This allows us to test the locking behavior without actually making calls
+    struct MockRuntime;
+
+    #[async_trait]
+    impl Runtime for MockRuntime {
+        async fn call_without_cleanup<In, Out>(
+            _id: CanisterId,
+            _method: &str,
+            _args: In,
+        ) -> Result<Out, (i32, String)>
+        where
+            In: ArgumentEncoder + Send,
+            Out: for<'a> ArgumentDecoder<'a>,
+        {
+            Err((
+                1,
+                "MockRuntime: call_without_cleanup not implemented".to_string(),
+            ))
+        }
+
+        async fn call_with_cleanup<In, Out>(
+            _id: CanisterId,
+            _method: &str,
+            _args: In,
+        ) -> Result<Out, (i32, String)>
+        where
+            In: ArgumentEncoder + Send,
+            Out: for<'a> ArgumentDecoder<'a>,
+        {
+            Err((
+                1,
+                "MockRuntime: call_with_cleanup not implemented".to_string(),
+            ))
+        }
+
+        async fn call_bytes_with_cleanup(
+            _id: CanisterId,
+            _method: &str,
+            _args: &[u8],
+        ) -> Result<Vec<u8>, (i32, String)> {
+            Err((
+                1,
+                "MockRuntime: call_bytes_with_cleanup not implemented".to_string(),
+            ))
+        }
+
+        fn spawn_future<F: 'static + Future<Output = ()>>(_future: F) {
+            // Do nothing - we don't need to actually spawn
+        }
+
+        fn canister_version() -> u64 {
+            1
+        }
+    }
+
+    #[tokio::test]
+    async fn test_change_canister_fails_when_lock_exists() {
+        let canister_id = CanisterId::from_u64(42);
+
+        // Create a request that we'll use to pre-populate the lock
+        let conflicting_request = ChangeCanisterRequest {
+            stop_before_installing: false,
+            canister_id,
+            mode: CanisterInstallMode::Install,
+            wasm_module: vec![1, 2, 3],
+            chunked_canister_wasm: None,
+            arg: vec![7, 8, 9],
+        };
+
+        // Manually insert a lock for this canister to simulate a concurrent operation
+        CANISTER_CHANGE_LOCKS.with(|locks| {
+            locks
+                .borrow_mut()
+                .insert(canister_id, conflicting_request.clone());
+        });
+
+        // Now try to call change_canister on the same canister - this should fail
+        let new_request = ChangeCanisterRequest {
+            stop_before_installing: true,
+            canister_id,
+            mode: CanisterInstallMode::Upgrade,
+            wasm_module: vec![10, 11, 12],
+            chunked_canister_wasm: None,
+            arg: vec![16, 17, 18],
+        };
+
+        let result = change_canister::<MockRuntime>(new_request).await;
+
+        // Should return an error indicating the canister is locked
+        assert!(result.is_err());
+        let error_msg = result.unwrap_err();
+        assert!(error_msg.contains("currently locked by another change operation"));
+        assert!(error_msg.contains(&format!("{}", canister_id)));
+    }
+}
```

### rs/nns/handlers/root/unreleased_changelog.md
```diff
@@ -11,10 +11,16 @@ on the process that this file is part of, see
 
 ## Changed
 
+## Unreleased
+
 ## Deprecated
 
 ## Removed
 
 ## Fixed
 
+- A lock was added to `change_canister` to prevent two simultaneous upgrade operations from being executed  
+  at the same time. The second upgrade will now fail immediately instead of attempting to run, which prevents
+  dangerous edge cases where the canister is restarted by one operation while being upgraded by another.
+
 ## Security
```

### rs/sns/root/unreleased_changelog.md
```diff
@@ -17,4 +17,8 @@ on the process that this file is part of, see
 
 ## Fixed
 
+- A lock was added to `change_canister` to prevent two simultaneous upgrade operations from being executed  
+  at the same time. The second upgrade will now fail immediately instead of attempting to run, which prevents
+  dangerous edge cases where the canister is restarted by one operation while being upgraded by another.
+
 ## Security
```
