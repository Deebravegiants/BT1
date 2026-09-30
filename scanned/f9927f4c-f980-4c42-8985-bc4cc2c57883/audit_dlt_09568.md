# [?] Fix Influxdb panic after upgrading.

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2023-03-21
Source: https://github.com/Conflux-Chain/conflux-rust/commit/67a78c35a52995e011dd57252f0286c2da43a0cf
Type: security-commit

## Details
Fix Influxdb panic after upgrading.

## Patch
### Cargo.lock
```diff
@@ -562,7 +562,7 @@ name = "bounded-executor"
 version = "0.1.0"
 dependencies = [
  "futures 0.3.26",
- "tokio 1.25.0",
+ "tokio 1.26.0",
 ]
 
 [[package]]
@@ -984,7 +984,7 @@ dependencies = [
  "throttling",
  "tiny-keccak 2.0.2",
  "tokio 0.2.25",
- "tokio 1.25.0",
+ "tokio 1.26.0",
  "tokio-stream",
  "tokio-timer",
  "toml",
@@ -1061,7 +1061,7 @@ dependencies = [
  "diem-metrics",
  "diem-types",
  "futures 0.3.26",
- "tokio 1.25.0",
+ "tokio 1.26.0",
 ]
 
 [[package]]
@@ -1223,7 +1223,7 @@ dependencies = [
  "textwrap 0.9.0",
  "threadpool",
  "throttling",
- "tokio 1.25.0",
+ "tokio 1.26.0",
  "tokio-stream",
  "tokio-timer",
  "toml",
@@ -1921,7 +1921,7 @@ dependencies = [
  "prometheus 0.12.0",
  "rusty-fork",
  "serde_json",
- "tokio 1.25.0",
+ "tokio 1.26.0",
 ]
 
 [[package]]
@@ -2034,7 +2034,7 @@ dependencies = [
  "futures 0.3.26",
  "pin-project",
  "thiserror",
- "tokio 1.25.0",
+ "tokio 1.26.0",
  "tokio-test",
 ]
 
@@ -2912,7 +2912,7 @@ dependencies = [
  "http 0.2.9",
  "indexmap",
  "slab",
- "tokio 1.25.0",
+ "tokio 1.26.0",
  "tokio-util",
  "tracing",
 ]
@@ -3208,7 +3208,7 @@ dependencies = [
  "itoa 1.0.5",
  "pin-project-lite 0.2.9",
  "socket2",
- "tokio 1.25.0",
+ "tokio 1.26.0",
  "tower-service",
  "tracing",
  "want 0.3.0",
@@ -3223,7 +3223,7 @@ dependencies = [
  "bytes 1.4.0",
  "hyper 0.14.24",
  "native-tls",
- "tokio 1.25.0",
+ "tokio 1.26.0",
  "tokio-native-tls",
 ]
 
@@ -4000,6 +4000,7 @@ dependencies = [
  "rand 0.7.3",
  "time 0.1.45",
  "timer",
+ "tokio 1.26.0",
 ]
 
 [[package]]
@@ -5494,7 +5495,7 @@ dependencies = [
  "serde",
  "serde_json",
  "serde_urlencoded",
- "tokio 1.25.0",
+ "tokio 1.26.0",
  "tokio-native-tls",
  "tower-service",
  "url 2.3.1",
@@ -6604,9 +6605,9 @@ dependencies = [
 
 [[package]]
 name = "tokio"
-version = "1.25.0"
+version = "1.26.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c8e00990ebabbe4c14c08aca901caed183ecd5c09562a12c824bb53d3c3fd3af"
+checksum = "03201d01c3c27a29c8a5cee5b55a93ddae1ccf6f08f65365c2c918f8c1b76f64"
 dependencies = [
  "autocfg",
  "bytes 1.4.0",
@@ -6619,7 +6620,7 @@ dependencies = [
  "signal-hook-registry",
  "socket2",
  "tokio-macros 1.8.2",
- "windows-sys 0.42.0",
+ "windows-sys 0.45.0",
 ]
 
 [[package]]
@@ -6715,7 +6716,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "bbae76ab933c85776efabc971569dd6119c580d8f5d448769dec1764bf796ef2"
 dependencies = [
  "native-tls",
- "tokio 1.25.0",
+ "tokio 1.26.0",
 ]
 
 [[package]]
@@ -6754,7 +6755,7 @@ checksum = "8fb52b74f05dbf495a8fba459fdc331812b96aa086d9eb78101fa0d4569c3313"
 dependencies = [
  "futures-core",
  "pin-project-lite 0.2.9",
- "tokio 1.25.0",
+ "tokio 1.26.0",
 ]
 
 [[package]]
@@ -6790,7 +6791,7 @@ dependencies = [
  "async-stream",
  "bytes 1.4.0",
  "futures-core",
- "tokio 1.25.0",
+ "tokio 1.26.0",
  "tokio-stream",
 ]
 
@@ -6866,7 +6867,7 @@ dependencies = [
  "futures-core",
  "futures-sink",
  "pin-project-lite 0.2.9",
- "tokio 1.25.0",
+ "tokio 1.26.0",
  "tracing",
 ]
 
```

### util/metrics/Cargo.toml
```diff
@@ -13,6 +13,7 @@ influx_db_client = "0.5.1"
 log = "0.4"
 log4rs = { version = "1.2.0", features = ["background_rotation", "gzip"] }
 futures = "0.3.26"
+tokio = "1.26.0"
 
 [dev-dependencies]
 criterion = "0.3"
```

### util/metrics/src/report_influxdb.rs
```diff
@@ -16,10 +16,12 @@ use influx_db_client::{
 };
 use log::debug;
 use std::{collections::HashMap, convert::TryInto, time::Duration};
+use tokio::runtime::{Builder, Runtime};
 
 const REPORT_TIMEOUT_SECONDS: u64 = 30;
 
 pub struct InfluxdbReporter {
+    runtime: Runtime,
     client: Client,
     tags: HashMap<String, String>, // e.g. node=Node_0, region=east_asia
 }
@@ -39,6 +41,7 @@ impl InfluxdbReporter {
             http_client,
         );
         InfluxdbReporter {
+            runtime: Builder::new_current_thread().enable_all().build().unwrap(),
             client,
             tags: HashMap::new(),
         }
@@ -48,6 +51,7 @@ impl InfluxdbReporter {
         host: T, db: T, username: R, password: R,
     ) -> Self {
         InfluxdbReporter {
+            runtime: Builder::new_current_thread().enable_all().build().unwrap(),
             client: Client::new(
                 host.into().as_str().try_into().expect("wrong url"),
                 db,
@@ -92,7 +96,7 @@ impl Reporter for InfluxdbReporter {
             points = points.push(point);
         }
 
-        if let Err(e) = futures::executor::block_on(self.client.write_points(
+        if let Err(e) = self.runtime.block_on(self.client.write_points(
             points,
             Some(Precision::Milliseconds),
             None,
```
