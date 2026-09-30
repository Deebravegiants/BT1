# [?] deps: fix crate vulnerabilities

## Summary
Severity: Unknown
Chain: Namada
Component: namada-net/namada
Published: 2024-12-31
Source: https://github.com/namada-net/namada/commit/2b69df184a906144a253592b1cf154f91d04f62f
Type: security-commit

## Details
deps: fix crate vulnerabilities

## Patch
### Cargo.lock
```diff
@@ -545,7 +545,7 @@ dependencies = [
  "bitflags 2.5.0",
  "cexpr",
  "clang-sys",
- "itertools 0.12.1",
+ "itertools 0.10.5",
  "lazy_static",
  "lazycell",
  "proc-macro2",
@@ -1466,9 +1466,9 @@ dependencies = [
 
 [[package]]
 name = "critical-section"
-version = "1.1.2"
+version = "1.2.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7059fff8937831a9ae6f0fe4d658ffabf58f2ca96aa9dec1c889f936f705f216"
+checksum = "790eea4361631c5e7d22598ecd5723ff611904e3344ce8720784c93e3d83d40b"
 
 [[package]]
 name = "crossbeam-channel"
@@ -1569,16 +1569,15 @@ checksum = "b365fabc795046672053e29c954733ec3b05e4be654ab130fe8f1f94d7051f35"
 
 [[package]]
 name = "curve25519-dalek"
-version = "4.1.2"
+version = "4.1.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0a677b8922c94e01bdbb12126b0bc852f00447528dee1782229af9c720c3f348"
+checksum = "97fb8b7c4503de7d6ae7b42ab72a5a59857b4c937ec27a3d4539dba95b5ab2be"
 dependencies = [
  "cfg-if",
  "cpufeatures",
  "curve25519-dalek-derive",
  "digest 0.10.7",
  "fiat-crypto",
- "platforms",
  "rustc_version 0.4.0",
  "subtle",
  "zeroize",
@@ -2782,19 +2781,19 @@ dependencies = [
 
 [[package]]
 name = "futures-channel"
-version = "0.3.29"
+version = "0.3.31"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "ff4dd66668b557604244583e3e1e1eada8c5c2e96a6d0d6653ede395b78bbacb"
+checksum = "2dff15bf788c671c1934e366d07e30c1814a8ef514e1af724a602e8a2fbe1b10"
 dependencies = [
  "futures-core",
  "futures-sink",
 ]
 
 [[package]]
 name = "futures-core"
-version = "0.3.29"
+version = "0.3.31"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "eb1d22c66e66d9d72e1758f0bd7d4fd0bee04cad842ee34587d68c07e45d088c"
+checksum = "05f29059c0c2090612e8d742178b0580d2dc940c837851ad723096f87af6663e"
 
 [[package]]
 name = "futures-executor"
@@ -2809,9 +2808,9 @@ dependencies = [
 
 [[package]]
 name = "futures-io"
-version = "0.3.29"
+version = "0.3.31"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8bf34a163b5c4c52d0478a4d757da8fb65cabef42ba90515efee0f6f9fa45aaa"
+checksum = "9e5c1b78ca4aae1ac06c48a526a655760685149f0d465d21f37abfe57ce075c6"
 
 [[package]]
 name = "futures-locks"
@@ -2825,9 +2824,9 @@ dependencies = [
 
 [[package]]
 name = "futures-macro"
-version = "0.3.29"
+version = "0.3.31"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "53b153fd91e4b0147f4aced87be237c98248656bb01050b96bf3ee89220a8ddb"
+checksum = "162ee34ebcb7c64a8abebc059ce0fee27c2262618d7b60ed8faf72fef13c3650"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -2836,15 +2835,15 @@ dependencies = [
 
 [[package]]
 name = "futures-sink"
-version = "0.3.29"
+version = "0.3.31"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e36d3378ee38c2a36ad710c5d30c2911d752cb941c00c72dbabfb786a7970817"
+checksum = "e575fab7d1e0dcb8d0c7bcf9a63ee213816ab51902e6d244a95819acacf1d4f7"
 
 [[package]]
 name = "futures-task"
-version = "0.3.29"
+version = "0.3.31"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "efd193069b0ddadc69c46389b740bbccdd97203899b48d09c5f7969591d6bae2"
+checksum = "f90f7dce0722e95104fcb095585910c0977252f286e354b5e3bd38902cd99988"
 
 [[package]]
 name = "futures-timer"
@@ -2858,9 +2857,9 @@ dependencies = [
 
 [[package]]
 name = "futures-util"
-version = "0.3.29"
+version = "0.3.31"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a19526d624e703a3179b3d322efec918b6246ea0fa51d41124525f00f1cc8104"
+checksum = "9fa08315bb612088cc391249efdc3bc77536f16c91f6cf495e6fbe85b20a4a81"
 dependencies = [
  "futures-channel",
  "futures-core",
@@ -6334,9 +6333,9 @@ dependencies = [
 
 [[package]]
 name = "openssl"
-version = "0.10.61"
+version = "0.10.68"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6b8419dc8cc6d866deb801274bba2e6f8f6108c1bb7fcc10ee5ab864931dbb45"
+checksum = "6174bc48f102d208783c2c84bf931bb75927a617866870de8a4ea85597f871f5"
 dependencies = [
  "bitflags 2.5.0",
  "cfg-if",
@@ -6366,9 +6365,9 @@ checksum = "ff011a302c396a5197692431fc1948019154afc178baf7d8e37367442a4601cf"
 
 [[package]]
 name = "openssl-sys"
-version = "0.9.97"
+version = "0.9.104"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c3eaad34cdd97d81de97964fc7f29e2d104f483840d906ef56daa1912338460b"
+checksum = "45abf306cbf99debc8195b66b7346498d7b10c210de50418b5ccd7ceba08c741"
 dependencies = [
  "cc",
  "libc",
@@ -6700,12 +6699,6 @@ version = "0.3.27"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "26072860ba924cbfa98ea39c8c19b4dd6a4a25423dbdf219c1eca91aa0cf6964"
 
-[[package]]
-name = "platforms"
-version = "3.2.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "14e6ab3f592e6fb464fc9712d8d6e6912de6473954635fd76a589d832cffcbb0"
-
 [[package]]
 name = "plotters"
 version = "0.3.5"
```
