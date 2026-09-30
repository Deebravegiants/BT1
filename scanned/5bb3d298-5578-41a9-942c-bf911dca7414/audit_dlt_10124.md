# [?] dep: Upgrade indicatif from 0.16.2 to 0.18.3, resolve https://rustsec.org/advisories/RUSTSEC-2025-0119

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2025-11-20
Source: https://github.com/nervosnetwork/ckb/commit/ab3961e5bfc30af81969f67e02f5dc90aedeb23d
Type: security-commit

## Details
dep: Upgrade indicatif from 0.16.2 to 0.18.3, resolve https://rustsec.org/advisories/RUSTSEC-2025-0119

## Patch
### Cargo.lock
```diff
@@ -3854,14 +3854,15 @@ dependencies = [
 
 [[package]]
 name = "indicatif"
-version = "0.16.2"
+version = "0.18.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "2d207dc617c7a380ab07ff572a6e52fa202a2a8f355860ac9c38e23f8196be1b"
+checksum = "9375e112e4b463ec1b1c6c011953545c65a30164fbab5b581df32b3abf0dcb88"
 dependencies = [
  "console",
- "lazy_static",
- "number_prefix",
- "regex",
+ "portable-atomic",
+ "unicode-width 0.2.2",
+ "unit-prefix",
+ "web-time",
 ]
 
 [[package]]
@@ -4478,12 +4479,6 @@ dependencies = [
  "libc",
 ]
 
-[[package]]
-name = "number_prefix"
-version = "0.4.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "830b246a0e5f20af87141b25c173cd1b609bd7779a4617d6ec582abaf90870f3"
-
 [[package]]
 name = "numext-constructor"
 version = "0.1.6"
@@ -7341,6 +7336,12 @@ version = "0.2.6"
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
```

### Cargo.toml
```diff
@@ -246,7 +246,7 @@ hyper-util = "0.1"
 include_dir = "0.7"
 includedir = "0.6.0"
 includedir_codegen = "0.6.0"
-indicatif = "0.16"
+indicatif = "0.18"
 ipnetwork = "0.20"
 is-terminal = "0.4.7"
 is_sorted = "0.1.1"
```
