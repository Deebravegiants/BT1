# [?] fix: bump openssl to fix RUSTSEC-2025-0022 (#5788)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2025-04-04
Source: https://github.com/chainflip-io/chainflip-backend/commit/fca132c4d5e4af2c5ecf9d87b7b419ee1894358d
Type: security-commit

## Details
fix: bump openssl to fix RUSTSEC-2025-0022 (#5788)

fix: bump openssl to fix RUSTSEC-2025-0022`

## Patch
### Cargo.lock
```diff
@@ -2931,7 +2931,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "1145d32e826a7748b69ee8fc62d3e6355ff7f1051df53141e7048162fc90481b"
 dependencies = [
  "data-encoding",
- "syn 2.0.96",
+ "syn 1.0.109",
 ]
 
 [[package]]
@@ -7876,9 +7876,9 @@ dependencies = [
 
 [[package]]
 name = "openssl"
-version = "0.10.70"
+version = "0.10.72"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "61cfb4e166a8bb8c9b55c500bc2308550148ece889be90f609377e58140f42c6"
+checksum = "fedfea7d58a1f73118430a55da6a286e7b044961736ce96a16a17068ea25e5da"
 dependencies = [
  "bitflags 2.8.0",
  "cfg-if",
@@ -7917,9 +7917,9 @@ dependencies = [
 
 [[package]]
 name = "openssl-sys"
-version = "0.9.105"
+version = "0.9.107"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8b22d5b84be05a8d6947c7cb71f7c849aa0f112acd4bf51c2a7c1c988ac0a9dc"
+checksum = "8288979acd84749c744a9014b4382d42b8f7b2592847b5afb2ed29e5d16ede07"
 dependencies = [
  "cc",
  "libc",
```
