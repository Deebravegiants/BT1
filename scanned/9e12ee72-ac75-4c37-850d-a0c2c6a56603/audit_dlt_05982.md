# [?] build(deps): bump ruint from 1.17.2 to 1.20.0 to fix RUSTSEC-2026-0220

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-07-31
Source: https://github.com/Conflux-Chain/conflux-rust/commit/1cd7e5e96675351c02d95d2bf0e1cb48751ba5eb
Type: security-commit

## Details
build(deps): bump ruint from 1.17.2 to 1.20.0 to fix RUSTSEC-2026-0220

ruint 1.17.2 has false-negative overflow flags in overflowing_shl/shr
(RUSTSEC-2026-0220), failing cargo-audit and cargo-deny CI jobs on all
branches. ruint is a pure transitive dependency (via the alloy stack),
so only the lockfiles of the three workspaces need updating. The bump
also introduces arkworks 0.6 crates as new optional deps of ruint,
coexisting with the 0.4/0.5 stacks.

## Patch
### Cargo.lock
```diff
@@ -705,6 +705,23 @@ dependencies = [
  "zeroize",
 ]
 
+[[package]]
+name = "ark-ff"
+version = "0.6.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "f7a806ac6c8307b929df4645776290a50ee2aac754ad09d8bdf73391309e43af"
+dependencies = [
+ "ark-ff-asm 0.6.0",
+ "ark-ff-macros 0.6.0",
+ "ark-serialize 0.6.0",
+ "ark-std 0.6.0",
+ "digest 0.10.7",
+ "educe",
+ "num-bigint 0.4.4",
+ "num-traits",
+ "zeroize",
+]
+
 [[package]]
 name = "ark-ff-asm"
 version = "0.3.0"
@@ -735,6 +752,16 @@ dependencies = [
  "syn 2.0.114",
 ]
 
+[[package]]
+name = "ark-ff-asm"
+version = "0.6.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "1479009684adc073dff49a1025d3a7065b317a9ead25aaaca38cdc70058ba8a2"
+dependencies = [
+ "quote",
+ "syn 2.0.114",
+]
+
 [[package]]
 name = "ark-ff-macros"
 version = "0.3.0"
@@ -773,6 +800,19 @@ dependencies = [
  "syn 2.0.114",
 ]
 
+[[package]]
+name = "ark-ff-macros"
+version = "0.6.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "4a0691ed21ef00ef89c1e9bda832eba493dda3ec2f8d892fb25b705f73f06bb8"
+dependencies = [
+ "num-bigint 0.4.4",
+ "num-traits",
+ "proc-macro2",
+ "quote",
+ "syn 2.0.114",
+]
+
 [[package]]
 name = "ark-poly"
 version = "0.5.0"
@@ -844,13 +884,26 @@ version = "0.5.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "3f4d068aaf107ebcd7dfb52bc748f8030e0fc930ac8e360146ca54c1203088f7"
 dependencies = [
- "ark-serialize-derive",
+ "ark-serialize-derive 0.5.0",
  "ark-std 0.5.0",
  "arrayvec",
  "digest 0.10.7",
  "num-bigint 0.4.4",
 ]
 
+[[package]]
+name = "ark-serialize"
+version = "0.6.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "a74dd304fd536fb95d0a328e72be759209cc496a9da094c5bc56e5fea4f9e86b"
+dependencies = [
+ "ark-serialize-derive 0.6.0",
+ "ark-std 0.6.0",
+ "digest 0.10.7",
+ "num-bigint 0.4.4",
+ "serde_with",
+]
+
 [[package]]
 name = "ark-serialize-derive"
 version = "0.5.0"
@@ -862,6 +915,17 @@ dependencies = [
  "syn 2.0.114",
 ]
 
+[[package]]
+name = "ark-serialize-derive"
+version = "0.6.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "4f153690697a2b91e5e1251ff98411ee5371500a111a0fd317a70e588eb300f9"
+dependencies = [
+ "proc-macro2",
+ "quote",
+ "syn 2.0.114",
+]
+
 [[package]]
 name = "ark-std"
 version = "0.3.0"
@@ -892,6 +956,16 @@ dependencies = [
  "rand 0.8.6",
 ]
 
+[[package]]
+name = "ark-std"
+version = "0.6.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "367c9c827ed431bff6868b7aa926e05b16eb46603cc8b6e768e4a5553fa1d155"
+dependencies = [
+ "num-traits",
+ "rand 0.8.6",
+]
+
 [[package]]
 name = "array-macro"
 version = "1.0.5"
@@ -3711,7 +3785,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "778e2ac28f6c47af28e4907f13ffd1e1ddbd400980a9abd7c8df189bf578a5ad"
 dependencies = [
  "libc",
- "windows-sys 0.60.2",
+ "windows-sys 0.52.0",
 ]
 
 [[package]]
@@ -7613,14 +7687,15 @@ dependencies = [
 
 [[package]]
 name = "ruint"
-version = "1.17.2"
+version = "1.20.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c141e807189ad38a07276942c6623032d3753c8859c146104ac2e4d68865945a"
+checksum = "f5e99bff0393163bb25029a6af25d3d8d202ba5b5438a74d1bd8789f5c822970"
 dependencies = [
  "alloy-rlp",
  "ark-ff 0.3.0",
  "ark-ff 0.4.2",
  "ark-ff 0.5.0",
+ "ark-ff 0.6.0",
  "bytes",
  "fastrlp 0.3.1",
  "fastrlp 0.4.0",
@@ -7720,7 +7795,7 @@ dependencies = [
  "errno",
  "libc",
  "linux-raw-sys 0.9.4",
- "windows-sys 0.60.2",
+ "windows-sys 0.52.0",
 ]
 
 [[package]]
@@ -8841,7 +8916,7 @@ dependencies = [
  "getrandom 0.3.2",
  "once_cell",
  "rustix 1.0.8",
- "windows-sys 0.60.2",
+ "windows-sys 0.52.0",
 ]
 
 [[package]]
```

### tools/consensus_bench/Cargo.lock
```diff
@@ -689,6 +689,23 @@ dependencies = [
  "zeroize",
 ]
 
+[[package]]
+name = "ark-ff"
+version = "0.6.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "f7a806ac6c8307b929df4645776290a50ee2aac754ad09d8bdf73391309e43af"
+dependencies = [
+ "ark-ff-asm 0.6.0",
+ "ark-ff-macros 0.6.0",
+ "ark-serialize 0.6.0",
+ "ark-std 0.6.0",
+ "digest 0.10.7",
+ "educe",
+ "num-bigint",
+ "num-traits",
+ "zeroize",
+]
+
 [[package]]
 name = "ark-ff-asm"
 version = "0.3.0"
@@ -719,6 +736,16 @@ dependencies = [
  "syn 2.0.111",
 ]
 
+[[package]]
+name = "ark-ff-asm"
+version = "0.6.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "1479009684adc073dff49a1025d3a7065b317a9ead25aaaca38cdc70058ba8a2"
+dependencies = [
+ "quote",
+ "syn 2.0.111",
+]
+
 [[package]]
 name = "ark-ff-macros"
 version = "0.3.0"
@@ -757,6 +784,19 @@ dependencies = [
  "syn 2.0.111",
 ]
 
+[[package]]
+name = "ark-ff-macros"
+version = "0.6.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "4a0691ed21ef00ef89c1e9bda832eba493dda3ec2f8d892fb25b705f73f06bb8"
+dependencies = [
+ "num-bigint",
+ "num-traits",
+ "proc-macro2",
+ "quote",
+ "syn 2.0.111",
+]
+
 [[package]]
 name = "ark-poly"
 version = "0.5.0"
@@ -828,13 +868,26 @@ version = "0.5.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "3f4d068aaf107ebcd7dfb52bc748f8030e0fc930ac8e360146ca54c1203088f7"
 dependencies = [
- "ark-serialize-derive",
+ "ark-serialize-derive 0.5.0",
  "ark-std 0.5.0",
  "arrayvec",
  "digest 0.10.7",
  "num-bigint",
 ]
 
+[[package]]
+name = "ark-serialize"
+version = "0.6.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "a74dd304fd536fb95d0a328e72be759209cc496a9da094c5bc56e5fea4f9e86b"
+dependencies = [
+ "ark-serialize-derive 0.6.0",
+ "ark-std 0.6.0",
+ "digest 0.10.7",
+ "num-bigint",
+ "serde_with",
+]
+
 [[package]]
 name = "ark-serialize-derive"
 version = "0.5.0"
@@ -846,6 +899,17 @@ dependencies = [
  "syn 2.0.111",
 ]
 
+[[package]]
+name = "ark-serialize-derive"
+version = "0.6.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "4f153690697a2b91e5e1251ff98411ee5371500a111a0fd317a70e588eb300f9"
+dependencies = [
+ "proc-macro2",
+ "quote",
+ "syn 2.0.111",
+]
+
 [[package]]
 name = "ark-std"
 version = "0.3.0"
@@ -876,6 +940,16 @@ dependencies = [
  "rand 0.8.6",
 ]
 
+[[package]]
+name = "ark-std"
+version = "0.6.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "367c9c827ed431bff6868b7aa926e05b16eb46603cc8b6e768e4a5553fa1d155"
+dependencies = [
+ "num-traits",
+ "rand 0.8.6",
+]
+
 [[package]]
 name = "array-macro"
 version = "1.0.5"
@@ -6003,14 +6077,15 @@ dependencies = [
 
 [[package]]
 name = "ruint"
-version = "1.17.2"
+version = "1.20.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c141e807189ad38a07276942c6623032d3753c8859c146104ac2e4d68865945a"
+checksum = "f5e99bff0393163bb25029a6af25d3d8d202ba5b5438a74d1bd8789f5c822970"
 dependencies = [
  "alloy-rlp",
  "ark-ff 0.3.0",
  "ark-ff 0.4.2",
  "ark-ff 0.5.0",
+ "ark-ff 0.6.0",
  "bytes",
  "fastrlp 0.3.1",
  "fastrlp 0.4.0",
```

### tools/evm-spec-tester/Cargo.lock
```diff
@@ -689,6 +689,23 @@ dependencies = [
  "zeroize",
 ]
 
+[[package]]
+name = "ark-ff"
+version = "0.6.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "f7a806ac6c8307b929df4645776290a50ee2aac754ad09d8bdf73391309e43af"
+dependencies = [
+ "ark-ff-asm 0.6.0",
+ "ark-ff-macros 0.6.0",
+ "ark-serialize 0.6.0",
+ "ark-std 0.6.0",
+ "digest 0.10.7",
+ "educe",
+ "num-bigint 0.4.4",
+ "num-traits",
+ "zeroize",
+]
+
 [[package]]
 name = "ark-ff-asm"
 version = "0.3.0"
@@ -719,6 +736,16 @@ dependencies = [
  "syn 2.0.111",
 ]
 
+[[package]]
+name = "ark-ff-asm"
+version = "0.6.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "1479009684adc073dff49a1025d3a7065b317a9ead25aaaca38cdc70058ba8a2"
+dependencies = [
+ "quote",
+ "syn 2.0.111",
+]
+
 [[package]]
 name = "ark-ff-macros"
 version = "0.3.0"
@@ -757,6 +784,19 @@ dependencies = [
  "syn 2.0.111",
 ]
 
+[[package]]
+name = "ark-ff-macros"
+version = "0.6.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "4a0691ed21ef00ef89c1e9bda832eba493dda3ec2f8d892fb25b705f73f06bb8"
+dependencies = [
+ "num-bigint 0.4.4",
+ "num-traits",
+ "proc-macro2",
+ "quote",
+ "syn 2.0.111",
+]
+
 [[package]]
 name = "ark-poly"
 version = "0.5.0"
@@ -828,13 +868,26 @@ version = "0.5.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "3f4d068aaf107ebcd7dfb52bc748f8030e0fc930ac8e360146ca54c1203088f7"
 dependencies = [
- "ark-serialize-derive",
+ "ark-serialize-derive 0.5.0",
  "ark-std 0.5.0",
  "arrayvec",
  "digest 0.10.7",
  "num-bigint 0.4.4",
 ]
 
+[[package]]
+name = "ark-serialize"
+version = "0.6.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "a74dd304fd536fb95d0a328e72be759209cc496a9da094c5bc56e5fea4f9e86b"
+dependencies = [
+ "ark-serialize-derive 0.6.0",
+ "ark-std 0.6.0",
+ "digest 0.10.7",
+ "num-bigint 0.4.4",
+ "serde_with",
+]
+
 [[package]]
 name = "ark-serialize-derive"
 version = "0.5.0"
@@ -846,6 +899,17 @@ dependencies = [
  "syn 2.0.111",
 ]
 
+[[package]]
+name = "ark-serialize-derive"
+version = "0.6.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "4f153690697a2b91e5e1251ff98411ee5371500a111a0fd317a70e588eb300f9"
+dependencies = [
+ "proc-macro2",
+ "quote",
+ "syn 2.0.111",
+]
+
 [[package]]
 name = "ark-std"
 version = "0.3.0"
@@ -876,6 +940,16 @@ dependencies = [
  "rand 0.8.6",
 ]
 
+[[package]]
+name = "ark-std"
+version = "0.6.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "367c9c827ed431bff6868b7aa926e05b16eb46603cc8b6e768e4a5553fa1d155"
+dependencies = [
+ "num-traits",
+ "rand 0.8.6",
+]
+
 [[package]]
 name = "array-macro"
 version = "1.0.5"
@@ -6620,14 +6694,15 @@ dependencies = [
 
 [[package]]
 name = "ruint"
-version = "1.17.2"
+version = "1.20.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c141e807189ad38a07276942c6623032d3753c8859c146104ac2e4d68865945a"
+checksum = "f5e99bff0393163bb25029a6af25d3d8d202ba5b5438a74d1bd8789f5c822970"
 dependencies = [
  "alloy-rlp",
  "ark-ff 0.3.0",
  "ark-ff 0.4.2",
  "ark-ff 0.5.0",
+ "ark-ff 0.6.0",
  "bytes",
  "fastrlp 0.3.1",
  "fastrlp 0.4.0",
```
