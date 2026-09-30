# [?] chore(deps): bump rustls to 0.23.45 to fix RUSTSEC-2026-0285 (#13736)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-09-15
Source: https://github.com/noir-lang/noir/commit/1257c19c13f9810e8c6ddd80f42aeb4ab3c8d5c4
Type: security-commit

## Details
chore(deps): bump rustls to 0.23.45 to fix RUSTSEC-2026-0285 (#13736)

## Patch
### Cargo.lock
```diff
@@ -4814,9 +4814,9 @@ dependencies = [
 
 [[package]]
 name = "rustls"
-version = "0.23.40"
+version = "0.23.45"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "ef86cd5876211988985292b91c96a8f2d298df24e75989a43a3c73f2d4d8168b"
+checksum = "0d41d731c7d2f962d1ccc364cec258de3c0e93b38c2fb3ba97ac74513048d634"
 dependencies = [
  "log",
  "once_cell",
@@ -4877,9 +4877,9 @@ checksum = "f87165f0995f63a9fbeea62b64d10b4d9d8e78ec6d7d51fb2125fda7bb36788f"
 
 [[package]]
 name = "rustls-webpki"
-version = "0.103.13"
+version = "0.103.15"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "61c429a8649f110dddef65e2a5ad240f747e85f7758a6bccc7e5777bd33f756e"
+checksum = "f3c3cf1d8b1e7d4927e2d154c3fcb02979afb9939629c62cd9048d4f07b60ac2"
 dependencies = [
  "ring",
  "rustls-pki-types",
```
