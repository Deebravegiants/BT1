# [?] Fix panic in ord env shutdown (#3787)

## Summary
Severity: Unknown
Chain: Bitcoin
Component: ordinals/ord
Published: 2024-05-30
Source: https://github.com/ordinals/ord/commit/08e135be2d8af8f767f55805c8112c28a56e2ffd
Type: security-commit

## Details
Fix panic in ord env shutdown (#3787)

## Patch
### src/subcommand/env.rs
```diff
@@ -4,12 +4,11 @@ struct KillOnDrop(process::Child);
 
 impl Drop for KillOnDrop {
   fn drop(&mut self) {
-    assert!(Command::new("kill")
-      .arg(self.0.id().to_string())
-      .status()
-      .unwrap()
-      .success());
-    self.0.wait().unwrap();
+    let _ = Command::new("kill").arg(self.0.id().to_string()).status();
+
+    let _ = self.0.kill();
+
+    let _ = self.0.wait();
   }
 }
 
```
