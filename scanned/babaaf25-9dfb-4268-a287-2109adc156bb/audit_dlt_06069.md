# [?] fix potential panic when checking VC++ Redistributable version

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2025-12-10
Source: https://github.com/nervosnetwork/ckb/commit/4a5fee669148e48996f0f5fce6dbed5cca48bec1
Type: security-commit

## Details
fix potential panic when checking VC++ Redistributable version

The previous code used `?` to propagate an error from
`get_vc_redist_version`, but the parent function does not return a
Result. This change uses `unwrap_or_default()` to safely handle the
absence of a version.

## Patch
### src/main.rs
```diff
@@ -64,7 +64,7 @@ fn check_msvc_version() {
         }
     }
 
-    if let Some(version) = get_vc_redist_version("x64")? {
+    if let Some(version) = get_vc_redist_version("x64").unwrap_or_default() {
         eprintln!("Detected VC++ Redistributable version (x64): {}", version);
         let threshold = "14.44.0.0";
         if !is_version_at_least(&version, threshold) {
```
