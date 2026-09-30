# [?] rust: bump rustls to 0.23.45 for RUSTSEC-2026-0285 (#22898)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2026-09-15
Source: https://github.com/ethereum-optimism/optimism/commit/7238ed3f8165a0ed68fbe709c92f6f89c65eccd9
Type: security-commit

## Details
rust: bump rustls to 0.23.45 for RUSTSEC-2026-0285 (#22898)

Co-authored-by: Adrian Sutton <adrian@oplabs.co>

## Patch
### rust/Cargo.lock
```diff
@@ -2038,9 +2038,9 @@ dependencies = [
 
 [[package]]
 name = "aws-lc-rs"
-version = "1.16.3"
+version = "1.18.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0ec6fb3fe69024a75fa7e1bfb48aa6cf59706a101658ea01bfd33b2b248a038f"
+checksum = "b281d307588d634de920874890732659e2e7672f72b5e10e81badc1a8a83621e"
 dependencies = [
  "aws-lc-sys",
  "untrusted 0.7.1",
@@ -2049,14 +2049,15 @@ dependencies = [
 
 [[package]]
 name = "aws-lc-sys"
-version = "0.40.0"
+version = "0.45.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f50037ee5e1e41e7b8f9d161680a725bd1626cb6f8c7e901f91f942850852fe7"
+checksum = "9bff6c3b54fad79a2e60b8102caf565819711497c1f5f092f49508e2f5c31b27"
 dependencies = [
  "cc",
  "cmake",
  "dunce",
  "fs_extra",
+ "pkg-config",
 ]
 
 [[package]]
@@ -4037,7 +4038,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "7ab67060fc6b8ef687992d439ca0fa36e7ed17e9a0b16b25b601e8757df720de"
 dependencies = [
  "data-encoding",
- "syn 2.0.117",
+ "syn 1.0.109",
 ]
 
 [[package]]
@@ -15251,9 +15252,9 @@ dependencies = [
 
 [[package]]
 name = "rustls"
-version = "0.23.43"
+version = "0.23.45"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0283386ce02abc0151e1761d08802dfe86c173b0b494af5cbc086574e453da06"
+checksum = "0d41d731c7d2f962d1ccc364cec258de3c0e93b38c2fb3ba97ac74513048d634"
 dependencies = [
  "aws-lc-rs",
  "log",
@@ -15346,9 +15347,9 @@ checksum = "f87165f0995f63a9fbeea62b64d10b4d9d8e78ec6d7d51fb2125fda7bb36788f"
 
 [[package]]
 name = "rustls-webpki"
-version = "0.103.13"
+version = "0.103.15"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "61c429a8649f110dddef65e2a5ad240f747e85f7758a6bccc7e5777bd33f756e"
+checksum = "f3c3cf1d8b1e7d4927e2d154c3fcb02979afb9939629c62cd9048d4f07b60ac2"
 dependencies = [
  "aws-lc-rs",
  "ring",
@@ -18247,7 +18248,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "c5f7c95348f20c1c913d72157b3c6dee6ea3e30b3d19502c5a7f6d3f160dacbf"
 dependencies = [
  "cc",
- "windows-targets 0.52.6",
+ "windows-targets 0.48.5",
 ]
 
 [[package]]
```
