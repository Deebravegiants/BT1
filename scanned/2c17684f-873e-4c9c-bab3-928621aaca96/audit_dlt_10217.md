# [?] Fix spurious test suite crashes related to tracing

## Summary
Severity: Unknown
Chain: Penumbra
Component: penumbra-zone/penumbra
Published: 2023-10-18
Source: https://github.com/penumbra-zone/penumbra/commit/e08116538a080df9b0c63d511cd19fa3fe742b17
Type: security-commit

## Details
Fix spurious test suite crashes related to tracing

## Patch
### Cargo.lock
```diff
@@ -5774,7 +5774,7 @@ dependencies = [
 
 [[package]]
 name = "penumbra-wasm"
-version = "0.63.0-preview-2"
+version = "0.62.0"
 dependencies = [
  "anyhow",
  "ark-ff",
```

### crates/misc/tct-visualize/src/bin/tct-live-edit.rs
```diff
@@ -42,7 +42,7 @@ struct Args {
 
 #[tokio::main]
 async fn main() -> anyhow::Result<()> {
-    tracing_subscriber::fmt::init();
+    let _ = tracing_subscriber::fmt::try_init();
     let args = Args::parse();
     let rng = rand::rngs::OsRng;
 
```

### crates/storage/src/tests.rs
```diff
@@ -20,7 +20,7 @@ async fn delete_nonexistent_key() -> anyhow::Result<()> {
 /// the next Storage::load() call is made. This is fixed by `Storage::release()`
 /// which mimicks the behavior of an async drop (releasing resources).
 async fn db_lock_is_released() -> anyhow::Result<()> {
-    tracing_subscriber::fmt::init();
+    let _ = tracing_subscriber::fmt::try_init();
     let tmpdir = tempfile::tempdir()?;
 
     let storage = Storage::load(tmpdir.path().to_owned()).await?;
@@ -45,7 +45,7 @@ async fn db_lock_is_released() -> anyhow::Result<()> {
 
 #[tokio::test]
 async fn simple_flow() -> anyhow::Result<()> {
-    tracing_subscriber::fmt::init();
+    let _ = tracing_subscriber::fmt::try_init();
     let tmpdir = tempfile::tempdir()?;
 
     // Initialize an empty Storage in the new directory
@@ -803,7 +803,7 @@ async fn simple_flow() -> anyhow::Result<()> {
 /// - queries with a prefix, a start key, and no end key
 /// - queries with a prefix, no start key, and an end key
 async fn range_queries_basic() -> anyhow::Result<()> {
-    tracing_subscriber::fmt::init();
+    let _ = tracing_subscriber::fmt::try_init();
     let tmpdir = tempfile::tempdir()?;
     let storage = Storage::load(tmpdir.path().to_owned()).await?;
 
@@ -1134,7 +1134,7 @@ async fn range_queries_basic() -> anyhow::Result<()> {
 #[tokio::test]
 /// Test that overwrites work correctly, and that we can read the latest value.
 async fn range_query_overwrites() -> anyhow::Result<()> {
-    tracing_subscriber::fmt::init();
+    let _ = tracing_subscriber::fmt::try_init();
     let tmpdir = tempfile::tempdir()?;
 
     let storage = Storage::load(tmpdir.path().to_owned()).await?;
@@ -1151,7 +1151,7 @@ async fn range_query_overwrites() -> anyhow::Result<()> {
 /// Test that inserting a value that precedes the peeked value works.
 async fn range_query_prepend_peeked_value() -> anyhow::Result<()> {
     use crate::StateWrite;
-    tracing_subscriber::fmt::init();
+    let _ = tracing_subscriber::fmt::try_init();
     let tmpdir = tempfile::tempdir()?;
 
     let storage = Storage::load(tmpdir.path().to_owned()).await?;
@@ -1229,7 +1229,7 @@ async fn range_query_prepend_peeked_value() -> anyhow::Result<()> {
 #[tokio::test]
 /// Test that specifying an inverted range does not work.
 async fn range_query_ordering() -> anyhow::Result<()> {
-    tracing_subscriber::fmt::init();
+    let _ = tracing_subscriber::fmt::try_init();
     let tmpdir = tempfile::tempdir()?;
 
     let storage = Storage::load(tmpdir.path().to_owned()).await?;
@@ -1292,7 +1292,7 @@ async fn range_query_ordering() -> anyhow::Result<()> {
 #[tokio::test]
 /// Test that passing in an absurd range does not work.
 async fn range_query_bad_range() -> anyhow::Result<()> {
-    tracing_subscriber::fmt::init();
+    let _ = tracing_subscriber::fmt::try_init();
     let tmpdir = tempfile::tempdir()?;
 
     let storage = Storage::load(tmpdir.path().to_owned()).await?;
@@ -1322,7 +1322,7 @@ async fn range_query_bad_range() -> anyhow::Result<()> {
 async fn range_query_storage_basic() -> anyhow::Result<()> {
     use crate::read::StateRead;
     use crate::write::StateWrite;
-    tracing_subscriber::fmt::init();
+    let _ = tracing_subscriber::fmt::try_init();
     let tmpdir = tempfile::tempdir()?;
 
     let storage = Storage::load(tmpdir.path().to_owned()).await?;
@@ -1408,7 +1408,7 @@ async fn range_query_storage_basic() -> anyhow::Result<()> {
 async fn range_query_storage() -> anyhow::Result<()> {
     use crate::read::StateRead;
     use crate::write::StateWrite;
-    tracing_subscriber::fmt::init();
+    let _ = tracing_subscriber::fmt::try_init();
     let tmpdir = tempfile::tempdir()?;
 
     let storage = Storage::load(tmpdir.path().to_owned()).await?;
```
