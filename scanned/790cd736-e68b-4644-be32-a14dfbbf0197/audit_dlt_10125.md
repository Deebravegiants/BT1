# [?] Upgrade openssl from 0.10.68 to 0.10.70, fix  https://rustsec.org/advisories/RUSTSEC-2025-0004

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2025-02-07
Source: https://github.com/nervosnetwork/ckb/commit/17bc6fa4c319b9be041792bb0ddfd92ec50db672
Type: security-commit

## Details
Upgrade openssl from 0.10.68 to 0.10.70, fix  https://rustsec.org/advisories/RUSTSEC-2025-0004

## Patch
### Cargo.lock
```diff
@@ -4267,9 +4267,9 @@ checksum = "c08d65885ee38876c4f86fa503fb49d7b507c2b62552df7c70b2fce627e06381"
 
 [[package]]
 name = "openssl"
-version = "0.10.68"
+version = "0.10.70"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6174bc48f102d208783c2c84bf931bb75927a617866870de8a4ea85597f871f5"
+checksum = "61cfb4e166a8bb8c9b55c500bc2308550148ece889be90f609377e58140f42c6"
 dependencies = [
  "bitflags 2.6.0",
  "cfg-if",
@@ -4308,9 +4308,9 @@ dependencies = [
 
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
