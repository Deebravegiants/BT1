# [?] Fix one more possible crash in execution_driver (#19870)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2024-10-23
Source: https://github.com/MystenLabs/sui/commit/ac10df6e7ce5bee86ca401d47e48ea2326f4423f
Type: security-commit

## Details
Fix one more possible crash in execution_driver (#19870)

Don't even try to execute certs from prior epochs

## Patch
### crates/sui-core/src/execution_driver.rs
```diff
@@ -99,6 +99,16 @@ pub async fn execution_process(
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
