# [?] Merge pull request #5851 from oasisprotocol/peternose/bugfix/fix-abort-on-panic

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2024-09-12
Source: https://github.com/oasisprotocol/oasis-core/commit/c3e7d2de2fded99f3f56af08b7e4c56e82cda8d4
Type: security-commit

## Details
Merge pull request #5851 from oasisprotocol/peternose/bugfix/fix-abort-on-panic

runtime/src/dispatcher: Propagate panics during status/policy update

## Patch
### .changelog/5851.bugfix.md
```diff
@@ -0,0 +1 @@
+runtime/src/dispatcher: Propagate panics during status/policy update
```

### runtime/src/dispatcher.rs
```diff
@@ -985,7 +985,8 @@ impl Dispatcher {
 
             Ok(())
         })
-        .await??;
+        .await
+        .unwrap()?; // Propagate panics during key manager status update.
 
         debug!(self.logger, "KM status update request complete");
 
@@ -1018,7 +1019,8 @@ impl Dispatcher {
 
             Ok(())
         })
-        .await??;
+        .await
+        .unwrap()?; // Propagate panics during key manager quote policy update.
 
         debug!(self.logger, "KM quote policy update request complete");
 
```
