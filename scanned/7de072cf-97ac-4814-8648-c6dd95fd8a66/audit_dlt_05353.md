# [?] fix: `RUSTSEC-2026-0007` (#10084)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-02-05
Source: https://github.com/iotaledger/iota/commit/2b5a5d93f11384aaeee4dc90be8db603fbae8dd1
Type: security-commit

## Details
fix: `RUSTSEC-2026-0007` (#10084)

```
173 │ bytes 1.9.0 registry+https://github.com/rust-lang/crates.io-index
    │ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ security vulnerability detected
    │
    ├ ID: RUSTSEC-2026-0007
    ├ Advisory: https://rustsec.org/advisories/RUSTSEC-2026-0007
    ├ In the unique reclaim path of `BytesMut::reserve`, the condition
      ```rs
      if v_capacity >= new_cap + offset
      ```
      uses an unchecked addition. When `new_cap + offset` overflows `usize` in release builds, this condition may incorrectly pass, causing `self.cap` to be set to a value that exceeds the actual allocated capacity. Subsequent APIs such as `spare_capacity_mut()` then trust this corrupted `cap` value and may create out-of-bounds slices, leading to UB.
      
      This behavior is observable in release builds (integer overflow wraps), whereas debug builds panic due to overflow checks.
      
      ## PoC
      
      ```rs
      use bytes::*;
      
      fn main() {
          let mut a = BytesMut::from(&b"hello world"[..]);
          let mut b = a.split_off(5);
      
          // Ensure b becomes the unique owner of the backing storage
          drop(a);
      
          // Trigger overflow in new_cap + offset inside reserve
          b.reserve(usize::MAX - 6);
      
          // This call relies on the corrupted cap and may cause UB & HBO
          b.put_u8(b'h');
      }
      ```
      
      # Workarounds
      
      Users of `BytesMut::reserve` are only affected if integer overflow checks are configured to wrap. When integer overflow is configured to panic, this issue does not apply.
    ├ Announcement: https://github.com/advisories/GHSA-434x-w66g-qw3r
    ├ Solution: Upgrade to >=1.11.1 (try `cargo update -p bytes`)
```

### Cargo.lock
```diff
@@ -2149,9 +2149,9 @@ checksum = "1fd0f2584146f6f2ef48085050886acf353beff7305ebd1ae69500e27c67f64b"
 
 [[package]]
 name = "bytes"
-version = "1.9.0"
+version = "1.11.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "325918d6fe32f23b19878fe4b34794ae41fc19ddbe53b10571a4874d44ffd39b"
+checksum = "1e748733b7cbc798e1434b6ac524f0c1ff2ab456fe201501e6497c8417a4fc33"
 dependencies = [
  "serde",
 ]
```

### external-crates/move/Cargo.lock
```diff
@@ -370,9 +370,9 @@ checksum = "1fd0f2584146f6f2ef48085050886acf353beff7305ebd1ae69500e27c67f64b"
 
 [[package]]
 name = "bytes"
-version = "1.10.1"
+version = "1.11.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d71b6127be86fdcfddb610f7182ac57211d4b18a3e9c82eb2d17662f2227ad6a"
+checksum = "1e748733b7cbc798e1434b6ac524f0c1ff2ab456fe201501e6497c8417a4fc33"
 
 [[package]]
 name = "cassowary"
@@ -942,6 +942,15 @@ version = "1.0.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "877a4ace8713b0bcf2a4e7eec82529c029f1d0619886d18145fea96c3ffe5c0f"
 
+[[package]]
+name = "erased-discriminant"
+version = "1.0.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "c1a6df962265a53221f29081896c412ef325c17fa7d638cd9578febe53d3c82c"
+dependencies = [
+ "typeid",
+]
+
 [[package]]
 name = "errno"
 version = "0.3.13"
@@ -3281,13 +3290,16 @@ dependencies = [
 
 [[package]]
 name = "serde-reflection"
-version = "0.4.0"
+version = "0.5.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5b6798a64289ff550d8d79847467789a5fd30b42c9c406a4d6dc0bc9b567e55c"
+checksum = "68fb2363ca88876b3e16442b02dde5305646fd50df297c79a4b54fc5f5cf51d4"
 dependencies = [
+ "erased-discriminant",
  "once_cell",
  "serde",
+ "serde_json",
  "thiserror",
+ "typeid",
 ]
 
 [[package]]
@@ -3930,6 +3942,12 @@ version = "0.1.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "a7f741b240f1a48843f9b8e0444fb55fb2a4ff67293b50a9179dfd5ea67f8d41"
 
+[[package]]
+name = "typeid"
+version = "1.0.3"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "bc7d623258602320d5c55d1bc22793b57daff0ec7efc270ea7d55ce1d5f5471c"
+
 [[package]]
 name = "typenum"
 version = "1.18.0"
```

### external-crates/move/deny.toml
```diff
@@ -47,9 +47,6 @@ ignore = [
   "RUSTSEC-2024-0370",
   # `atty` is unmaintained
   "RUSTSEC-2024-0375",
-  # Potential unaligned read in `atty`
-  "RUSTSEC-2021-0145",
-
   # allow unmaintained instant crate used in transitive dependencies (backoff, cached, fastrand, parking_lot_*)
   "RUSTSEC-2024-0384",
   # `paste` is unmaintained
```
