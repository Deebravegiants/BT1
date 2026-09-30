# [?] fix(PocketIC): zombie process after panic (#6912)

## Summary
Severity: Unknown
Chain: Internet Computer
Component: dfinity/ic
Published: 2025-09-24
Source: https://github.com/dfinity/ic/commit/fec7eb34e757a47413d618f96bddab5b0f2f4329
Type: security-commit

## Details
fix(PocketIC): zombie process after panic (#6912)

This PR fixes the PocketIC server to not become a zombie process after
an operation panicked.

So far, the PocketIC server increments a counter before executing an
operation and decrements the counter after the operation executed.
However, if an operation crashes, then the counter is not decremented
and the server believes that the (failed) operation is still pending.
This PR fixes that issue by using `Drop` guards that are guaranteed to
run even after panics.

Since `Drop` guards are synchronous, this PR switches from
`tokio::sync::RwLock` to `std::sync::AtomicU64` for storing the server's
TTL.

The issue has been reproduced and the fix tested manually by introducing
an artificial panic in the server and running:
```
./pocket-ic-server --ttl 3 --port 8080
```
in one tab and
```
curl http://localhost:8080/api.json
```
in another tab. Before the fix, the server will not stop after its TTL
of 3s. After the fix, the server terminates after its TTL of 3s.

## Patch
### rs/pocket_ic_server/src/main.rs
```diff
@@ -33,17 +33,18 @@ use pocket_ic_server::state_api::{
     routes::{AppState, RouterExt, http_gateway_routes, instances_routes, status},
     state::{ApiState, PocketIcApiStateBuilder},
 };
+use std::cmp::max;
 use std::collections::HashMap;
 use std::fs::File;
 use std::io::Write;
 use std::io::{self, Error};
 use std::path::PathBuf;
 use std::sync::Arc;
 use std::sync::atomic::{AtomicU64, Ordering};
+use std::time::{Duration, SystemTime, UNIX_EPOCH};
 use tokio::runtime::Runtime;
 use tokio::sync::RwLock;
 use tokio::sync::mpsc::channel;
-use tokio::time::{Duration, Instant};
 use tower_http::trace::TraceLayer;
 use tracing::{debug, error, info};
 use tracing_appender::non_blocking::WorkerGuard;
@@ -198,7 +199,12 @@ async fn start(runtime: Arc<Runtime>) {
         .build();
     // A time-to-live mechanism: Requests bump this value, and the server
     // gracefully shuts down when the value wasn't bumped for a while.
-    let min_alive_until = Arc::new(RwLock::new(Instant::now()));
+    let min_alive_until = Arc::new(AtomicU64::new(
+        SystemTime::now()
+            .duration_since(UNIX_EPOCH)
+            .unwrap()
+            .as_nanos() as u64,
+    ));
     let app_state = AppState {
         api_state,
         pending_requests: Arc::new(AtomicU64::new(0)),
@@ -265,12 +271,15 @@ async fn start(runtime: Arc<Runtime>) {
     // This is a safeguard against orphaning this child process.
     tokio::spawn(async move {
         loop {
-            let pending_requests = app_state.pending_requests.load(Ordering::Relaxed);
-            let guard = app_state.min_alive_until.read().await;
-            if pending_requests == 0 && guard.elapsed() > Duration::from_secs(args.ttl) {
+            let pending_requests = app_state.pending_requests.load(Ordering::SeqCst);
+            let min_alive_until =
+                UNIX_EPOCH + Duration::from_nanos(app_state.min_alive_until.load(Ordering::SeqCst));
+            let elapsed = SystemTime::now()
+                .duration_since(min_alive_until)
+                .unwrap_or_default();
+            if pending_requests == 0 && elapsed > Duration::from_secs(args.ttl) {
                 break;
             }
-            drop(guard);
             tokio::time::sleep(Duration::from_secs(1)).await;
         }
 
@@ -398,6 +407,42 @@ fn create_file<P: AsRef<std::path::Path>>(file_path: P) -> std::io::Result<File>
         .open(&file_path)
 }
 
+struct PendingGuard {
+    pending_requests: Arc<AtomicU64>,
+    min_alive_until: Arc<AtomicU64>,
+}
+
+impl PendingGuard {
+    fn new(pending_requests: Arc<AtomicU64>, min_alive_until: Arc<AtomicU64>) -> Self {
+        pending_requests.fetch_add(1, Ordering::SeqCst);
+        Self {
+            pending_requests,
+            min_alive_until,
+        }
+    }
+}
+
+impl Drop for PendingGuard {
+    fn drop(&mut self) {
+        // TTL should not decrease: If now is later
+        // than the current TTL (from previous requests), reset it.
+        // Otherwise, a previous request set a larger TTL and we don't
+        // touch it.
+        let alive_until = SystemTime::now()
+            .duration_since(UNIX_EPOCH)
+            .unwrap()
+            .as_nanos() as u64;
+        self.min_alive_until
+            .fetch_update(Ordering::SeqCst, Ordering::SeqCst, |min_alive_until| {
+                Some(max(min_alive_until, alive_until))
+            })
+            .unwrap();
+        // Only mark the pending request as completed (by subtracting the counter)
+        // *after* updating TTL!
+        self.pending_requests.fetch_sub(1, Ordering::SeqCst);
+    }
+}
+
 async fn bump_last_request_timestamp(
     State(AppState {
         pending_requests,
@@ -407,22 +452,8 @@ async fn bump_last_request_timestamp(
     request: http::Request<axum::body::Body>,
     next: Next,
 ) -> impl IntoApiResponse {
-    pending_requests.fetch_add(1, Ordering::Relaxed);
-    let resp = next.run(request).await;
-    // TTL should not decrease: If now is later
-    // than the current TTL (from previous requests), reset it.
-    // Otherwise, a previous request set a larger TTL and we don't
-    // touch it.
-    let alive_until = Instant::now();
-    let mut min_alive_until = min_alive_until.write().await;
-    if *min_alive_until < alive_until {
-        *min_alive_until = alive_until;
-    }
-    drop(min_alive_until);
-    // Only mark the pending request as completed (by subtracting the counter)
-    // *after* updating TTL!
-    pending_requests.fetch_sub(1, Ordering::Relaxed);
-    resp
+    let _guard = PendingGuard::new(pending_requests.clone(), min_alive_until.clone());
+    next.run(request).await
 }
 
 async fn get_blob_store_entry(
```

### rs/pocket_ic_server/src/state_api/routes.rs
```diff
@@ -56,7 +56,7 @@ use std::{
     sync::atomic::AtomicU64,
     time::{Duration, SystemTime},
 };
-use tokio::{runtime::Runtime, sync::RwLock, time::Instant};
+use tokio::runtime::Runtime;
 use tower_http::limit::RequestBodyLimitLayer;
 use tracing::trace;
 
@@ -88,7 +88,8 @@ const RETRY_TIMEOUT_S: u64 = 300;
 pub struct AppState {
     pub api_state: Arc<ApiState>,
     pub pending_requests: Arc<AtomicU64>,
-    pub min_alive_until: Arc<RwLock<Instant>>,
+    /// TTL in nanoseconds since UNIX epoch
+    pub min_alive_until: Arc<AtomicU64>,
     pub runtime: Arc<Runtime>,
     pub blob_store: Arc<dyn BlobStore>,
 }
```
