# [?] fix: audit vulnerability RUSTSEC-2025-0004 (#5601)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2025-02-03
Source: https://github.com/chainflip-io/chainflip-backend/commit/3760253f31cf6e2b40012a87f363f6dcb8f801b5
Type: security-commit

## Details
fix: audit vulnerability RUSTSEC-2025-0004 (#5601)

## Patch
### Cargo.lock
```diff
@@ -2789,7 +2789,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "1145d32e826a7748b69ee8fc62d3e6355ff7f1051df53141e7048162fc90481b"
 dependencies = [
  "data-encoding",
- "syn 2.0.96",
+ "syn 1.0.109",
 ]
 
 [[package]]
@@ -7768,9 +7768,9 @@ dependencies = [
 
 [[package]]
 name = "openssl"
-version = "0.10.68"
+version = "0.10.70"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6174bc48f102d208783c2c84bf931bb75927a617866870de8a4ea85597f871f5"
+checksum = "61cfb4e166a8bb8c9b55c500bc2308550148ece889be90f609377e58140f42c6"
 dependencies = [
  "bitflags 2.8.0",
  "cfg-if",
@@ -7809,9 +7809,9 @@ dependencies = [
 
 [[package]]
 name = "openssl-sys"
-version = "0.9.104"
+version = "0.9.105"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "45abf306cbf99debc8195b66b7346498d7b10c210de50418b5ccd7ceba08c741"
+checksum = "8b22d5b84be05a8d6947c7cb71f7c849aa0f112acd4bf51c2a7c1c988ac0a9dc"
 dependencies = [
  "cc",
  "libc",
```
