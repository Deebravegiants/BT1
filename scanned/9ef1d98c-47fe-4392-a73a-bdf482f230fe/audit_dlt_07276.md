# [?] chore(deps): bump imbl to 7.0.2 to fix RUSTSEC-2026-0292 (#16446)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-09-21
Source: https://github.com/near/nearcore/commit/6de070881e862d5f0bf5ef341b4762928edea8a0
Type: security-commit

## Details
chore(deps): bump imbl to 7.0.2 to fix RUSTSEC-2026-0292 (#16446)

`cargo audit -D warnings` fails on master with RUSTSEC-2026-0292:
`imbl-sized-chunks` 0.1.3 can double free or use freed memory in the
`Chunk` and `InlineArray` removal methods when an element's `Drop`
panics. The fix is in 0.2.0.

- Bump `imbl` 7.0.1 -> 7.0.2 in `Cargo.lock`. This moves
`imbl-sized-chunks` to 0.2.0.
- `imbl` 7.0.2 no longer depends on `bitmaps`, so remove the stale
RUSTSEC-2026-0247 (`bitmaps` unmaintained) ignore from
`.cargo/audit.toml`.

## Patch
### .cargo/audit.toml
```diff
@@ -46,14 +46,6 @@ ignore = [
     # host functions and does not enable or link Wasmtime's WASI support.
     "RUSTSEC-2026-0269",
 
-    # bitmaps is unmaintained (repo archived 2026-05-03), but imbl depends on it
-    # and every version is affected, so there is nothing to upgrade to. imbl is
-    # itself the maintained replacement for im, which nearcore used before.
-    # bitmaps is pinned to 3.1.0 in Cargo.lock: 3.2.0 added the unsound
-    # `Bitmap::try_from(&[u8])` and `AsMut<[u8]>` of RUSTSEC-2025-0167, and imbl
-    # calls neither. Do not bump it without re-checking that advisory.
-    "RUSTSEC-2026-0247",
-
     # RUSTSEC-2026-0253: lru `pop()` leaves dangling list pointers if the key's
     # `Drop` panics, fixed in >= 0.18.2. The workspace dependency is bumped. The
     # copy left is lru 0.7.8 under reed-solomon-erasure, which requires `^0.7.8`
```

### Cargo.lock
```diff
@@ -672,12 +672,6 @@ version = "2.11.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "843867be96c8daad0d758b57df9392b6d8d271134fce549de6ce169ff98a92af"
 
-[[package]]
-name = "bitmaps"
-version = "3.1.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "303cec55cd9c5fde944b061b902f142b52a8bb5438cc822481ea1e3ebc96bbcb"
-
 [[package]]
 name = "bitvec"
 version = "1.0.1"
@@ -3105,12 +3099,11 @@ dependencies = [
 
 [[package]]
 name = "imbl"
-version = "7.0.1"
+version = "7.0.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "43ea8d4c37ee560727e824d62804183624d371e632019b0e9e3532bce64a33e5"
+checksum = "46bad832b9b463ed9398b8506488cc2e3b897a9d44f13af115f382aac71f4fec"
 dependencies = [
  "archery",
- "bitmaps",
  "equivalent",
  "imbl-sized-chunks",
  "rand_core 0.9.3",
@@ -3121,12 +3114,9 @@ dependencies = [
 
 [[package]]
 name = "imbl-sized-chunks"
-version = "0.1.3"
+version = "0.2.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8f4241005618a62f8d57b2febd02510fb96e0137304728543dfc5fd6f052c22d"
-dependencies = [
- "bitmaps",
-]
+checksum = "2a0813be332553f857953298749fa19549e8b61b80589757c29b4e2a804fa9c6"
 
 [[package]]
 name = "impl-codec"
```
