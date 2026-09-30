# [?] Fix one more possible crash in execution_driver (#4900)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2025-01-23
Source: https://github.com/iotaledger/iota/commit/bcd2b9a9bbb2a2784a7cdad3e10075ac601dd99d
Type: security-commit

## Details
Fix one more possible crash in execution_driver (#4900)

## Patch
### crates/iota-core/src/execution_driver.rs
```diff
@@ -87,6 +87,16 @@ pub async fn execution_process(
         let digest = *certificate.digest();
         trace!(?digest, "Pending certificate execution activated.");
 
+        if epoch_store.epoch() != certificate.epoch() {
+            info!(
+                ?digest,
+                cur_epoch = epoch_store.epoch(),
+                cert_epoch = certificate.epoch(),
+                "Ignoring certificate from previous epoch."
+            );
+            continue;
+        }
+
         let limit = limit.clone();
         // hold semaphore permit until task completes. unwrap ok because we never close
         // the semaphore in this context.
```
