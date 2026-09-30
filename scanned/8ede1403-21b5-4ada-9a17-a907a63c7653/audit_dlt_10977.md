# [?] fix: sspark out of bounds initialization (#219)

## Summary
Severity: Unknown
Chain: ZK
Component: succinctlabs/sp1
Published: 2025-11-17
Source: https://github.com/succinctlabs/sp1/commit/728085b508ee53b92b9bb720bfc922857676c8c3
Type: security-commit

## Details
fix: sspark out of bounds initialization (#219)

* overflow

* update dep

## Patch
### Cargo.lock
```diff
@@ -105,22 +105,22 @@ dependencies = [
 
 [[package]]
 name = "anstyle-query"
-version = "1.1.4"
+version = "1.1.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9e231f6134f61b71076a3eab506c379d4f36122f2af15a9ff04415ea4c3339e2"
+checksum = "40c48f72fd53cd289104fc64099abca73db4166ad86ea0b4341abe65af83dadc"
 dependencies = [
- "windows-sys 0.60.2",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
 name = "anstyle-wincon"
-version = "3.0.10"
+version = "3.0.11"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "3e0633414522a32ffaac8ac6cc8f748e090c5717661fddeea04219e2344f5f2a"
+checksum = "291e6a250ff86cd4a820112fb8898808a366d8f9f58ce16d1f538353ad55747d"
 dependencies = [
  "anstyle",
  "once_cell_polyfill",
- "windows-sys 0.60.2",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
@@ -556,9 +556,9 @@ checksum = "1fd0f2584146f6f2ef48085050886acf353beff7305ebd1ae69500e27c67f64b"
 
 [[package]]
 name = "bytes"
-version = "1.10.1"
+version = "1.11.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d71b6127be86fdcfddb610f7182ac57211d4b18a3e9c82eb2d17662f2227ad6a"
+checksum = "b35204fbdc0b3f4446b89fc1ac2cf84a8a68971995d0bf2e925ec7cd960f9cb3"
 
 [[package]]
 name = "camino"
@@ -613,9 +613,9 @@ dependencies = [
 
 [[package]]
 name = "cc"
-version = "1.2.45"
+version = "1.2.46"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "35900b6c8d709fb1d854671ae27aeaa9eec2f8b01b364e1619a40da3e6fe2afe"
+checksum = "b97463e1064cb1b1c1384ad0a0b9c8abd0988e2a91f52606c80ef14aadb63e36"
 dependencies = [
  "find-msvc-tools",
  "jobserver",
@@ -668,19 +668,19 @@ dependencies = [
 
 [[package]]
 name = "clap"
-version = "4.5.51"
+version = "4.5.52"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "4c26d721170e0295f191a69bd9a1f93efcdb0aff38684b61ab5750468972e5f5"
+checksum = "aa8120877db0e5c011242f96806ce3c94e0737ab8108532a76a3300a01db2ab8"
 dependencies = [
  "clap_builder",
  "clap_derive",
 ]
 
 [[package]]
 name = "clap_builder"
-version = "4.5.51"
+version = "4.5.52"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "75835f0c7bf681bfd05abe44e965760fea999a5286c6eb2d59883634fd02011a"
+checksum = "02576b399397b659c26064fbc92a75fede9d18ffd5f80ca1cd74ddab167016e1"
 dependencies = [
  "anstream",
  "anstyle",
@@ -1979,9 +1979,9 @@ dependencies = [
 
 [[package]]
 name = "find-msvc-tools"
-version = "0.1.4"
+version = "0.1.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "52051878f80a721bb68ebfbc930e07b65ba72f2da88968ea5c06fd6ca3d3a127"
+checksum = "3a3076410a55c90011c298b04d0cfa770b00fa04e1e3c97d3f6c9de105a03844"
 
 [[package]]
 name = "fixedbitset"
@@ -2450,9 +2450,9 @@ dependencies = [
 
 [[package]]
 name = "hyper"
-version = "1.8.0"
+version = "1.8.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1744436df46f0bde35af3eda22aeaba453aada65d8f1c171cd8a5f59030bd69f"
+checksum = "2ab2d4f250c3d7b1c9fcdff1cece94ea4e2dfbec68614f7b87cb205f24ca9d11"
 dependencies = [
  "atomic-waker",
  "bytes",
@@ -2478,7 +2478,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "e3c93eb611681b207e1fe55d5a71ecf91572ec8a6705cdb6857f7d8d5242cf58"
 dependencies = [
  "http 1.3.1",
- "hyper 1.8.0",
+ "hyper 1.8.1",
  "hyper-util",
  "rustls",
  "rustls-pki-types",
@@ -2506,7 +2506,7 @@ version = "0.5.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "2b90d566bffbce6a75bd8b09a05aa8c2cb1fabb6cb348f8840c9e4c90a0d83b0"
 dependencies = [
- "hyper 1.8.0",
+ "hyper 1.8.1",
  "hyper-util",
  "pin-project-lite",
  "tokio",
@@ -2515,9 +2515,9 @@ dependencies = [
 
 [[package]]
 name = "hyper-util"
-version = "0.1.17"
+version = "0.1.18"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "3c6995591a8f1380fcb4ba966a252a4b29188d51d2b89e3a252f5305be65aea8"
+checksum = "52e9a2a24dc5c6821e71a7030e1e14b7b632acac55c40e9d2e082c621261bb56"
 dependencies = [
  "base64 0.22.1",
  "bytes",
@@ -2526,7 +2526,7 @@ dependencies = [
  "futures-util",
  "http 1.3.1",
  "http-body 1.0.1",
- "hyper 1.8.0",
+ "hyper 1.8.1",
  "ipnet",
  "libc",
  "percent-encoding",
@@ -2549,7 +2549,7 @@ dependencies = [
  "js-sys",
  "log",
  "wasm-bindgen",
- "windows-core 0.57.0",
+ "windows-core 0.62.2",
 ]
 
 [[package]]
@@ -3992,7 +3992,7 @@ version = "0.13.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "be769465445e8c1474e9c5dac2018218498557af32d9ed057325ec9a41ae81bf"
 dependencies = [
- "heck 0.4.1",
+ "heck 0.5.0",
  "itertools 0.14.0",
  "log",
  "multimap",
@@ -4278,7 +4278,7 @@ dependencies = [
  "http 1.3.1",
  "http-body 1.0.1",
  "http-body-util",
- "hyper 1.8.0",
+ "hyper 1.8.1",
  "hyper-rustls",
  "hyper-util",
  "js-sys",
@@ -4714,15 +4714,15 @@ checksum = "7a2ae44ef20feb57a68b23d846850f861394c2e02dc425a50098ae8c90267589"
 [[package]]
 name = "slop-air"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "p3-air",
 ]
 
 [[package]]
 name = "slop-algebra"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "itertools 0.13.0",
  "p3-field 0.1.0",
@@ -4732,7 +4732,7 @@ dependencies = [
 [[package]]
 name = "slop-alloc"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "serde",
  "slop-algebra",
@@ -4742,7 +4742,7 @@ dependencies = [
 [[package]]
 name = "slop-baby-bear"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "lazy_static",
  "p3-baby-bear 0.1.0",
@@ -4756,7 +4756,7 @@ dependencies = [
 [[package]]
 name = "slop-basefold"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "derive-where",
  "itertools 0.13.0",
@@ -4778,7 +4778,7 @@ dependencies = [
 [[package]]
 name = "slop-basefold-prover"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "derive-where",
  "itertools 0.13.0",
@@ -4805,7 +4805,7 @@ dependencies = [
 [[package]]
 name = "slop-bn254"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "ff 0.13.1",
  "p3-bn254-fr",
@@ -4820,7 +4820,7 @@ dependencies = [
 [[package]]
 name = "slop-challenger"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "futures",
  "p3-challenger",
@@ -4832,7 +4832,7 @@ dependencies = [
 [[package]]
 name = "slop-commit"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "p3-commit",
  "serde",
@@ -4842,7 +4842,7 @@ dependencies = [
 [[package]]
 name = "slop-dft"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "p3-dft 0.1.0",
  "serde",
@@ -4855,15 +4855,15 @@ dependencies = [
 [[package]]
 name = "slop-fri"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "p3-fri",
 ]
 
 [[package]]
 name = "slop-futures"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "crossbeam",
  "futures",
@@ -4877,7 +4877,7 @@ dependencies = [
 [[package]]
 name = "slop-jagged"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "derive-where",
  "futures",
@@ -4910,15 +4910,15 @@ dependencies = [
 [[package]]
 name = "slop-keccak-air"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "p3-keccak-air",
 ]
 
 [[package]]
 name = "slop-koala-bear"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "lazy_static",
  "p3-koala-bear",
@@ -4932,23 +4932,23 @@ dependencies = [
 [[package]]
 name = "slop-matrix"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "p3-matrix 0.1.0",
 ]
 
 [[package]]
 name = "slop-maybe-rayon"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "p3-maybe-rayon 0.1.0",
 ]
 
 [[package]]
 name = "slop-merkle-tree"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "derive-where",
  "ff 0.13.1",
@@ -4975,7 +4975,7 @@ dependencies = [
 [[package]]
 name = "slop-multilinear"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "derive-where",
  "futures",
@@ -4996,23 +4996,23 @@ dependencies = [
 [[package]]
 name = "slop-poseidon2"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "p3-poseidon2 0.1.0",
 ]
 
 [[package]]
 name = "slop-primitives"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "slop-algebra",
 ]
 
 [[package]]
 name = "slop-stacked"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "derive-where",
  "futures",
@@ -5032,7 +5032,7 @@ dependencies = [
 [[package]]
 name = "slop-sumcheck"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "futures",
  "itertools 0.13.0",
@@ -5049,15 +5049,15 @@ dependencies = [
 [[package]]
 name = "slop-symmetric"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "p3-symmetric 0.1.0",
 ]
 
 [[package]]
 name = "slop-tensor"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "arrayvec",
  "derive-where",
@@ -5077,15 +5077,15 @@ dependencies = [
 [[package]]
 name = "slop-uni-stark"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "p3-uni-stark",
 ]
 
 [[package]]
 name = "slop-utils"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "p3-util 0.1.0",
  "tracing-forest",
@@ -5095,7 +5095,7 @@ dependencies = [
 [[package]]
 name = "slop-whir"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "derive-where",
  "futures",
@@ -5163,7 +5163,7 @@ dependencies = [
 [[package]]
 name = "sp1-build"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "anyhow",
  "cargo_metadata",
@@ -5176,7 +5176,7 @@ dependencies = [
 [[package]]
 name = "sp1-core-executor"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "bincode",
  "bytemuck",
@@ -5215,7 +5215,7 @@ dependencies = [
 [[package]]
 name = "sp1-core-machine"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "bincode",
  "cfg-if",
@@ -5261,7 +5261,7 @@ dependencies = [
 [[package]]
 name = "sp1-cuda"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "bincode",
  "bytes",
@@ -5280,7 +5280,7 @@ dependencies = [
 [[package]]
 name = "sp1-curves"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "cfg-if",
  "dashu",
@@ -5301,7 +5301,7 @@ dependencies = [
 [[package]]
 name = "sp1-derive"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -5311,7 +5311,7 @@ dependencies = [
 [[package]]
 name = "sp1-hypercube"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "arrayref",
  "deepsize2",
@@ -5356,7 +5356,7 @@ dependencies = [
 [[package]]
 name = "sp1-jit"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "dynasmrt",
  "hashbrown 0.14.5",
@@ -5402,7 +5402,7 @@ dependencies = [
 [[package]]
 name = "sp1-primitives"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "bincode",
  "blake3",
@@ -5425,7 +5425,7 @@ dependencies = [
 [[package]]
 name = "sp1-prover"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "anyhow",
  "bincode",
@@ -5484,7 +5484,7 @@ dependencies = [
 [[package]]
 name = "sp1-prover-types"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "anyhow",
  "async-scoped",
@@ -5504,7 +5504,7 @@ dependencies = [
 [[package]]
 name = "sp1-recursion-circuit"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "itertools 0.13.0",
  "rand 0.8.5",
@@ -5542,7 +5542,7 @@ dependencies = [
 [[package]]
 name = "sp1-recursion-compiler"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "backtrace",
  "cfg-if",
@@ -5562,7 +5562,7 @@ dependencies = [
 [[package]]
 name = "sp1-recursion-executor"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "backtrace",
  "cfg-if",
@@ -5585,7 +5585,7 @@ dependencies = [
 [[package]]
 name = "sp1-recursion-gnark-ffi"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "anyhow",
  "bincode",
@@ -5609,7 +5609,7 @@ dependencies = [
 [[package]]
 name = "sp1-recursion-machine"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "itertools 0.13.0",
  "rand 0.8.5",
@@ -5631,7 +5631,7 @@ dependencies = [
 [[package]]
 name = "sp1-sdk"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "anyhow",
  "async-trait",
@@ -5665,7 +5665,7 @@ dependencies = [
 [[package]]
 name = "sp1-verifier"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#028b742a2dd57026ea3d8b7a697b7bc055a2270f"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#ffb282aca8b31a1c8f8a29549b83f9db28c6803b"
 dependencies = [
  "bincode",
  "blake3",
@@ -6226,7 +6226,7 @@ dependencies = [
  "http 1.3.1",
  "http-body 1.0.1",
  "http-body-util",
- "hyper 1.8.0",
+ "hyper 1.8.1",
  "hyper-timeout 0.5.2",
  "hyper-util",
  "percent-encoding",
@@ -6732,12 +6732,25 @@ version = "0.57.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "d2ed2439a290666cd67ecce2b0ffaad89c2a56b976b736e6ece670297897832d"
 dependencies = [
- "windows-implement",
- "windows-interface",
- "windows-result",
+ "windows-implement 0.57.0",
+ "windows-interface 0.57.0",
+ "windows-result 0.1.2",
  "windows-targets 0.52.6",
 ]
 
+[[package]]
+name = "windows-core"
+version = "0.62.2"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "b8e83a14d34d0623b51dce9581199302a221863196a1dde71a7663a4c2be9deb"
+dependencies = [
+ "windows-implement 0.60.2",
+ "windows-interface 0.59.3",
+ "windows-link",
+ "windows-result 0.4.1",
+ "windows-strings",
+]
+
 [[package]]
 name = "windows-implement"
 version = "0.57.0"
@@ -6749,6 +6762,17 @@ dependencies = [
  "syn 2.0.110",
 ]
 
+[[package]]
+name = "windows-implement"
+version = "0.60.2"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "053e2e040ab57b9dc951b72c264860db7eb3b0200ba345b4e4c3b14f67855ddf"
+dependencies = [
+ "proc-macro2",
+ "quote",
+ "syn 2.0.110",
+]
+
 [[package]]
 name = "windows-interface"
 version = "0.57.0"
@@ -6760,6 +6784,17 @@ dependencies = [
  "syn 2.0.110",
 ]
 
+[[package]]
+name = "windows-interface"
+version = "0.59.3"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "3f316c4a2570ba26bbec722032c4099d8c8bc095efccdc15688708623367e358"
+dependencies = [
+ "proc-macro2",
+ "quote",
+ "syn 2.0.110",
+]
+
 [[package]]
 name = "windows-link"
 version = "0.2.1"
@@ -6775,6 +6810,24 @@ dependencies = [
  "windows-targets 0.52.6",
 ]
 
+[[package]]
+name = "windows-result"
+version = "0.4.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "7781fa89eaf60850ac3d2da7af8e5242a5ea78d1a11c49bf2910bb5a73853eb5"
+dependencies = [
+ "windows-link",
+]
+
+[[package]]
+name = "windows-strings"
+version = "0.5.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "7837d08f69c77cf6b07689544538e017c1bfcf57e34b4c0ff58e6c2cd3b37091"
+dependencies = [
+ "windows-link",
+]
+
 [[package]]
 name = "windows-sys"
 version = "0.48.0"
```

### cuda/ntt/sppark.cuh
```diff
@@ -29,7 +29,7 @@ extern "C" rustCudaError_t sppark_init(const cudaStream_t stream) {
     uint32_t lg_domain_size = 1;
     uint32_t domain_size = 1U << lg_domain_size;
 
-    std::vector<fr_t> inout{domain_size};
+    std::vector<fr_t> inout(domain_size);
     inout[0] = fr_t(1);
     inout[1] = fr_t(1);
     try {
```
