# [?] chore(ci): bump lru to 0.18.2 and allow RUSTSEC-2026-0253 (#16210)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-08-17
Source: https://github.com/near/nearcore/commit/ff6ed2096f8bd281f9c9534291f3c312026beb3a
Type: security-commit

## Details
chore(ci): bump lru to 0.18.2 and allow RUSTSEC-2026-0253 (#16210)

`cargo audit -D warnings` fails on master. RUSTSEC-2026-0253 was filed
against `lru`: `LruCache::pop()` was not panic-safe, so a panicking key
`Drop` could leave dangling pointers in the internal linked list. Fixed
in 0.18.2.

Bumps the workspace dependency from 0.16.3 to 0.18.2.

The other copy is `lru` 0.7.8 under `reed-solomon-erasure`, which
requires `^0.7.8` in its latest release, 6.0.0 (2022-09-23), so no
published version resolves to a patched `lru`. That one is added to
`.cargo/audit.toml` instead: the bug needs unwinding plus a key with a
panicking `Drop`, and that cache is keyed by `Vec<usize>`.

Not urgent either way, since release builds set `panic = 'abort'`
(`Cargo.toml:398`).

## Patch
### .cargo/audit.toml
```diff
@@ -48,4 +48,12 @@ ignore = [
     # `Bitmap::try_from(&[u8])` and `AsMut<[u8]>` of RUSTSEC-2025-0167, and imbl
     # calls neither. Do not bump it without re-checking that advisory.
     "RUSTSEC-2026-0247",
+
+    # RUSTSEC-2026-0253: lru `pop()` leaves dangling list pointers if the key's
+    # `Drop` panics, fixed in >= 0.18.2. The workspace dependency is bumped. The
+    # copy left is lru 0.7.8 under reed-solomon-erasure, which requires `^0.7.8`
+    # in its latest release, 6.0.0 (2022-09-23). Not triggerable there anyway:
+    # the bug needs unwinding plus a key with a panicking `Drop`, and that cache
+    # is keyed by `Vec<usize>` (reed-solomon-erasure `src/core.rs:349`).
+    "RUSTSEC-2026-0253",
 ]
```

### Cargo.lock
```diff
@@ -2680,18 +2680,15 @@ name = "hashbrown"
 version = "0.16.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "841d1cc9bed7f9236f321df977030373f4a4163ae1a7dbfe1a51a2c1a51d9100"
-dependencies = [
- "allocator-api2",
- "equivalent",
- "foldhash 0.2.0",
-]
 
 [[package]]
 name = "hashbrown"
 version = "0.17.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "4f467dd6dccf739c208452f8014c75c18bb8301b050ad1cfb27153803edb0f51"
 dependencies = [
+ "allocator-api2",
+ "equivalent",
  "foldhash 0.2.0",
  "serde",
  "serde_core",
@@ -3666,11 +3663,11 @@ dependencies = [
 
 [[package]]
 name = "lru"
-version = "0.16.3"
+version = "0.18.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a1dc47f592c06f33f8e3aea9591776ec7c9f9e4124778ff8a3c3b87159f7e593"
+checksum = "5d2f2f9b4ba7e6b24d95e7e899329d35be83bcded72c8540cdd5368932d1d90a"
 dependencies = [
- "hashbrown 0.16.1",
+ "hashbrown 0.17.0",
 ]
 
 [[package]]
@@ -3950,7 +3947,7 @@ name = "near-cache"
 version = "0.0.0"
 dependencies = [
  "bencher",
- "lru 0.16.3",
+ "lru 0.18.2",
  "parking_lot 0.12.1",
  "rand 0.8.5",
 ]
@@ -3969,7 +3966,7 @@ dependencies = [
  "enum-map",
  "insta",
  "itertools 0.14.0",
- "lru 0.16.3",
+ "lru 0.18.2",
  "near-async",
  "near-cache",
  "near-chain-configs",
@@ -4047,7 +4044,7 @@ version = "0.0.0"
 dependencies = [
  "assert_matches",
  "itertools 0.14.0",
- "lru 0.16.3",
+ "lru 0.18.2",
  "near-async",
  "near-chain",
  "near-chain-configs",
@@ -4086,7 +4083,7 @@ dependencies = [
  "criterion",
  "futures",
  "itertools 0.14.0",
- "lru 0.16.3",
+ "lru 0.18.2",
  "near-async",
  "near-cache",
  "near-chain",
@@ -4573,7 +4570,7 @@ dependencies = [
  "futures-util",
  "imbl",
  "itertools 0.14.0",
- "lru 0.16.3",
+ "lru 0.18.2",
  "named-lock",
  "near-async",
  "near-chain-configs",
@@ -4930,7 +4927,7 @@ dependencies = [
  "insta",
  "itertools 0.14.0",
  "itoa",
- "lru 0.16.3",
+ "lru 0.18.2",
  "near-async",
  "near-chain",
  "near-chain-configs",
@@ -5077,7 +5074,7 @@ dependencies = [
  "finite-wasm 0.5.1",
  "finite-wasm 0.6.1",
  "hex",
- "lru 0.16.3",
+ "lru 0.18.2",
  "near-crypto",
  "near-o11y",
  "near-parameters",
```

### Cargo.toml
```diff
@@ -205,7 +205,7 @@ inventory = "0.3.15"
 itertools = "0.14.0"
 itoa = "1.0"
 json_comments = "0.2.1"
-lru = "0.16.3"
+lru = "0.18.2"
 named-lock = "0.4.1"
 near-account-id = { version = "2.0.0", features = [
     "internal_unstable",
```
