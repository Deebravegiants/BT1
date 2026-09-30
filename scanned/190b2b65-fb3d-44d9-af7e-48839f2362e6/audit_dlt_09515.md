# [?] chore: fix RUSTSEC-2024-0003 (#4426)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2024-01-18
Source: https://github.com/chainflip-io/chainflip-backend/commit/4e0764940247e88ec48b39a5c1fbd2cedd66f648
Type: security-commit

## Details
chore: fix RUSTSEC-2024-0003 (#4426)

## Patch
### Cargo.lock
```diff
@@ -4480,17 +4480,17 @@ dependencies = [
 
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
+ "indexmap 2.1.0",
  "slab",
  "tokio",
  "tokio-util",
```
