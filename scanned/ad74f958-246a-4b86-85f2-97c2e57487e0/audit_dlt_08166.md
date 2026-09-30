# [?] fix(deps): bump inferno to 0.12.8 to pull quick-xml 0.41 (RUSTSEC-2026-0194, RUSTSEC-2026-0195)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-08-19
Source: https://github.com/ZcashFoundation/zebra/commit/d45427e8c069bc0fc31472a7afe98eaf66fd1b88
Type: security-commit

## Details
fix(deps): bump inferno to 0.12.8 to pull quick-xml 0.41 (RUSTSEC-2026-0194, RUSTSEC-2026-0195)

## Patch
### Cargo.lock
```diff
@@ -2556,9 +2556,9 @@ dependencies = [
 
 [[package]]
 name = "inferno"
-version = "0.12.6"
+version = "0.12.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "90807d610575744524d9bdc69f3885d96f0e6c3354565b0828354a7ff2a262b8"
+checksum = "0c460d4fa06223667240720ab69a8045133755ae6dfbe100cf481b95e3a014f1"
 dependencies = [
  "ahash",
  "itoa",
@@ -4133,9 +4133,9 @@ checksum = "a1d01941d82fa2ab50be1e79e6714289dd7cde78eba4c074bc5a4374f650dfe0"
 
 [[package]]
 name = "quick-xml"
-version = "0.39.2"
+version = "0.41.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "958f21e8e7ceb5a1aa7fa87fab28e7c75976e0bfe7e23ff069e0a260f894067d"
+checksum = "e660451e55124f798a69a5af3f49ccfbefbd41910eefd25caf2393e1f3473ec1"
 dependencies = [
  "memchr",
 ]
```
