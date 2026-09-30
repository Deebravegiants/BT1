# [?] Merge pull request #6513 from oasisprotocol/martin/internal/rustsec-2026-0104

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2026-04-22
Source: https://github.com/oasisprotocol/oasis-core/commit/b9659e7ad4e5b537bd16ffd5e5d6ec17faee98f9
Type: security-commit

## Details
Merge pull request #6513 from oasisprotocol/martin/internal/rustsec-2026-0104

rust: Add RUSTSEC-2026-0104 to audit.toml

## Patch
### .cargo/audit.toml
```diff
@@ -4,4 +4,5 @@ ignore = [
     "RUSTSEC-2026-0049", # Vulnerable crate is only used in simple-rofl test runtime.
     "RUSTSEC-2026-0098", # Vulnerable crate is only used in simple-rofl test runtime.
     "RUSTSEC-2026-0099", # Vulnerable crate is only used in simple-rofl test runtime.
+    "RUSTSEC-2026-0104", # Vulnerable crate is only used in simple-rofl test runtime.
 ]
```

### .changelog/6513.internal.md
```diff
@@ -0,0 +1 @@
+rust: Add RUSTSEC-2026-0104 to audit.toml
```

### Cargo.lock
```diff
@@ -2690,7 +2690,7 @@ dependencies = [
  "log",
  "once_cell",
  "rustls-pki-types",
- "rustls-webpki 0.103.12",
+ "rustls-webpki 0.103.13",
  "subtle",
  "zeroize",
 ]
@@ -2755,9 +2755,9 @@ dependencies = [
 
 [[package]]
 name = "rustls-webpki"
-version = "0.103.12"
+version = "0.103.13"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8279bb85272c9f10811ae6a6c547ff594d6a7f3c6c6b02ee9726d1d0dcfcdd06"
+checksum = "61c429a8649f110dddef65e2a5ad240f747e85f7758a6bccc7e5777bd33f756e"
 dependencies = [
  "ring",
  "rustls-pki-types",
```
