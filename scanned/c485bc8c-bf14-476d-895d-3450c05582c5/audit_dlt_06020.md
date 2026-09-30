# [?] fix: address CI failures - unused panic import and admin_auth test flakiness

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-02-02
Source: https://github.com/fedimint/fedimint/commit/bc6c0b4553769f6fed3c6918469a4c4deb5222dd
Type: security-commit

## Details
fix: address CI failures - unused panic import and admin_auth test flakiness

- Conditionally import panic module only for non-WASM targets in jit.rs
- Add retry logic to admin_auth test to handle transient iroh connection issues

Signed-off-by: Devansh Vashisht <devansh.vashisht.ug24@nsut.ac.in>

## Patch
### devimint/src/tests.rs
```diff
@@ -2339,13 +2339,18 @@ pub async fn admin_auth_tests(dev_fed: DevFed) -> Result<()> {
 
     // Now run an admin command WITHOUT --our-id and --password
     // It should use the stored credentials automatically
-    let status_result = cmd!(client, "admin", "status").out_json().await;
-
-    // The command should succeed using stored credentials
-    assert!(
-        status_result.is_ok(),
-        "Admin status command should succeed with stored credentials"
-    );
+    // Use retry logic to handle transient iroh connection issues
+    retry(
+        "Admin status with stored credentials",
+        aggressive_backoff(),
+        || async {
+            cmd!(client, "admin", "status")
+                .out_json()
+                .await
+                .context("Admin status command should succeed with stored credentials")
+        },
+    )
+    .await?;
 
     info!(target: LOG_DEVIMINT, "Testing that --force overwrites existing credentials");
 
```

### fedimint-core/src/task/jit.rs
```diff
@@ -1,6 +1,8 @@
 use std::convert::Infallible;
+use std::fmt;
+#[cfg(not(target_family = "wasm"))]
+use std::panic;
 use std::sync::Arc;
-use std::{fmt, panic};
 
 use fedimint_core::runtime::JoinHandle;
 use fedimint_logging::LOG_TASK;
```
