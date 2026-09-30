# [?] sec: bump to `bytes` `^1.11.1` for `RUSTSEC-2026-0007` (#13306)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-02-03
Source: https://github.com/foundry-rs/foundry/commit/dc9594060d8e6056d8a4bdc8ee434028bf904432
Type: security-commit

## Details
sec: bump to `bytes` `^1.11.1` for `RUSTSEC-2026-0007` (#13306)

bump to 1.11.1 for patch: https://rustsec.org/advisories/RUSTSEC-2026-0007

## Patch
### Cargo.lock
```diff
@@ -2503,9 +2503,9 @@ checksum = "1fd0f2584146f6f2ef48085050886acf353beff7305ebd1ae69500e27c67f64b"
 
 [[package]]
 name = "bytes"
-version = "1.11.0"
+version = "1.11.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b35204fbdc0b3f4446b89fc1ac2cf84a8a68971995d0bf2e925ec7cd960f9cb3"
+checksum = "1e748733b7cbc798e1434b6ac524f0c1ff2ab456fe201501e6497c8417a4fc33"
 dependencies = [
  "serde",
 ]
```
