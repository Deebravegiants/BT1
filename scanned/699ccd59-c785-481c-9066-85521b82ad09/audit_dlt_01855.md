# [?] rust: bump rkyv to 0.8.16 for RUSTSEC-2026-0122 (#20653)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2026-05-11
Source: https://github.com/ethereum-optimism/optimism/commit/cef9741905b2dd3711aa628aa59886438abf4e2e
Type: security-commit

## Details
rust: bump rkyv to 0.8.16 for RUSTSEC-2026-0122 (#20653)

`cargo update -p rkyv`. Fixes the unsound `InlineVec::clear` /
`SerVec::clear` advisory flagged by rust-deny.

Co-authored-by: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

## Patch
### rust/Cargo.lock
```diff
@@ -12726,13 +12726,13 @@ dependencies = [
 
 [[package]]
 name = "rkyv"
-version = "0.8.15"
+version = "0.8.16"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1a30e631b7f4a03dee9056b8ef6982e8ba371dd5bedb74d3ec86df4499132c70"
+checksum = "73389e0c99e664f919275ab5b5b0471391fe9a8de61e1dff9b1eaf56a90f16e3"
 dependencies = [
  "bytecheck",
  "bytes",
- "hashbrown 0.16.1",
+ "hashbrown 0.17.0",
  "indexmap 2.14.0",
  "munge",
  "ptr_meta",
@@ -12745,9 +12745,9 @@ dependencies = [
 
 [[package]]
 name = "rkyv_derive"
-version = "0.8.15"
+version = "0.8.16"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8100bb34c0a1d0f907143db3149e6b4eea3c33b9ee8b189720168e818303986f"
+checksum = "5d2ed0b54125315fb36bd021e82d314d1c126548f871634b483f46b31d13cac6"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -14006,7 +14006,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "32497e9a4c7b38532efcdebeef879707aa9f794296a4f0244f6f69e9bc8574bd"
 dependencies = [
  "fastrand",
- "getrandom 0.4.2",
+ "getrandom 0.3.4",
  "once_cell",
  "rustix",
  "windows-sys 0.61.2",
```
