# [?] chore: ignore RUSTSEC-2020-0071 and upgrade two yanked crates

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2021-10-18
Source: https://github.com/nervosnetwork/ckb/commit/95d9587c67ecf8af1fce8a3d617cd5fe199733eb
Type: security-commit

## Details
chore: ignore RUSTSEC-2020-0071 and upgrade two yanked crates

## Patch
### Cargo.lock
```diff
@@ -1764,9 +1764,9 @@ checksum = "524cbf6897b527295dff137cec09ecf3a05f4fddffd7dfcd1585403449e74198"
 
 [[package]]
 name = "digest"
-version = "0.8.0"
+version = "0.8.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "05f47366984d3ad862010e22c7ce81a7dbcaebbdfb37241a620f8b6596ee135c"
+checksum = "f3d0c8c8752312f9713efd397ff63acb9f85585afbf179282e720e7704954dd5"
 dependencies = [
  "generic-array 0.12.4",
 ]
@@ -3276,9 +3276,9 @@ dependencies = [
 
 [[package]]
 name = "pin-project-lite"
-version = "0.2.4"
+version = "0.2.7"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "439697af366c49a6d0a010c56a0d97685bc140ce0d377b13a2ea2aa42d64a827"
+checksum = "8d31d11c69a6b52a174b42bdc0c30e5e11670f90788b2c471c31c1d17d449443"
 
 [[package]]
 name = "pin-utils"
@@ -4017,7 +4017,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "23962131a91661d643c98940b20fcaffe62d776a823247be80a48fcb8b6fce68"
 dependencies = [
  "block-buffer 0.7.3",
- "digest 0.8.0",
+ "digest 0.8.1",
  "fake-simd",
  "opaque-debug 0.2.2",
 ]
```

### deny.toml
```diff
@@ -3,7 +3,10 @@ vulnerability = "deny"
 unmaintained = "warn"
 yanked = "deny"
 notice = "deny"
-ignore = []
+ignore = [
+    # TODO Potential segfault in the time crate; waiting for the fix from upstream (chrono)
+    "RUSTSEC-2020-0071"
+]
 
 [licenses]
 unlicensed = "deny"
```
