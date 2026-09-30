# [?] Fixed risc0-build deadlock / double build (#498)

## Summary
Severity: Unknown
Chain: ZK
Component: risc0/risc0
Published: 2023-04-05
Source: https://github.com/risc0/risc0/commit/96deb8515ec614d36482619122b46584376b20e5
Type: security-commit

## Details
Fixed risc0-build deadlock / double build (#498)

## Patch
### risc0/build/src/lib.rs
```diff
@@ -409,10 +409,9 @@ fn build_guest_package<P>(
         }
     }
 
-    let status = cmd.status().unwrap();
-
-    if !status.success() {
-        std::process::exit(status.code().unwrap());
+    let res = child.wait().expect("Guest 'cargo build' failed");
+    if !res.success() {
+        std::process::exit(res.code().unwrap());
     }
 }
 
```
