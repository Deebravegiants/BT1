# [?] fix(taiko-client-rs): defer whitelist preconf driver timeouts instead of crashing (#21568)

## Summary
Severity: Unknown
Chain: Taiko
Component: taikoxyz/taiko-mono
Published: 2026-04-16
Source: https://github.com/taikoxyz/taiko-mono/commit/b67b17582f11d1f6fe64f880fb8bc3bb258ddbc7
Type: security-commit

## Details
fix(taiko-client-rs): defer whitelist preconf driver timeouts instead of crashing (#21568)

## Patch
### packages/taiko-client-rs/crates/whitelist-preconfirmation-driver/src/importer/cache_import.rs
```diff
@@ -260,7 +260,10 @@ fn should_drop_cached_driver_error(err: &driver::DriverError) -> bool {
 /// Returns true when a driver error is expected to recover after sync catches up.
 fn should_defer_cached_driver_error(err: &driver::DriverError) -> bool {
     match err {
-        driver::DriverError::EngineSyncing(_) | driver::DriverError::BlockNotFound(_) => true,
+        driver::DriverError::EngineSyncing(_) |
+        driver::DriverError::BlockNotFound(_) |
+        driver::DriverError::PreconfEnqueueTimeout { .. } |
+        driver::DriverError::PreconfResponseTimeout { .. } => true,
         driver::DriverError::PreconfInjectionFailed { source, .. } => matches!(
             source,
             driver::sync::error::EngineSubmissionError::EngineSyncing(_) |
```

### packages/taiko-client-rs/crates/whitelist-preconfirmation-driver/src/importer/tests.rs
```diff
@@ -167,13 +167,23 @@ fn propagates_cached_import_errors_for_non_payload_failures() {
 }
 
 #[test]
-fn propagates_cached_import_errors_for_driver_queue_timeouts() {
+fn defers_cached_import_errors_for_preconf_enqueue_timeout() {
     let err =
         WhitelistPreconfirmationDriverError::Driver(driver::DriverError::PreconfEnqueueTimeout {
             waited: Duration::from_secs(1),
         });
     assert!(!should_drop_cached_import_error(&err));
-    assert!(!should_defer_cached_import_error(&err));
+    assert!(should_defer_cached_import_error(&err));
+}
+
+#[test]
+fn defers_cached_import_errors_for_preconf_response_timeout() {
+    let err =
+        WhitelistPreconfirmationDriverError::Driver(driver::DriverError::PreconfResponseTimeout {
+            waited: Duration::from_secs(12),
+        });
+    assert!(!should_drop_cached_import_error(&err));
+    assert!(should_defer_cached_import_error(&err));
 }
 
 #[test]
```
