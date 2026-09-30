# [?] fix: RUSTSEC-2018-0018

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2020-11-02
Source: https://github.com/nervosnetwork/ckb/commit/3e64e407e0c491600f8185d39f55e62848af680d
Type: security-commit

## Details
fix: RUSTSEC-2018-0018

Advisory: https://rustsec.org/advisories/RUSTSEC-2018-0018

## Patch
### Cargo.lock
```diff
@@ -1709,7 +1709,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "6fdb60074c9b82c91f8702fa5351b85d22b668dae7f73bf06b44a09bc372380f"
 dependencies = [
  "hashbrown 0.5.0",
- "smallvec 0.6.10",
+ "smallvec 0.6.13",
 ]
 
 [[package]]
@@ -3309,7 +3309,7 @@ dependencies = [
  "petgraph",
  "rand 0.6.5",
  "rustc_version",
- "smallvec 0.6.10",
+ "smallvec 0.6.13",
  "thread-id",
  "winapi 0.3.8",
 ]
@@ -3325,7 +3325,7 @@ dependencies = [
  "libc",
  "redox_syscall",
  "rustc_version",
- "smallvec 0.6.10",
+ "smallvec 0.6.13",
  "winapi 0.3.8",
 ]
 
@@ -4290,9 +4290,12 @@ checksum = "c111b5bd5695e56cffe5129854aa230b39c93a305372fdbb2668ca2394eea9f8"
 
 [[package]]
 name = "smallvec"
-version = "0.6.10"
+version = "0.6.13"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "ab606a9c5e214920bb66c458cd7be8ef094f813f20fe77a54cc7dbfff220d4b7"
+checksum = "f7b0758c52e15a8b5e3691eae6cc559f08eee9406e548a4477ba4e67770a82b6"
+dependencies = [
+ "maybe-uninit",
+]
 
 [[package]]
 name = "smallvec"
@@ -4955,7 +4958,7 @@ version = "0.1.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "141339a08b982d942be2ca06ff8b076563cbe223d1befd5450716790d44e2426"
 dependencies = [
- "smallvec 0.6.10",
+ "smallvec 0.6.13",
 ]
 
 [[package]]
```
