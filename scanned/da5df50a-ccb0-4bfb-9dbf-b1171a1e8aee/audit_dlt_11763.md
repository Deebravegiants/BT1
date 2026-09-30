# [?] Merge pull request #2914 from tenequm/fix/update-tracing-subscriber-vulnerability

## Summary
Severity: Unknown
Chain: Aleo
Component: AleoNet/snarkVM-test
Published: 2025-09-04
Source: https://github.com/AleoNet/snarkVM-test/commit/aeba4912057416a3f612dd04ff907031fa9541eb
Type: security-commit

## Details
Merge pull request #2914 from tenequm/fix/update-tracing-subscriber-vulnerability

fix: update tracing-subscriber to resolve RUSTSEC-2025-0055

## Patch
### Cargo.lock
```diff
@@ -461,19 +461,19 @@ dependencies = [
 
 [[package]]
 name = "clap"
-version = "4.5.46"
+version = "4.5.47"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "2c5e4fcf9c21d2e544ca1ee9d8552de13019a42aa7dbf32747fa7aaf1df76e57"
+checksum = "7eac00902d9d136acd712710d71823fb8ac8004ca445a89e73a41d45aa712931"
 dependencies = [
  "clap_builder",
  "clap_derive",
 ]
 
 [[package]]
 name = "clap_builder"
-version = "4.5.46"
+version = "4.5.47"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "fecb53a0e6fcfb055f686001bc2e2592fa527efaf38dbe81a6a9563562e57d41"
+checksum = "2ad9bbf750e73b5884fb8a211a9424a1906c1e156724260fdae972f31d70e1d6"
 dependencies = [
  "anstream",
  "anstyle",
@@ -483,9 +483,9 @@ dependencies = [
 
 [[package]]
 name = "clap_derive"
-version = "4.5.45"
+version = "4.5.47"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "14cb31bb0a7d536caef2639baa7fad459e15c3144efefa6dbd1c84562c4739f6"
+checksum = "bbfd7eae0b0f1a6e63d4b13c9c478de77c2eb546fba158ad50b4203dc24b9f9c"
 dependencies = [
  "heck",
  "proc-macro2",
@@ -1737,11 +1737,11 @@ dependencies = [
 
 [[package]]
 name = "matchers"
-version = "0.1.0"
+version = "0.2.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8263075bb86c5a1b1427b5ae862e8889656f126e9f77c484496e8b47cf5c5558"
+checksum = "d1525a2a28c7f4fa0fc98bb91ae755d1e2d1505079e05539e35bc876b5d65ae9"
 dependencies = [
- "regex-automata 0.1.10",
+ "regex-automata",
 ]
 
 [[package]]
@@ -1837,12 +1837,11 @@ dependencies = [
 
 [[package]]
 name = "nu-ansi-term"
-version = "0.46.0"
+version = "0.50.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "77a8165726e8236064dbb45459242600304b42a5ea24ee2948e18e023bf7ba84"
+checksum = "d4a28e057d01f97e61255210fcff094d74ed0466038633e95017f5beb68e4399"
 dependencies = [
- "overload",
- "winapi",
+ "windows-sys 0.52.0",
 ]
 
 [[package]]
@@ -1988,12 +1987,6 @@ dependencies = [
  "vcpkg",
 ]
 
-[[package]]
-name = "overload"
-version = "0.1.1"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b15813163c1d831bf4a13c3610c05c0d03b39feb07f7e09fa234dac9b15aaf39"
-
 [[package]]
 name = "parking_lot"
 version = "0.12.4"
@@ -2144,7 +2137,7 @@ dependencies = [
  "rand 0.9.2",
  "rand_chacha 0.9.0",
  "rand_xorshift 0.4.0",
- "regex-syntax 0.8.6",
+ "regex-syntax",
  "rusty-fork",
  "tempfile",
  "unarray",
@@ -2376,17 +2369,8 @@ checksum = "23d7fd106d8c02486a8d64e778353d1cffe08ce79ac2e82f540c86d0facf6912"
 dependencies = [
  "aho-corasick",
  "memchr",
- "regex-automata 0.4.10",
- "regex-syntax 0.8.6",
-]
-
-[[package]]
-name = "regex-automata"
-version = "0.1.10"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6c230d73fb8d8c1b9c0b3135c5142a8acee3a0558fb8db5cf1cb65f8d7862132"
-dependencies = [
- "regex-syntax 0.6.29",
+ "regex-automata",
+ "regex-syntax",
 ]
 
 [[package]]
@@ -2397,15 +2381,9 @@ checksum = "6b9458fa0bfeeac22b5ca447c63aaf45f28439a709ccd244698632f9aa6394d6"
 dependencies = [
  "aho-corasick",
  "memchr",
- "regex-syntax 0.8.6",
+ "regex-syntax",
 ]
 
-[[package]]
-name = "regex-syntax"
-version = "0.6.29"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f162c6dd7b008981e4d40210aca20b4bd0f9b60ca9271061b07f78537722f2e1"
-
 [[package]]
 name = "regex-syntax"
 version = "0.8.6"
@@ -4273,14 +4251,14 @@ dependencies = [
 
 [[package]]
 name = "tracing-subscriber"
-version = "0.3.19"
+version = "0.3.20"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e8189decb5ac0fa7bc8b96b7cb9b2701d60d48805aca84a238004d665fcc4008"
+checksum = "2054a14f5307d601f88daf0553e1cbf472acc4f2c51afab632431cdcd72124d5"
 dependencies = [
  "matchers",
  "nu-ansi-term",
  "once_cell",
- "regex",
+ "regex-automata",
  "sharded-slab",
  "smallvec",
  "thread_local",
```

### ledger/store/Cargo.toml
```diff
@@ -124,4 +124,4 @@ path = "../../ledger/test-helpers"
 workspace = true
 
 [dev-dependencies.tracing-test]
-version = "0.2"
+version = "0.2.5"
```
