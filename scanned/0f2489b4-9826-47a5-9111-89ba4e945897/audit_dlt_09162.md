# [?] fix(offchain): Update tower to fix polling monitor deadlock (#4124)

## Summary
Severity: Unknown
Chain: The Graph
Component: graphprotocol/graph-node
Published: 2022-11-02
Source: https://github.com/graphprotocol/graph-node/commit/c6c38d79c0a08487018b35ecbc7ee4d2c4107223
Type: security-commit

## Details
fix(offchain): Update tower to fix polling monitor deadlock (#4124)

## Patch
### Cargo.lock
```diff
@@ -4722,7 +4722,7 @@ dependencies = [
 [[package]]
 name = "tower"
 version = "0.4.12"
-source = "git+https://github.com/tower-rs/tower.git#d27ba65891590b848fa9ba13a202d5d4aa5eda81"
+source = "git+https://github.com/tower-rs/tower.git#c9d84cde0c9a23e1d2d5b5ae7ae432629712658b"
 dependencies = [
  "futures-core",
  "futures-util",
@@ -4765,7 +4765,7 @@ checksum = "343bc9466d3fe6b0f960ef45960509f84480bf4fd96f92901afe7ff3df9d3a62"
 [[package]]
 name = "tower-layer"
 version = "0.3.1"
-source = "git+https://github.com/tower-rs/tower.git#d27ba65891590b848fa9ba13a202d5d4aa5eda81"
+source = "git+https://github.com/tower-rs/tower.git#c9d84cde0c9a23e1d2d5b5ae7ae432629712658b"
 
 [[package]]
 name = "tower-service"
@@ -4776,12 +4776,12 @@ checksum = "360dfd1d6d30e05fda32ace2c8c70e9c0a9da713275777f5a4dbb8a1893930c6"
 [[package]]
 name = "tower-service"
 version = "0.3.1"
-source = "git+https://github.com/tower-rs/tower.git#d27ba65891590b848fa9ba13a202d5d4aa5eda81"
+source = "git+https://github.com/tower-rs/tower.git#c9d84cde0c9a23e1d2d5b5ae7ae432629712658b"
 
 [[package]]
 name = "tower-test"
 version = "0.4.0"
-source = "git+https://github.com/tower-rs/tower.git#d27ba65891590b848fa9ba13a202d5d4aa5eda81"
+source = "git+https://github.com/tower-rs/tower.git#c9d84cde0c9a23e1d2d5b5ae7ae432629712658b"
 dependencies = [
  "futures-util",
  "pin-project-lite",
```

### core/src/polling_monitor/mod.rs
```diff
@@ -256,6 +256,28 @@ mod tests {
         (handle, monitor, rx)
     }
 
+    #[tokio::test]
+    async fn polling_monitor_shared_svc() {
+        let (svc, mut handle) = mock::pair();
+        let shared_svc = tower::buffer::Buffer::new(tower::limit::ConcurrencyLimit::new(svc, 1), 1);
+        let make_monitor = |svc| {
+            let (tx, rx) = mpsc::channel(10);
+            let metrics = PollingMonitorMetrics::mock();
+            let monitor = spawn_monitor(svc, tx, log::discard(), metrics);
+            (monitor, rx)
+        };
+
+        // Spawn a monitor and yield to ensure it is polled and waiting on the tx.
+        let (_monitor0, mut _rx0) = make_monitor(shared_svc.clone());
+        tokio::task::yield_now().await;
+
+        // Test that the waiting monitor above is not occupying a concurrency slot on the service.
+        let (monitor1, mut rx1) = make_monitor(shared_svc);
+        monitor1.monitor("req-0");
+        send_response(&mut handle, Some("res-0")).await;
+        assert_eq!(rx1.recv().await, Some(("req-0", "res-0")));
+    }
+
     #[tokio::test]
     async fn polling_monitor_simple() {
         let (mut handle, monitor, mut rx) = setup();
```

### tests/tests/runner.rs
```diff
@@ -146,7 +146,7 @@ async fn file_data_sources() {
 
     // This test assumes the file data sources will be processed in the same block in which they are
     // created. But the test might fail due to a race condition if for some reason it takes longer
-    // than expectd to fetch the file from IPFS. The sleep here will conveniently happen after the
+    // than expected to fetch the file from IPFS. The sleep here will conveniently happen after the
     // data source is added to the offchain monitor but before the monitor is checked, in an an
     // attempt to ensure the monitor has enough time to fetch the file.
     let adapter_selector = NoopAdapterSelector {
```
