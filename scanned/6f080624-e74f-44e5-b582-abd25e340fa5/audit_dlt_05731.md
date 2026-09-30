# [?] fix(state): Write database format version to disk atomically to avoid a rare panic (#8795)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2024-08-29
Source: https://github.com/ZcashFoundation/zebra/commit/0ef9987e9eeaae4d9af121264f66a866501d4cee
Type: security-commit

## Details
fix(state): Write database format version to disk atomically to avoid a rare panic (#8795)

* Splits `atomic_write_to_tmp_file` out of `zebra_network::Config::update_peer_cache`

* Uses the new `atomic_write_to_tmp_file` fn in `update_peer_cache()`

* Replaces repetitive code for getting the default peer and state cache directories with `default_cache_dir()`

* Converts `atomic_write_to_tmp_file` to a blocking function and adds `spawn_atomic_write_to_tmp_file` for use in async environments.

* Uses `atomic_write_to_tmp_file` to write database versions to disk

* Removes `spawn_atomic_write_to_tmp_file()` and inlines its body at its callsite to avoid adding tokio as a dependency of zebra-chain.

* Apply suggestions from code review

Co-authored-by: Marek <mail@marek.onl>

---------

Co-authored-by: Marek <mail@marek.onl>

## Patch
### Cargo.lock
```diff
@@ -5964,6 +5964,7 @@ dependencies = [
  "chrono",
  "color-eyre",
  "criterion",
+ "dirs",
  "ed25519-zebra",
  "equihash 0.2.0 (registry+https://github.com/rust-lang/crates.io-index)",
  "futures",
@@ -5996,6 +5997,7 @@ dependencies = [
  "sha2",
  "spandoc",
  "static_assertions",
+ "tempfile",
  "thiserror",
  "tinyvec",
  "tokio",
```

### zebra-chain/Cargo.toml
```diff
@@ -81,6 +81,8 @@ group = "0.13.0"
 incrementalmerkletree.workspace = true
 jubjub = "0.10.0"
 lazy_static = "1.4.0"
+tempfile = "3.11.0"
+dirs = "5.0.1"
 num-integer = "0.1.46"
 primitive-types = "0.12.2"
 rand_core = "0.6.4"
```

### zebra-chain/src/common.rs
```diff
@@ -0,0 +1,71 @@
+//! Common functions used in Zebra.
+
+use std::{
+    ffi::OsString,
+    fs,
+    io::{self, Write},
+    path::PathBuf,
+};
+
+use tempfile::PersistError;
+
+/// Returns Zebra's default cache directory path.
+pub fn default_cache_dir() -> PathBuf {
+    dirs::cache_dir()
+        .unwrap_or_else(|| std::env::current_dir().unwrap().join("cache"))
+        .join("zebra")
+}
+
+/// Accepts a target file path and a byte-slice.
+///
+/// Atomically writes the byte-slice to a file to avoid corrupting the file if Zebra
+/// panics, crashes, or exits while the file is being written, or if multiple Zebra instances
+/// try to read and write the same file.
+///
+/// Returns the provided file path if successful.
+///
+/// # Concurrency
+///
+/// This function blocks on filesystem operations and should be called in a blocking task
+/// when calling from an async environment.
+///
+/// # Panics
+///
+/// If the provided `file_path` is a directory path.
+pub fn atomic_write(
+    file_path: PathBuf,
+    data: &[u8],
+) -> io::Result<Result<PathBuf, PersistError<fs::File>>> {
+    // Get the file's parent directory, or use Zebra's default cache directory
+    let file_dir = file_path
+        .parent()
+        .map(|p| p.to_owned())
+        .unwrap_or_else(default_cache_dir);
+
+    // Create the directory if needed.
+    fs::create_dir_all(&file_dir)?;
+
+    // Give the temporary file a similar name to the permanent file,
+    // but hide it in directory listings.
+    let mut tmp_file_prefix: OsString = ".tmp.".into();
+    tmp_file_prefix.push(
+        file_path
+            .file_name()
+            .expect("file path must have a file name"),
+    );
+
+    // Create the temporary file in the same directory as the permanent file,
+    // so atomic filesystem operations are possible.
+    let mut tmp_file = tempfile::Builder::new()
+        .prefix(&tmp_file_prefix)
+        .tempfile_in(file_dir)?;
+
+    tmp_file.write_all(data)?;
+
+    // Atomically write the temp file to `file_path`.
+    let persist_result = tmp_file
+        .persist(&file_path)
+        // Drops the temp file and returns the file path.
+        .map(|_| file_path);
+    Ok(persist_result)
+}
```

### zebra-chain/src/lib.rs
```diff
@@ -22,6 +22,7 @@ pub mod amount;
 pub mod block;
 pub mod chain_sync_status;
 pub mod chain_tip;
+pub mod common;
 pub mod diagnostic;
 pub mod error;
 pub mod fmt;
```

### zebra-network/src/config.rs
```diff
@@ -2,19 +2,18 @@
 
 use std::{
     collections::HashSet,
-    ffi::OsString,
     io::{self, ErrorKind},
     net::{IpAddr, SocketAddr},
     time::Duration,
 };
 
 use indexmap::IndexSet;
 use serde::{de, Deserialize, Deserializer};
-use tempfile::NamedTempFile;
-use tokio::{fs, io::AsyncWriteExt};
-use tracing::Span;
+use tokio::fs;
 
+use tracing::Span;
 use zebra_chain::{
+    common::atomic_write,
     parameters::{
         testnet::{self, ConfiguredActivationHeights, ConfiguredFundingStreams},
         Magic, Network, NetworkKind,
@@ -503,90 +502,36 @@ impl Config {
         // Make a newline-separated list
         let peer_data = peer_list.join("\n");
 
-        // Write to a temporary file, so the cache is not corrupted if Zebra shuts down or crashes
-        // at the same time.
-        //
-        // # Concurrency
-        //
-        // We want to use async code to avoid blocking the tokio executor on filesystem operations,
-        // but `tempfile` is implemented using non-asyc methods. So we wrap its filesystem
-        // operations in `tokio::spawn_blocking()`.
-        //
-        // TODO: split this out into an atomic_write_to_tmp_file() method if we need to re-use it
-
-        // Create the peer cache directory if needed
-        let peer_cache_dir = peer_cache_file
-            .parent()
-            .expect("cache path always has a network directory")
-            .to_owned();
-        tokio::fs::create_dir_all(&peer_cache_dir).await?;
-
-        // Give the temporary file a similar name to the permanent cache file,
-        // but hide it in directory listings.
-        let mut tmp_peer_cache_prefix: OsString = ".tmp.".into();
-        tmp_peer_cache_prefix.push(
-            peer_cache_file
-                .file_name()
-                .expect("cache file always has a file name"),
-        );
-
-        // Create the temporary file.
-        // Do blocking filesystem operations on a dedicated thread.
+        // Write the peer cache file atomically so the cache is not corrupted if Zebra shuts down
+        // or crashes.
         let span = Span::current();
-        let tmp_peer_cache_file = tokio::task::spawn_blocking(move || {
-            span.in_scope(move || {
-                // Put the temporary file in the same directory as the permanent file,
-                // so atomic filesystem operations are possible.
-                tempfile::Builder::new()
-                    .prefix(&tmp_peer_cache_prefix)
-                    .tempfile_in(peer_cache_dir)
-            })
+        let write_result = tokio::task::spawn_blocking(move || {
+            span.in_scope(move || atomic_write(peer_cache_file, peer_data.as_bytes()))
         })
         .await
-        .expect("unexpected panic creating temporary peer cache file")?;
-
-        // Write the list to the file asynchronously, by extracting the inner file, using it,
-        // then combining it back into a type that will correctly drop the file on error.
-        let (tmp_peer_cache_file, tmp_peer_cache_path) = tmp_peer_cache_file.into_parts();
-        let mut tmp_peer_cache_file = tokio::fs::File::from_std(tmp_peer_cache_file);
-        tmp_peer_cache_file.write_all(peer_data.as_bytes()).await?;
-
-        let tmp_peer_cache_file =
-            NamedTempFile::from_parts(tmp_peer_cache_file, tmp_peer_cache_path);
-
-        // Atomically replace the current cache with the temporary cache.
-        // Do blocking filesystem operations on a dedicated thread.
-        let span = Span::current();
-        tokio::task::spawn_blocking(move || {
-            span.in_scope(move || {
-                let result = tmp_peer_cache_file.persist(&peer_cache_file);
-
-                // Drops the temp file if needed
-                match result {
-                    Ok(_temp_file) => {
-                        info!(
-                            cached_ip_count = ?peer_list.len(),
-                            ?peer_cache_file,
-                            "updated cached peer IP addresses"
-                        );
+        .expect("could not write the peer cache file")?;
+
+        match write_result {
+            Ok(peer_cache_file) => {
+                info!(
+                    cached_ip_count = ?peer_list.len(),
+                    ?peer_cache_file,
+                    "updated cached peer IP addresses"
+                );
 
-                        for ip in &peer_list {
-                            metrics::counter!(
-                                "zcash.net.peers.cache",
-                                "cache" => peer_cache_file.display().to_string(),
-                                "remote_ip" => ip.to_string()
-                            )
-                            .increment(1);
-                        }
-
-                        Ok(())
-                    }
-                    Err(error) => Err(error.error),
+                for ip in &peer_list {
+                    metrics::counter!(
+                        "zcash.net.peers.cache",
+                        "cache" => peer_cache_file.display().to_string(),
+                        "remote_ip" => ip.to_string()
+                    )
+                    .increment(1);
                 }
-            })
-        })
-        .await
-        .expect("unexpected panic making temporary peer cache file permanent")
+
+                Ok(())
+            }
+            Err(error) => Err(error.error),
+        }
     }
 }
 
```

### zebra-network/src/config/cache_dir.rs
```diff
@@ -2,7 +2,7 @@
 
 use std::path::{Path, PathBuf};
 
-use zebra_chain::parameters::Network;
+use zebra_chain::{common::default_cache_dir, parameters::Network};
 
 /// A cache directory config field.
 ///
@@ -56,12 +56,7 @@ impl CacheDir {
     /// Returns the `zebra-network` base cache directory, if enabled.
     pub fn cache_dir(&self) -> Option<PathBuf> {
         match self {
-            Self::IsEnabled(is_enabled) => is_enabled.then(|| {
-                dirs::cache_dir()
-                    .unwrap_or_else(|| std::env::current_dir().unwrap().join("cache"))
-                    .join("zebra")
-            }),
-
+            Self::IsEnabled(is_enabled) => is_enabled.then(default_cache_dir),
             Self::CustomPath(cache_dir) => Some(cache_dir.to_owned()),
         }
     }
```

### zebra-state/src/config.rs
```diff
@@ -12,7 +12,7 @@ use serde::{Deserialize, Serialize};
 use tokio::task::{spawn_blocking, JoinHandle};
 use tracing::Span;
 
-use zebra_chain::parameters::Network;
+use zebra_chain::{common::default_cache_dir, parameters::Network};
 
 use crate::{
     constants::{DATABASE_FORMAT_VERSION_FILE_NAME, RESTORABLE_DB_VERSIONS, STATE_DATABASE_KIND},
@@ -173,12 +173,8 @@ impl Config {
 
 impl Default for Config {
     fn default() -> Self {
-        let cache_dir = dirs::cache_dir()
-            .unwrap_or_else(|| std::env::current_dir().unwrap().join("cache"))
-            .join("zebra");
-
         Self {
-            cache_dir,
+            cache_dir: default_cache_dir(),
             ephemeral: false,
             delete_old_database: true,
             debug_stop_at_height: None,
@@ -471,6 +467,8 @@ pub(crate) use hidden::{
 pub(crate) mod hidden {
     #![allow(dead_code)]
 
+    use zebra_chain::common::atomic_write;
+
     use super::*;
 
     /// Writes `changed_version` to the on-disk state database after the format is changed.
@@ -512,10 +510,9 @@ pub(crate) mod hidden {
 
         let version = format!("{}.{}", changed_version.minor, changed_version.patch);
 
-        // # Concurrency
-        //
-        // The caller handles locking for this file write.
-        fs::write(version_path, version.as_bytes())?;
+        // Write the version file atomically so the cache is not corrupted if Zebra shuts down or
+        // crashes.
+        atomic_write(version_path, version.as_bytes())??;
 
         Ok(())
     }
```
