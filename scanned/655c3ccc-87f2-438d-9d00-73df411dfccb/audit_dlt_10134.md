# [?] Upgrade h2 from 0.3.21 to 0.3.24, fix RUSTSEC-2024-0003

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2024-01-18
Source: https://github.com/nervosnetwork/ckb/commit/4cec705c88898cd4226dca3252d3f0667559d28e
Type: security-commit

## Details
Upgrade h2 from 0.3.21 to 0.3.24, fix RUSTSEC-2024-0003

## Patch
### Cargo.lock
```diff
@@ -2448,17 +2448,17 @@ dependencies = [
 
 [[package]]
 name = "h2"
-version = "0.3.21"
+version = "0.3.24"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "91fc23aa11be92976ef4729127f1a74adf36d8436f7816b185d18df956790833"
+checksum = "bb2c4422095b67ee78da96fbb51a4cc413b3b25883c7717ff7ca1ab31022c9c9"
 dependencies = [
  "bytes",
  "fnv",
  "futures-core",
  "futures-sink",
  "futures-util",
  "http",
- "indexmap 1.9.3",
+ "indexmap 2.0.2",
  "slab",
  "tokio",
  "tokio-util",
```
