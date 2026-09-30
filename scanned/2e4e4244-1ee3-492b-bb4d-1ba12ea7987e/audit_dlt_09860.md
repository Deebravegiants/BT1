# [?] fix: RUSTSEC-2025-0119 advisory (#9320)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2025-11-18
Source: https://github.com/iotaledger/iota/commit/340d700a706b5629f6fe4e7bb095d0a42bcb04a8
Type: security-commit

## Details
fix: RUSTSEC-2025-0119 advisory (#9320)

# Description of change

Fixes https://rustsec.org/advisories/RUSTSEC-2025-0119.html

## Patch
### Cargo.lock
```diff
@@ -2722,10 +2722,22 @@ dependencies = [
  "encode_unicode 0.3.6",
  "lazy_static",
  "libc",
- "unicode-width 0.1.14",
  "windows-sys 0.52.0",
 ]
 
+[[package]]
+name = "console"
+version = "0.16.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "b430743a6eb14e9764d4260d4c0d8123087d504eeb9c48f2b2a5e810dd369df4"
+dependencies = [
+ "encode_unicode 1.0.0",
+ "libc",
+ "once_cell",
+ "unicode-width 0.2.0",
+ "windows-sys 0.61.2",
+]
+
 [[package]]
 name = "console-api"
 version = "0.8.0"
@@ -5281,15 +5293,15 @@ dependencies = [
 
 [[package]]
 name = "indicatif"
-version = "0.17.8"
+version = "0.18.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "763a5a8f45087d6bcea4222e7b72c291a054edf80e4ef6efd2a4979878c7bea3"
+checksum = "9375e112e4b463ec1b1c6c011953545c65a30164fbab5b581df32b3abf0dcb88"
 dependencies = [
- "console",
- "instant",
- "number_prefix",
+ "console 0.16.1",
  "portable-atomic",
- "unicode-width 0.1.14",
+ "unicode-width 0.2.0",
+ "unit-prefix",
+ "web-time",
 ]
 
 [[package]]
@@ -5356,7 +5368,7 @@ version = "1.42.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "50259abbaa67d11d2bcafc7ba1d094ed7a0c70e3ce893f0d0997f73558cb3084"
 dependencies = [
- "console",
+ "console 0.15.8",
  "linked-hash-map",
  "once_cell",
  "pest",
@@ -10256,12 +10268,6 @@ dependencies = [
  "libc",
 ]
 
-[[package]]
-name = "number_prefix"
-version = "0.4.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "830b246a0e5f20af87141b25c173cd1b609bd7779a4617d6ec582abaf90870f3"
-
 [[package]]
 name = "object"
 version = "0.32.2"
@@ -15450,6 +15456,12 @@ version = "0.2.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "ebc1c04c71510c7f702b52b7c350734c9ff1295c464a03335b00bb84fc54f853"
 
+[[package]]
+name = "unit-prefix"
+version = "0.5.2"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "81e544489bf3d8ef66c953931f56617f423cd4b5494be343d9b9d3dda037b9a3"
+
 [[package]]
 name = "universal-hash"
 version = "0.5.1"
@@ -16025,6 +16037,15 @@ dependencies = [
  "windows-targets 0.53.5",
 ]
 
+[[package]]
+name = "windows-sys"
+version = "0.61.2"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "ae137229bcbd6cdf0f7b80a31df61766145077ddf49416a728b02cb3921ff3fc"
+dependencies = [
+ "windows-link 0.2.1",
+]
+
 [[package]]
 name = "windows-targets"
 version = "0.42.2"
```

### Cargo.toml
```diff
@@ -294,7 +294,7 @@ hyper-rustls = { version = "0.27", default-features = false, features = ["webpki
 hyper-util = { version = "0.1.4", features = ["tokio", "server-auto", "service"] }
 im = "15"
 indexmap = { version = "2.11.0", features = ["serde"] }
-indicatif = "0.17.2"
+indicatif = "0.18.3"
 insta = { version = "1.21.1", features = ["redactions", "yaml", "json"] }
 integer-encoding = "3.0.1"
 itertools = "0.13.0"
```
