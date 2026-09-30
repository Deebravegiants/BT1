# [?] fix: RUSTSEC-2025-0134 (#9636)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-02-06
Source: https://github.com/iotaledger/iota/commit/f00d90937e7a42fb3dfd6e5c03561c9d8aab6b29
Type: security-commit

## Details
fix: RUSTSEC-2025-0134 (#9636)

# Description of change

This PR updates all dependencies that use the deprecated
`rustls-pemfile`.

## How the change has been tested

- [x] Basic tests (linting, compilation, formatting, unit/integration
tests)
- [ ] Patch-specific tests (correctness, functionality coverage)
- [ ] I have added tests that prove my fix is effective or that my
feature works
- [ ] I have checked that new and existing unit tests pass locally with
my changes

## Patch
### Cargo.toml
```diff
@@ -240,11 +240,11 @@ async-graphql = { version = "7.1.0", default-features = false }
 async-recursion = "1.0.4"
 async-stream = "0.3.6"
 async-trait = "0.1.61"
-aws-config = "1.5.6"
-aws-sdk-dynamodb = "1.42"
+aws-config = "1.8"
+aws-sdk-dynamodb = "1.103"
 axum = { version = "0.8", default-features = false, features = ["tokio", "http2", "json", "matched-path", "original-uri", "form", "query", "ws", "macros"] }
 axum-extra = { version = "0.10", features = ["typed-header"] }
-axum-server = { git = "https://github.com/bmwill/axum-server.git", rev = "f44323e271afdd1365fd0c8b0a4c0bbdf4956cb7", version = "0.6", default-features = false, features = ["tls-rustls"] }
+axum-server = { version = "0.8", default-features = false, features = ["tls-rustls"] }
 backoff = { version = "0.4.0", features = ["futures", "futures-core", "pin-project-lite", "tokio", "tokio_1"] }
 base64 = "0.21.2"
 base64-url = "2"
@@ -295,7 +295,7 @@ http-body = "1.0"
 http-body-util = "0.1.2"
 humantime = "2.1.0"
 hyper = "1"
-hyper-util = { version = "0.1.4", features = ["tokio", "server-auto", "service"] }
+hyper-util = { version = "0.1.20", features = ["tokio", "server-auto", "service"] }
 im = "15"
 indexmap = { version = "2.11.0", features = ["serde"] }
 indicatif = "0.18.3"
@@ -317,7 +317,7 @@ num-bigint = "0.4.4"
 num-rational = "0.4"
 num_cpus = "1.15.0"
 num_enum = "0.7"
-object_store = { version = "0.10", features = ["aws", "gcp", "azure", "http"] }
+object_store = { version = "0.13", features = ["aws", "gcp", "azure", "http"] }
 once_cell = "1.18.0"
 p256 = { version = "0.13.2", features = ["ecdsa"] }
 packable = { version = "0.8.3", features = ["io"], default-features = false }
```

### crates/iota-analytics-indexer/Cargo.toml
```diff
@@ -16,7 +16,7 @@ clap.workspace = true
 csv.workspace = true
 eyre.workspace = true
 fastcrypto = { workspace = true, features = ["copy_key"] }
-gcp-bigquery-client = "=0.18.0"
+gcp-bigquery-client = "0.28.0"
 num_enum.workspace = true
 object_store.workspace = true
 parquet = "53.1"
```

### crates/iota-analytics-indexer/src/lib.rs
```diff
@@ -7,7 +7,10 @@ use std::{ops::Range, path::PathBuf, sync::Arc};
 use anyhow::{Result, anyhow, bail};
 use arrow_array::Int32Array;
 use clap::*;
-use gcp_bigquery_client::{Client, model::query_request::QueryRequest};
+use gcp_bigquery_client::{
+    Client,
+    model::{query_request::QueryRequest, query_response::ResultSet},
+};
 use iota_config::object_storage_config::ObjectStoreConfig;
 use iota_data_ingestion_core::Worker;
 use iota_storage::object_store::util::{
@@ -241,11 +244,12 @@ impl BQMaxCheckpointReader {
 #[async_trait::async_trait]
 impl MaxCheckpointReader for BQMaxCheckpointReader {
     async fn max_checkpoint(&self) -> Result<i64> {
-        let mut result = self
+        let query_response = self
             .client
             .job()
             .query(&self.project_id, QueryRequest::new(&self.query))
             .await?;
+        let mut result = ResultSet::new_from_query_response(query_response);
         if result.next_row() {
             let max_checkpoint = result.get_i64(0)?.ok_or(anyhow!("no rows returned"))?;
             Ok(max_checkpoint)
```

### crates/iota-aws-orchestrator/Cargo.toml
```diff
@@ -10,9 +10,9 @@ publish = false
 # external dependencies
 async-trait.workspace = true
 aws-config.workspace = true
-aws-runtime = "1.4"
-aws-sdk-ec2 = "1.72"
-aws-smithy-runtime-api = "1.7"
+aws-runtime = "1.5"
+aws-sdk-ec2 = "1"
+aws-smithy-runtime-api = "1.11"
 chrono.workspace = true
 clap.workspace = true
 color-eyre = "0.6"
@@ -21,10 +21,9 @@ eyre.workspace = true
 futures.workspace = true
 prettytable-rs = "0.10"
 prometheus-parse = "0.2"
-rand = "0.9.2"
+rand.workspace = true
 reqwest.workspace = true
-russh = "0.44"
-russh-keys = "0.44"
+russh = "0.57"
 serde.workspace = true
 serde_json.workspace = true
 thiserror.workspace = true
```

### crates/iota-aws-orchestrator/src/error.rs
```diff
@@ -61,7 +61,7 @@ pub enum SshError {
     #[error("Failed to load private key for {address}: {error}")]
     PrivateKeyError {
         address: SocketAddr,
-        error: russh_keys::Error,
+        error: russh::keys::Error,
     },
 
     #[error("Failed to create ssh session with {address}: {error}")]
```

### crates/iota-aws-orchestrator/src/net_latency/latency_matrix_builder.rs
```diff
@@ -41,7 +41,7 @@ pub struct LatencyMatrixBuilder {
     matrix: Vec<Vec<u16>>,
 }
 
-use rand::{Rng, rng};
+use rand::{Rng, thread_rng};
 
 pub fn generate_block_matrix(n: usize, k: usize) -> Vec<Vec<bool>> {
     let k = k / 2;
@@ -103,11 +103,11 @@ impl LatencyMatrixBuilder {
     }
 
     fn fill_geographical(&mut self) {
-        let mut rng = rng();
+        let mut rng = thread_rng();
         let n = self.matrix.len();
 
         let positions: Vec<(f64, f64)> = (0..n)
-            .map(|_| (rng.random::<f64>(), rng.random::<f64>()))
+            .map(|_| (rng.gen::<f64>(), rng.gen::<f64>()))
             .collect();
 
         for i in 0..n {
```

### crates/iota-aws-orchestrator/src/ssh.rs
```diff
@@ -12,8 +12,7 @@ use std::{
 
 use async_trait::async_trait;
 use futures::future::try_join_all;
-use russh::{Channel, client, client::Msg};
-use russh_keys::key;
+use russh::{Channel, client, client::Msg, keys::PrivateKeyWithHashAlg};
 use tokio::{task::JoinHandle, time::sleep};
 
 use crate::{
@@ -351,11 +350,12 @@ struct Session {}
 impl client::Handler for Session {
     type Error = russh::Error;
 
-    async fn check_server_key(
+    #[allow(clippy::manual_async_fn)]
+    fn check_server_key(
         &mut self,
-        _server_public_key: &key::PublicKey,
-    ) -> Result<bool, Self::Error> {
-        Ok(true)
+        _server_public_key: &russh::keys::PublicKey,
+    ) -> impl std::future::Future<Output = Result<bool, Self::Error>> + Send {
+        async { Ok(true) }
     }
 }
 
@@ -381,8 +381,15 @@ impl SshConnection {
         inactivity_timeout: Option<Duration>,
         retries: Option<usize>,
     ) -> SshResult<Self> {
-        let key = russh_keys::load_secret_key(private_key_file, None)
-            .map_err(|error| SshError::PrivateKeyError { address, error })?;
+        let key_bytes = std::fs::read(private_key_file).map_err(|e| SshError::PrivateKeyError {
+            address,
+            error: russh::keys::Error::IO(e),
+        })?;
+        let key = russh::keys::decode_secret_key(&String::from_utf8_lossy(&key_bytes), None)
+            .map_err(|_e| SshError::PrivateKeyError {
+                address,
+                error: russh::keys::Error::CouldNotReadKey,
+            })?;
 
         let config = client::Config {
             inactivity_timeout: inactivity_timeout.or(Some(Self::DEFAULT_TIMEOUT)),
@@ -393,8 +400,9 @@ impl SshConnection {
             .await
             .map_err(|error| SshError::ConnectionError { address, error })?;
 
+        let key_with_hash = PrivateKeyWithHashAlg::new(Arc::new(key), None);
         let _auth_res = session
-            .authenticate_publickey(username, Arc::new(key))
+            .authenticate_publickey(username, key_with_hash)
             .await
             .map_err(|error| SshError::SessionError { address, error })?;
 
```

### crates/iota-core/src/db_checkpoint_handler.rs
```diff
@@ -15,7 +15,7 @@ use iota_storage::object_store::util::{
     copy_recursively, find_all_dirs_with_epoch_prefix, find_missing_epochs_dirs,
     path_to_filesystem, put, run_manifest_update_loop, write_snapshot_manifest,
 };
-use object_store::{DynObjectStore, path::Path};
+use object_store::{DynObjectStore, ObjectStoreExt, path::Path};
 use prometheus::{IntGauge, Registry, register_int_gauge_with_registry};
 use tracing::{debug, error, info};
 
```

### crates/iota-data-ingestion-core/src/reader/fetch.rs
```diff
@@ -15,7 +15,7 @@ use iota_storage::blob::Blob;
 use iota_types::messages_checkpoint::CheckpointSequenceNumber;
 #[cfg(not(target_os = "macos"))]
 use notify::{RecommendedWatcher, RecursiveMode};
-use object_store::{ObjectStore, path::Path as ObjectStorePath};
+use object_store::{ObjectStore, ObjectStoreExt, path::Path as ObjectStorePath};
 use tracing::{debug, info};
 
 use crate::{
```

### crates/iota-data-ingestion/src/workers/archival.rs
```diff
@@ -23,7 +23,7 @@ use iota_types::{
     full_checkpoint_content::CheckpointData,
     messages_checkpoint::{CheckpointSequenceNumber, FullCheckpointContents},
 };
-use object_store::{ObjectStore, path::Path};
+use object_store::{ObjectStore, ObjectStoreExt, path::Path};
 use serde::{Deserialize, Serialize};
 
 use crate::workers::RelayWorker;
```

### crates/iota-data-ingestion/src/workers/blob.rs
```diff
@@ -16,7 +16,7 @@ use iota_types::{
     committee::EpochId, full_checkpoint_content::CheckpointData,
     messages_checkpoint::CheckpointSequenceNumber,
 };
-use object_store::{DynObjectStore, MultipartUpload, ObjectStore, path::Path};
+use object_store::{DynObjectStore, MultipartUpload, ObjectStore, ObjectStoreExt, path::Path};
 use serde::{Deserialize, Deserializer, Serialize};
 use tokio::sync::Mutex;
 
```
