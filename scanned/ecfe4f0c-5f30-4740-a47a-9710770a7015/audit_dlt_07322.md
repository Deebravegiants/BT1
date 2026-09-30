# [?] fix(PocketIC): temporary state manager crash (#4928)

## Summary
Severity: Unknown
Chain: Internet Computer
Component: dfinity/ic
Published: 2025-04-30
Source: https://github.com/dfinity/ic/commit/2fd03f07735b5c1baee3e5b1e87def007ddb3fae
Type: security-commit

## Details
fix(PocketIC): temporary state manager crash (#4928)

This PR fixes a bug in PocketIC causing a temporary state manager to
crash: the temporary state manager used to retrieve subnet metadata must
operate on a private copy of the subnet state directory.

## Patch
### rs/pocket_ic_server/CHANGELOG.md
```diff
@@ -11,6 +11,11 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0
 
 ## Unreleased
 
+### Fixed
+- Crash when creating multiple instances with the same subnet state directory simultaneously.
+
+
+
 ## 9.0.0 - 2025-04-23
 
 ### Added
```

### rs/pocket_ic_server/src/pocket_ic.rs
```diff
@@ -980,23 +980,31 @@ impl PocketIc {
                 let (ranges, alloc_range, subnet_id, time) = if let Some(ref subnet_state_dir) =
                     subnet_state_dir
                 {
-                    // We create a temporary state manager used to read the given state metadata.
-                    let state_manager = StateManagerImpl::new(
-                        Arc::new(FakeVerifier),
-                        SubnetId::new(PrincipalId::default()),
-                        conv_type(subnet_kind),
-                        no_op_logger(),
-                        &MetricsRegistry::new(),
-                        &ic_config::state_manager::Config::new(
-                            subnet_state_dir.path().to_path_buf(),
-                        ),
-                        None,
-                        MaliciousFlags::default(),
-                    );
-                    let metadata = state_manager.get_latest_state().take().metadata.clone();
-                    // Shut down the temporary state manager to avoid race conditions.
-                    state_manager.flush_tip_channel();
-                    drop(state_manager);
+                    let metadata = {
+                        // We create a temporary state manager used to read the given state metadata.
+                        // We first copy the subnet state directory into a temporary directory
+                        // so that the temporary state manager has a private copy
+                        // of the subnet state directory (otherwise, it might crash).
+                        let temp_state_dir = TempDir::new().unwrap();
+                        copy_dir(subnet_state_dir, temp_state_dir.path())
+                            .expect("Failed to copy state directory");
+                        let state_manager = StateManagerImpl::new(
+                            Arc::new(FakeVerifier),
+                            SubnetId::new(PrincipalId::default()),
+                            conv_type(subnet_kind),
+                            no_op_logger(),
+                            &MetricsRegistry::new(),
+                            &ic_config::state_manager::Config::new(
+                                temp_state_dir.path().to_path_buf(),
+                            ),
+                            None,
+                            MaliciousFlags::default(),
+                        );
+                        let metadata = state_manager.get_latest_state().take().metadata.clone();
+                        // Shut down the temporary state manager to avoid race conditions.
+                        state_manager.flush_tip_channel();
+                        metadata
+                    };
 
                     let subnet_id = metadata.own_subnet_id;
                     let time = metadata.batch_time;
```
