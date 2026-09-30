# [?] chore(deps): bump smallvec from 0.6.13 / 1.3.0 to 0.6.14 / 1.6.1 to fix RUSTSEC-2021-0003

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2021-01-11
Source: https://github.com/nervosnetwork/ckb/commit/5b09bfa4bf436a8aa5e1746b2dc3bf0bd246a3aa
Type: security-commit

## Details
chore(deps): bump smallvec from 0.6.13 / 1.3.0 to 0.6.14 / 1.6.1 to fix RUSTSEC-2021-0003

## Patch
### Cargo.lock
```diff
@@ -3599,7 +3599,7 @@ dependencies = [
  "libc",
  "rand 0.6.5",
  "rustc_version",
- "smallvec 0.6.13",
+ "smallvec 0.6.14",
  "winapi 0.3.8",
 ]
 
@@ -3615,7 +3615,7 @@ dependencies = [
  "libc",
  "petgraph",
  "redox_syscall",
- "smallvec 1.3.0",
+ "smallvec 1.6.1",
  "thread-id",
  "winapi 0.3.8",
 ]
@@ -3630,7 +3630,7 @@ dependencies = [
  "instant",
  "libc",
  "redox_syscall",
- "smallvec 1.3.0",
+ "smallvec 1.6.1",
  "winapi 0.3.8",
 ]
 
@@ -4505,18 +4505,18 @@ checksum = "c111b5bd5695e56cffe5129854aa230b39c93a305372fdbb2668ca2394eea9f8"
 
 [[package]]
 name = "smallvec"
-version = "0.6.13"
+version = "0.6.14"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f7b0758c52e15a8b5e3691eae6cc559f08eee9406e548a4477ba4e67770a82b6"
+checksum = "b97fcaeba89edba30f044a10c6a3cc39df9c3f17d7cd829dd1446cab35f890e0"
 dependencies = [
  "maybe-uninit",
 ]
 
 [[package]]
 name = "smallvec"
-version = "1.3.0"
+version = "1.6.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "05720e22615919e4734f6a99ceae50d00226c3c5aca406e102ebc33298214e0a"
+checksum = "fe0f37c9e8f3c5a4a66ad655a93c74daac4ad00c441533bf5c6e7990bb42604e"
 
 [[package]]
 name = "snap"
@@ -5107,7 +5107,7 @@ dependencies = [
  "lazy_static",
  "log",
  "rand 0.7.3",
- "smallvec 1.3.0",
+ "smallvec 1.6.1",
  "thiserror",
  "tokio 0.2.24",
  "url",
@@ -5127,7 +5127,7 @@ dependencies = [
  "log",
  "lru-cache",
  "resolv-conf",
- "smallvec 1.3.0",
+ "smallvec 1.6.1",
  "thiserror",
  "tokio 0.2.24",
  "trust-dns-proto",
@@ -5178,7 +5178,7 @@ version = "0.1.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "141339a08b982d942be2ca06ff8b076563cbe223d1befd5450716790d44e2426"
 dependencies = [
- "smallvec 0.6.13",
+ "smallvec 0.6.14",
 ]
 
 [[package]]
```
