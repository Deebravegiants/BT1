# [?] Fix a test child process panic bug (#5842)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2022-12-12
Source: https://github.com/ZcashFoundation/zebra/commit/47073ab30a6cccb5dbc2af4260ade916ecec9813
Type: security-commit

## Details
Fix a test child process panic bug (#5842)

## Patch
### zebra-test/src/command.rs
```diff
@@ -846,8 +846,10 @@ impl<T> TestChild<T> {
             self.kill(true)?;
         }
 
-        let timeout =
-            humantime::format_duration(self.timeout.expect("already checked past_deadline()"));
+        let timeout = self
+            .timeout
+            .map(|timeout| humantime::format_duration(timeout).to_string())
+            .unwrap_or_else(|| "unlimited".to_string());
 
         let report = eyre!(
             "{stream_name} of command did not log any matches for the given regex,\n\
```
