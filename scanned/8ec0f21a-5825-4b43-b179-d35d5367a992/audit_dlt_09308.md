# [?] fix deny.toml, ignore RUSTSEC-2025-0014 (#10052)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2025-03-11
Source: https://github.com/foundry-rs/foundry/commit/18d4419760366f1f501b52f0378e1910a73ab1fa
Type: security-commit

## Details
fix deny.toml, ignore RUSTSEC-2025-0014 (#10052)

* fix deny.toml, ignore RUSTSEC-2025-0014

* roll back allow-git

## Patch
### deny.toml
```diff
@@ -11,6 +11,8 @@ ignore = [
     "RUSTSEC-2024-0436",
     # https://rustsec.org/advisories/RUSTSEC-2024-0437 protobuf! Crash due to uncontrolled recursion in protobuf crate.
     "RUSTSEC-2024-0437",
+    # humantime is unmaintained
+    "RUSTSEC-2025-0014",
 ]
 
 # This section is considered when running `cargo deny check bans`.
@@ -47,7 +49,6 @@ allow = [
     "BSD-3-Clause",
     "ISC",
     "Unicode-3.0",
-    "OpenSSL",
     "Unlicense",
     "WTFPL",
     "BSL-1.0",
```
