# [?] fix: RUSTSEC-2023-0034 alert

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2023-04-21
Source: https://github.com/nervosnetwork/ckb/commit/8aac5f83e65c826e3883d46e16b90aa1426f8e48
Type: security-commit

## Details
fix: RUSTSEC-2023-0034 alert

## Patch
### Cargo.lock
```diff
@@ -2376,9 +2376,9 @@ dependencies = [
 
 [[package]]
 name = "h2"
-version = "0.3.11"
+version = "0.3.18"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d9f1f717ddc7b2ba36df7e871fd88db79326551d3d6f1fc406fbfd28b582ff8e"
+checksum = "17f8a914c2987b688368b5138aa05321db91f4090cf26118185672ad588bce21"
 dependencies = [
  "bytes 1.4.0",
  "fnv",
@@ -2389,7 +2389,7 @@ dependencies = [
  "indexmap",
  "slab",
  "tokio",
- "tokio-util 0.6.10",
+ "tokio-util 0.7.7",
  "tracing",
 ]
 
```
