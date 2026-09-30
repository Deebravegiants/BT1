# [?] fix(audit): bump rkyv to 0.8.16 to fix RUSTSEC-2026-0122 (#15709)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-05-11
Source: https://github.com/near/nearcore/commit/ca6c2d54ad5dd01f25ebeeb59fd505fa32e6f9ce
Type: security-commit

## Details
fix(audit): bump rkyv to 0.8.16 to fix RUSTSEC-2026-0122 (#15709)

Bump `rkyv` from 0.8.13 to 0.8.16 to address
[RUSTSEC-2026-0122](https://rustsec.org/advisories/RUSTSEC-2026-0122) —
panic safety bugs in `InlineVec::clear` and `SerVec::clear` that enable
arbitrary code execution. The advisory affects 0.8.0–0.8.15; 0.8.16
contains the patch.

Used transitively in the workspace via the `near-vm-*` crates. Caught by
`cargo audit` on #15708.

## Patch
### Cargo.lock
```diff
@@ -2209,7 +2209,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "33d852cb9b869c2a9b3df2f71a3074817f01e1844f839a144f5fcef059a4eb5d"
 dependencies = [
  "libc",
- "windows-sys 0.52.0",
+ "windows-sys 0.59.0",
 ]
 
 [[package]]
@@ -7216,13 +7216,13 @@ dependencies = [
 
 [[package]]
 name = "rkyv"
-version = "0.8.13"
+version = "0.8.16"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8b2e88acca7157d83d789836a3987dafc12bc3d88a050e54b8fe9ea4aaa29d20"
+checksum = "73389e0c99e664f919275ab5b5b0471391fe9a8de61e1dff9b1eaf56a90f16e3"
 dependencies = [
  "bytecheck",
  "bytes",
- "hashbrown 0.16.1",
+ "hashbrown 0.17.0",
  "indexmap 2.14.0",
  "munge",
  "ptr_meta",
@@ -7235,9 +7235,9 @@ dependencies = [
 
 [[package]]
 name = "rkyv_derive"
-version = "0.8.13"
+version = "0.8.16"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7f6dffea3c91fa91a3c0fc8a061b0e27fef25c6304728038a6d6bcb1c58ba9bd"
+checksum = "5d2ed0b54125315fb36bd021e82d314d1c126548f871634b483f46b31d13cac6"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -7474,7 +7474,7 @@ dependencies = [
  "errno",
  "libc",
  "linux-raw-sys",
- "windows-sys 0.52.0",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
@@ -8385,7 +8385,7 @@ dependencies = [
  "getrandom 0.3.1",
  "once_cell",
  "rustix",
- "windows-sys 0.52.0",
+ "windows-sys 0.59.0",
 ]
 
 [[package]]
```

### Cargo.toml
```diff
@@ -339,7 +339,7 @@ regex = "1.7.1"
 region = "3.0"
 reqwest = { version = "0.13", features = ["blocking", "native-tls-vendored", "form", "query"] }
 ripemd = "0.1.1"
-rkyv = "0.8.13"
+rkyv = "0.8.16"
 rlimit = "0.7"
 rlp = "0.5.2"
 rocksdb = { version = "0.21.0", default-features = false }
```
