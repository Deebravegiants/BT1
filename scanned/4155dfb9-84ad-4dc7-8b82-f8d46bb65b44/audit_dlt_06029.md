# [?] fix(tests): make all temp_dir usages in tests nondeterministic to avoid collisions (#11189)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-04-14
Source: https://github.com/iotaledger/iota/commit/d49476f37c7740c3cadc158d576a3d6a7609d807
Type: security-commit

## Details
fix(tests): make all temp_dir usages in tests nondeterministic to avoid collisions (#11189)

# Description of change

Replace `std::env::temp_dir()` and raw `tempfile::tempdir()` with
`iota_common::tempdir()` in tests.

## Summary

- Replace all uses of `std::env::temp_dir()` in test code with
`iota_common::tempdir()`
- Replace all direct `tempfile::tempdir()` calls in test code with
`iota_common::tempdir()`
- Add `iota-common` dev-dependency to `iota-data-ingestion-core` and
`iota-archival`

## Motivation

After upgrading RocksDB, unrelated PRs (still on the old version)
started failing with "unsupported version 6" SST file errors. This
revealed that CI test runners were sharing database paths because tests
used `std::env::temp_dir()` directly, which always resolves to the same
`/tmp` directory. This also explains long-standing flaky tests where
RocksDB complained about databases already being opened.

Additionally, several test files had local `temp_dir()` helpers that
called `tempfile::tempdir()` directly, bypassing the
`nondeterministic!()` macro. In `simtests`, deterministic RNG seeding
can cause `tempfile::tempdir()` to produce identical paths across test
runs, leading to the same class of collisions.

`iota_common::tempdir()` is the existing utility that solves both
problems: it creates a unique random directory via `tempfile::tempdir()`
and wraps it in `nondeterministic!()` to ensure uniqueness even under
`simtest` determinism.

## How the change has been tested

- [x] Basic tests (linting, compilation, formatting, unit/integration
tests)
- [ ] Patch-specific tests (correctness, functionality coverage)
- [ ] I have added tests that prove my fix is effective or that my
feature works
- [ ] I have checked that new and existing unit tests pass locally with
my changes

### Cargo.lock
```diff
@@ -5817,6 +5817,7 @@ dependencies = [
  "fastcrypto",
  "futures",
  "indicatif",
+ "iota-common",
  "iota-config",
  "iota-macros",
  "iota-simulator",
@@ -5866,6 +5867,7 @@ dependencies = [
  "futures",
  "iota-benchmark",
  "iota-build-cache-server",
+ "iota-common",
  "iota-config",
  "iota-metrics",
  "iota-swarm-config",
@@ -6242,6 +6244,7 @@ dependencies = [
  "bytes",
  "fastcrypto",
  "futures",
+ "iota-common",
  "iota-config",
  "iota-grpc-client",
  "iota-grpc-types",
@@ -6280,6 +6283,7 @@ dependencies = [
  "futures",
  "indexmap 2.11.0",
  "insta",
+ "iota-common",
  "iota-config",
  "iota-core",
  "iota-framework",
@@ -6380,6 +6384,7 @@ dependencies = [
  "eyre",
  "futures",
  "http 1.4.0",
+ "iota-common",
  "iota-config",
  "iota-json-rpc-types",
  "iota-keys",
@@ -6419,6 +6424,7 @@ dependencies = [
  "anyhow",
  "bcs",
  "capitalize",
+ "iota-common",
  "iota-move-build",
  "iota-types",
  "move-binary-format",
@@ -6439,6 +6445,7 @@ dependencies = [
  "anyhow",
  "bcs",
  "bin-version",
+ "iota-common",
  "iota-framework",
  "iota-move-build",
  "iota-protocol-config",
@@ -6586,6 +6593,7 @@ dependencies = [
  "hyper 1.8.1",
  "im",
  "insta",
+ "iota-common",
  "iota-framework",
  "iota-graphql-config",
  "iota-graphql-rpc-client",
@@ -6767,6 +6775,7 @@ dependencies = [
  "fastcrypto",
  "futures",
  "hex",
+ "iota-common",
  "iota-config",
  "iota-data-ingestion-core",
  "iota-grpc-client",
@@ -7141,6 +7150,7 @@ dependencies = [
  "colored",
  "fastcrypto",
  "futures",
+ "iota-common",
  "iota-config",
  "iota-faucet",
  "iota-genesis-builder",
@@ -7293,6 +7303,7 @@ version = "1.22.0-alpha"
 dependencies = [
  "anyhow",
  "fastcrypto",
+ "iota-common",
  "iota-package-management",
  "iota-types",
  "iota-verifier-latest",
@@ -7372,6 +7383,7 @@ dependencies = [
  "futures",
  "governor",
  "iota-archival",
+ "iota-common",
  "iota-config",
  "iota-macros",
  "iota-metrics",
@@ -7693,6 +7705,7 @@ dependencies = [
  "clap",
  "futures",
  "http 1.4.0",
+ "iota-common",
  "iota-config",
  "iota-core",
  "iota-execution",
@@ -7957,6 +7970,7 @@ dependencies = [
  "expect-test",
  "flate2",
  "futures",
+ "iota-common",
  "iota-json-rpc-types",
  "iota-move-build",
  "iota-package-management",
@@ -7992,6 +8006,7 @@ dependencies = [
  "fs_extra",
  "hyper 1.8.1",
  "iota",
+ "iota-common",
  "iota-json-rpc-types",
  "iota-metrics",
  "iota-move",
@@ -8055,6 +8070,7 @@ dependencies = [
  "hyper 1.8.1",
  "indicatif",
  "integer-encoding",
+ "iota-common",
  "iota-config",
  "iota-macros",
  "iota-metrics",
@@ -8174,6 +8190,7 @@ version = "1.22.0-alpha"
 dependencies = [
  "anyhow",
  "clap",
+ "iota-common",
  "iota-storage",
  "iota-test-transaction-builder",
  "iota-types",
@@ -8240,6 +8257,7 @@ dependencies = [
  "indicatif",
  "inquire",
  "iota-archival",
+ "iota-common",
  "iota-config",
  "iota-core",
  "iota-genesis-builder",
@@ -8316,6 +8334,7 @@ dependencies = [
  "eyre",
  "fastcrypto",
  "http 1.4.0",
+ "iota-common",
  "iota-config",
  "iota-core",
  "iota-framework",
```

### crates/iota-archival/Cargo.toml
```diff
@@ -37,6 +37,7 @@ tempfile.workspace = true
 tokio = { workspace = true, features = ["test-util"] }
 
 # internal dependencies
+iota-common.workspace = true
 iota-macros.workspace = true
 iota-swarm-config.workspace = true
 move-binary-format.workspace = true
```

### crates/iota-archival/src/tests.rs
```diff
@@ -26,7 +26,6 @@ use iota_types::{
 use more_asserts as ma;
 use object_store::DynObjectStore;
 use prometheus::Registry;
-use tempfile::tempdir;
 
 use crate::{
     Manifest, read_manifest,
@@ -47,12 +46,6 @@ struct TestState {
     committee: CommitteeFixture,
 }
 
-fn temp_dir() -> std::path::PathBuf {
-    tempdir()
-        .expect("Failed to open temporary directory")
-        .keep()
-}
-
 async fn write_new_checkpoints_to_store(
     test_state: &TestState,
     store: SharedInMemoryStore,
@@ -164,7 +157,8 @@ async fn insert_checkpoints_and_verify_manifest(
 #[tokio::test]
 async fn test_archive_basic() -> Result<(), anyhow::Error> {
     let test_store = SharedInMemoryStore::default();
-    let test_state = setup_test_state(temp_dir()).await?;
+    let tmp_dir = iota_common::tempdir();
+    let test_state = setup_test_state(tmp_dir.path().to_path_buf()).await?;
     let kill = test_state.archive_writer.start(test_store.clone()).await?;
     insert_checkpoints_and_verify_manifest(&test_state, test_store, None).await?;
     kill.send(())?;
@@ -174,14 +168,16 @@ async fn test_archive_basic() -> Result<(), anyhow::Error> {
 #[tokio::test]
 async fn test_archive_resumes() -> Result<(), anyhow::Error> {
     let test_store = SharedInMemoryStore::default();
-    let test_state = setup_test_state(temp_dir()).await?;
+    let tmp_dir = iota_common::tempdir();
+    let test_state = setup_test_state(tmp_dir.path().to_path_buf()).await?;
     let kill = test_state.archive_writer.start(test_store.clone()).await?;
     let prev_checkpoint =
         insert_checkpoints_and_verify_manifest(&test_state, test_store.clone(), None).await?;
 
     // Kill the archive writer so we can restart it again
     drop(kill);
-    let test_state = setup_test_state(temp_dir()).await?;
+    let tmp_dir2 = iota_common::tempdir();
+    let test_state = setup_test_state(tmp_dir2.path().to_path_buf()).await?;
     let kill = test_state.archive_writer.start(test_store.clone()).await?;
     insert_checkpoints_and_verify_manifest(&test_state, test_store, prev_checkpoint).await?;
     kill.send(())?;
@@ -191,9 +187,10 @@ async fn test_archive_resumes() -> Result<(), anyhow::Error> {
 #[tokio::test]
 async fn test_manifest_serde() -> Result<()> {
     let original_manifest = Manifest::new(0, 100);
+    let tmp_dir = iota_common::tempdir();
     let remote_store = ObjectStoreConfig {
         object_store: Some(ObjectStoreType::File),
-        directory: Some(temp_dir()),
+        directory: Some(tmp_dir.path().to_path_buf()),
         ..Default::default()
     }
     .make()?;
@@ -206,7 +203,8 @@ async fn test_manifest_serde() -> Result<()> {
 #[tokio::test]
 async fn test_archive_reader_e2e() -> Result<(), anyhow::Error> {
     let test_store = SharedInMemoryStore::default();
-    let test_state = setup_test_state(temp_dir()).await?;
+    let tmp_dir = iota_common::tempdir();
+    let test_state = setup_test_state(tmp_dir.path().to_path_buf()).await?;
     let kill = test_state.archive_writer.start(test_store.clone()).await?;
     let mut latest_archived_checkpoint_seq_num = 0;
     while latest_archived_checkpoint_seq_num < 10 {
@@ -267,7 +265,8 @@ async fn test_archive_reader_e2e() -> Result<(), anyhow::Error> {
 #[tokio::test]
 async fn test_verify_archive_with_oneshot_store() -> Result<(), anyhow::Error> {
     let test_store = SharedInMemoryStore::default();
-    let test_state = setup_test_state(temp_dir()).await?;
+    let tmp_dir = iota_common::tempdir();
+    let test_state = setup_test_state(tmp_dir.path().to_path_buf()).await?;
     let kill = test_state.archive_writer.start(test_store.clone()).await?;
     let mut latest_archived_checkpoint_seq_num = 0;
     while latest_archived_checkpoint_seq_num < 10 {
@@ -315,7 +314,8 @@ async fn test_verify_archive_with_oneshot_store() -> Result<(), anyhow::Error> {
 #[tokio::test]
 async fn test_verify_archive_with_oneshot_store_bad_data() -> Result<(), anyhow::Error> {
     let test_store = SharedInMemoryStore::default();
-    let test_state = setup_test_state(temp_dir()).await?;
+    let tmp_dir = iota_common::tempdir();
+    let test_state = setup_test_state(tmp_dir.path().to_path_buf()).await?;
     let kill = test_state.archive_writer.start(test_store.clone()).await?;
     let mut latest_archived_checkpoint_seq_num = 0;
     while latest_archived_checkpoint_seq_num < 10 {
```

### crates/iota-aws-orchestrator/Cargo.toml
```diff
@@ -41,8 +41,12 @@ iota-swarm-config.workspace = true
 iota-types.workspace = true
 
 [dev-dependencies]
+# external dependencies
 tempfile.workspace = true
 
+# internal dependencies
+iota-common.workspace = true
+
 [[bin]]
 name = "iota-aws-orchestrator"
 path = "src/main.rs"
```

### crates/iota-aws-orchestrator/src/settings.rs
```diff
@@ -336,18 +336,17 @@ impl Settings {
     #[cfg(test)]
     pub fn new_for_test() -> Self {
         // Create a temporary public key file.
-        let mut path = tempfile::tempdir().unwrap().keep();
-        path.push("test_public_key.pub");
+        let test_public_key_path = iota_common::tempdir().keep().join("test_public_key.pub");
         let public_key = "This is a fake public key for tests";
-        fs::write(&path, public_key).unwrap();
+        fs::write(&test_public_key_path, public_key).unwrap();
 
         // Return set settings.
         Self {
             testbed_id: "testbed".into(),
             cloud_provider: CloudProvider::Aws,
             token_file: "/path/to/token/file".into(),
             ssh_private_key_file: "/path/to/private/key/file".into(),
-            ssh_public_key_file: Some(path),
+            ssh_public_key_file: Some(test_public_key_path),
             regions: vec!["London".into(), "New York".into()],
             node_specs: "small".into(),
             client_specs: "small".into(),
```

### crates/iota-common/src/random_util.rs
```diff
@@ -42,6 +42,7 @@ pub type TempDir = tempfile::TempDir;
 
 /// Creates a temporary directory with random name.
 /// Ensure the name is randomized even in simtests.
-pub fn tempdir() -> std::io::Result<TempDir> {
+pub fn tempdir() -> TempDir {
     nondeterministic!(tempfile::tempdir())
+        .expect("temporary directory should not fail to be created")
 }
```

### crates/iota-core/src/authority.rs
```diff
@@ -1342,6 +1342,8 @@ impl AuthorityState {
         certificate: &VerifiedExecutableTransaction,
         debug_dump_config: &StateDebugDumpConfig,
     ) -> IotaResult<PathBuf> {
+        // Fall back to the OS temp directory if no dump directory is configured.
+        // This is safe: dump files are named by transaction digest, so no collisions.
         let dump_dir = debug_dump_config
             .dump_file_directory
             .as_ref()
```

### crates/iota-core/src/authority/authority_per_epoch_store_pruner.rs
```diff
@@ -100,18 +100,19 @@ mod tests {
 
     #[tokio::test]
     async fn test_basic_epoch_pruner() {
-        let parent_directory = tempfile::tempdir().unwrap().keep();
+        let tmp_dir = iota_common::tempdir();
         let directories: Vec<_> = vec!["epoch_0", "epoch_1", "epoch_3", "epoch_4"]
             .into_iter()
-            .map(|name| parent_directory.join(name))
+            .map(|name| tmp_dir.path().join(name))
             .collect();
         for directory in &directories {
             fs::create_dir(directory).expect("failed to create directory");
         }
 
-        let pruned = AuthorityPerEpochStorePruner::prune_old_directories(&parent_directory, 2)
-            .await
-            .unwrap();
+        let pruned =
+            AuthorityPerEpochStorePruner::prune_old_directories(&tmp_dir.path().to_path_buf(), 2)
+                .await
+                .unwrap();
         assert_eq!(pruned, 2);
         assert_eq!(
             directories
```

### crates/iota-core/src/authority/authority_store_pruner.rs
```diff
@@ -1052,34 +1052,33 @@ mod tests {
     // Tests pruning old version of live objects.
     #[tokio::test]
     async fn test_pruning_objects() {
-        let path = tempfile::tempdir().unwrap().keep();
-        let to_keep = run_pruner(&path, 3, 2, 1000).await;
+        let tmp_dir = iota_common::tempdir();
+        let to_keep = run_pruner(tmp_dir.path(), 3, 2, 1000).await;
         assert_eq!(
             HashSet::from_iter(to_keep),
-            get_keys_after_pruning(&path).unwrap()
+            get_keys_after_pruning(tmp_dir.path()).unwrap()
         );
-        run_pruner(&tempfile::tempdir().unwrap().keep(), 3, 2, 1000).await;
     }
 
     // Tests pruning deleted objects (object tombstones).
     #[tokio::test]
     async fn test_pruning_tombstones() {
-        let path = tempfile::tempdir().unwrap().keep();
-        let to_keep = run_pruner(&path, 0, 0, 1000).await;
+        let tmp_dir = iota_common::tempdir();
+        let to_keep = run_pruner(tmp_dir.path(), 0, 0, 1000).await;
         assert_eq!(to_keep.len(), 0);
-        assert_eq!(get_keys_after_pruning(&path).unwrap().len(), 0);
+        assert_eq!(get_keys_after_pruning(tmp_dir.path()).unwrap().len(), 0);
 
-        let path = tempfile::tempdir().unwrap().keep();
-        let to_keep = run_pruner(&path, 3, 0, 1000).await;
+        let tmp_dir2 = iota_common::tempdir();
+        let to_keep = run_pruner(tmp_dir2.path(), 3, 0, 1000).await;
         assert_eq!(to_keep.len(), 0);
-        assert_eq!(get_keys_after_pruning(&path).unwrap().len(), 0);
+        assert_eq!(get_keys_after_pruning(tmp_dir2.path()).unwrap().len(), 0);
     }
 
     #[cfg(not(target_env = "msvc"))]
     #[tokio::test]
     async fn test_db_size_after_compaction() -> Result<(), anyhow::Error> {
-        let primary_path = tempfile::tempdir()?.keep();
-        let perpetual_db = Arc::new(AuthorityPerpetualTables::open(&primary_path, None));
+        let tmp_dir = iota_common::tempdir();
+        let perpetual_db = Arc::new(AuthorityPerpetualTables::open(tmp_dir.path(), None));
         let total_unique_object_ids = 10_000;
         let num_versions_per_object = 10;
         let ids = ObjectID::in_range(ObjectID::ZERO, total_unique_object_ids)?;
@@ -1111,7 +1110,7 @@ mod tests {
             size
         }
 
-        let db_path = primary_path.clone().join("perpetual");
+        let db_path = tmp_dir.path().join("perpetual");
         let start = ObjectKey(ObjectID::ZERO, SequenceNumber::MIN_VALID_INCL);
         let end = ObjectKey(ObjectID::MAX, SequenceNumber::MAX_VALID_EXCL);
 
```

### crates/iota-core/src/authority/test_authority_builder.rs
```diff
@@ -16,18 +16,13 @@ use iota_config::{
     },
     transaction_deny_config::TransactionDenyConfig,
 };
-use iota_macros::nondeterministic;
 use iota_network::randomness;
 use iota_protocol_config::{Chain, ProtocolConfig};
 use iota_swarm_config::{genesis_config::AccountConfig, network_config::NetworkConfig};
 use iota_types::{
-    base_types::{AuthorityName, ObjectID},
-    crypto::AuthorityKeyPair,
-    digests::ChainIdentifier,
-    executable_transaction::VerifiedExecutableTransaction,
-    iota_system_state::IotaSystemStateTrait,
-    object::Object,
-    supported_protocol_versions::SupportedProtocolVersions,
+    base_types::AuthorityName, crypto::AuthorityKeyPair, digests::ChainIdentifier,
+    executable_transaction::VerifiedExecutableTransaction, iota_system_state::IotaSystemStateTrait,
+    object::Object, supported_protocol_versions::SupportedProtocolVersions,
     transaction::VerifiedTransaction,
 };
 use prometheus::Registry;
@@ -208,21 +203,19 @@ impl<'a> TestAuthorityBuilder<'a> {
         let local_network_config = local_network_config_builder.build();
         let genesis = &self.genesis.unwrap_or(&local_network_config.genesis);
         let genesis_committee = genesis.committee().unwrap();
-        let path = self.store_base_path.unwrap_or_else(|| {
-            let dir = std::env::temp_dir();
-            let store_base_path =
-                dir.join(format!("DB_{:?}", nondeterministic!(ObjectID::random())));
-            std::fs::create_dir(&store_base_path).unwrap();
-            store_base_path
-        });
+        let storage_dir = self
+            .store_base_path
+            .unwrap_or_else(|| iota_common::tempdir().keep());
         let mut config = local_network_config.validator_configs()[0].clone();
         let registry = Registry::new();
         let mut pruner_db = None;
         if config
             .authority_store_pruning_config
             .enable_compaction_filter
         {
-            pruner_db = Some(Arc::new(AuthorityPrunerTables::open(&path.join("store"))));
+            pruner_db = Some(Arc::new(AuthorityPrunerTables::open(
+                &storage_dir.join("store"),
+            )));
         }
         let compaction_filter = pruner_db
             .clone()
@@ -236,7 +229,7 @@ impl<'a> TestAuthorityBuilder<'a> {
                     ..Default::default()
                 };
                 let perpetual_tables = Arc::new(AuthorityPerpetualTables::open(
-                    &path.join("store"),
+                    &storage_dir.join("store"),
                     Some(perpetual_tables_options),
                 ));
                 // unwrap ok - for testing only.
@@ -281,7 +274,7 @@ impl<'a> TestAuthorityBuilder<'a> {
         .unwrap();
         let expensive_safety_checks = self.expensive_safety_checks.unwrap_or_default();
 
-        let checkpoint_store = CheckpointStore::new(&path.join("checkpoints"));
+        let checkpoint_store = CheckpointStore::new(&storage_dir.join("checkpoints"));
         let backpressure_manager =
             BackpressureManager::new_from_checkpoint_store(&checkpoint_store);
 
@@ -302,7 +295,7 @@ impl<'a> TestAuthorityBuilder<'a> {
         let epoch_store = AuthorityPerEpochStore::new(
             name,
             Arc::new(genesis_committee.clone()),
-            &path.join("store"),
+            &storage_dir.join("store"),
             None,
             EpochMetrics::new(&registry),
             epoch_start_configuration,
@@ -319,7 +312,7 @@ impl<'a> TestAuthorityBuilder<'a> {
         )
         .expect("failed to create authority per epoch store");
         let committee_store = Arc::new(CommitteeStore::new(
-            path.join("epochs"),
+            storage_dir.join("epochs"),
             &genesis_committee,
             None,
         ));
@@ -335,7 +328,7 @@ impl<'a> TestAuthorityBuilder<'a> {
             None
         } else {
             Some(Arc::new(IndexStore::new(
-                path.join("indexes"),
+                storage_dir.join("indexes"),
                 &registry,
                 epoch_store
                     .protocol_config()
@@ -347,7 +340,7 @@ impl<'a> TestAuthorityBuilder<'a> {
         } else {
             Some(Arc::new(
                 GrpcIndexesStore::new(
-                    path.join(GRPC_INDEXES_DIR),
+                    storage_dir.join(GRPC_INDEXES_DIR),
                     Arc::clone(&authority_store),
                     &checkpoint_store,
                 )
```

### crates/iota-core/src/authority/transaction_deferral.rs
```diff
@@ -122,10 +122,10 @@ mod object_cost_tests {
         }
 
         // get a tempdir
-        let tempdir = tempfile::tempdir().unwrap();
+        let tmp_dir = iota_common::tempdir();
 
         let db = TestDB::open_tables_read_write(
-            tempdir.path().to_owned(),
+            tmp_dir.path().to_owned(),
             MetricConf::new("test_db"),
             None,
             None,
@@ -163,10 +163,10 @@ mod object_cost_tests {
         }
 
         // get a tempdir
-        let tempdir = tempfile::tempdir().unwrap();
+        let tmp_dir = iota_common::tempdir();
 
         let db = TestDB::open_tables_read_write(
-            tempdir.path().to_owned(),
+            tmp_dir.path().to_owned(),
             MetricConf::new("test_db"),
             None,
             None,
```

### crates/iota-core/src/checkpoints/checkpoint_executor/tests.rs
```diff
@@ -16,7 +16,6 @@ use iota_types::{
     },
     supported_protocol_versions::SupportedProtocolVersions,
 };
-use tempfile::tempdir;
 use tokio::time::timeout;
 use typed_store::Map;
 
@@ -38,8 +37,8 @@ pub async fn test_checkpoint_executor_crash_recovery() {
     telemetry_subscribers::init_for_testing();
 
     let buffer_size = num_cpus::get() * 2;
-    let tempdir = tempdir().unwrap();
-    let checkpoint_store = CheckpointStore::new(tempdir.path());
+    let tmp_dir = iota_common::tempdir();
+    let checkpoint_store = CheckpointStore::new(tmp_dir.path());
 
     let (state, executor, accumulator, committee): (
         Arc<AuthorityState>,
@@ -132,8 +131,8 @@ pub async fn test_checkpoint_executor_crash_recovery() {
 pub async fn test_checkpoint_executor_cross_epoch() {
     let buffer_size = 10;
     let num_to_sync_per_epoch = buffer_size * 2;
-    let tempdir = tempdir().unwrap();
-    let checkpoint_store = CheckpointStore::new(tempdir.path());
+    let tmp_dir = iota_common::tempdir();
+    let checkpoint_store = CheckpointStore::new(tmp_dir.path());
 
     let (authority_state, executor, accumulator, first_committee): (
         Arc<AuthorityState>,
@@ -311,8 +310,8 @@ pub async fn test_checkpoint_executor_cross_epoch() {
 #[tokio::test]
 #[ignore]
 pub async fn test_reconfig_crash_recovery() {
-    let tempdir = tempdir().unwrap();
-    let checkpoint_store = CheckpointStore::new(tempdir.path());
+    let tmp_dir = iota_common::tempdir();
+    let checkpoint_store = CheckpointStore::new(tmp_dir.path());
 
     // new Node (syncing from checkpoint 0)
     let (authority_state, executor, accumulator, first_committee): (
```
