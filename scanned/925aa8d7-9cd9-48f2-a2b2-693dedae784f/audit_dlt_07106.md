# [?] Update cargo lockfile to fix RUSTSEC-2022-0025, RUSTSEC-2022-0026 and RUSTSEC-2022-0027  (#3278)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2022-06-18
Source: https://github.com/sigp/lighthouse/commit/21b3425a12e12032339d24c731dd20bef56bd99d
Type: security-commit

## Details
Update cargo lockfile to fix RUSTSEC-2022-0025, RUSTSEC-2022-0026 and RUSTSEC-2022-0027  (#3278)

## Issue Addressed

Fixes [RUSTSEC-2022-0025](https://rustsec.org/advisories/RUSTSEC-2022-0025), [RUSTSEC-2022-0026](https://rustsec.org/advisories/RUSTSEC-2022-0026) and [RUSTSEC-2022-0027](https://rustsec.org/advisories/RUSTSEC-2022-0027) raised in [this test run](https://github.com/sigp/lighthouse/runs/6943343852?check_suite_focus=true)

## Proposed Changes
a `cargo update` was enough

## Additional Info

## Patch
### Cargo.lock
```diff
@@ -111,7 +111,7 @@ version = "0.7.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "fcb51a0695d8f838b1ee009b3fbf66bda078cd64590202a864a8f3e8c4315c47"
 dependencies = [
- "getrandom 0.2.6",
+ "getrandom 0.2.7",
  "once_cell",
  "version_check",
 ]
@@ -141,15 +141,15 @@ dependencies = [
 
 [[package]]
 name = "anyhow"
-version = "1.0.56"
+version = "1.0.57"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "4361135be9122e0870de935d7c439aef945b9f9ddd4199a553b5270b49c82a27"
+checksum = "08f9b8508dccb7687a1d6c4ce66b2b0ecef467c94667de27d8d7fe1f8d2a9cdc"
 
 [[package]]
 name = "arbitrary"
-version = "1.1.0"
+version = "1.1.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c38b6b6b79f671c25e1a3e785b7b82d7562ffc9cd3efdc98627e5668a2472490"
+checksum = "25e0a02cf12f1b1f48b14cb7f8217b876d09992b39c816ffb3b1ba64dd979a87"
 dependencies = [
  "derive_arbitrary",
 ]
@@ -180,9 +180,9 @@ checksum = "e22d1f4b888c298a027c99dc9048015fac177587de20fc30232a057dfbe24a21"
 
 [[package]]
 name = "async-trait"
-version = "0.1.53"
+version = "0.1.56"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "ed6aa3524a2dfcf9fe180c51eae2b58738348d819517ceadf95789c51fff7600"
+checksum = "96cf8829f67d2eab0b2dfa42c5d0ef737e0724e4a82b01b3e292456202b19716"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -199,7 +199,7 @@ dependencies = [
  "futures-sink",
  "futures-util",
  "memchr",
- "pin-project-lite 0.2.8",
+ "pin-project-lite 0.2.9",
 ]
 
 [[package]]
@@ -241,9 +241,9 @@ checksum = "d468802bab17cbc0cc575e9b053f41e72aa36bfa6b7f55e3529ffa43161b97fa"
 
 [[package]]
 name = "backtrace"
-version = "0.3.64"
+version = "0.3.65"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5e121dee8023ce33ab248d9ce1493df03c3b38a659b240096fcbd7048ff9c31f"
+checksum = "11a17d453482a265fd5f8479f2a3f405566e6ca627837aaddb85af8b1ab8ef61"
 dependencies = [
  "addr2line",
  "cc",
@@ -301,7 +301,7 @@ dependencies = [
  "maplit",
  "merkle_proof",
  "operation_pool",
- "parking_lot 0.12.0",
+ "parking_lot 0.12.1",
  "proto_array",
  "rand 0.8.5",
  "rayon",
@@ -472,13 +472,14 @@ dependencies = [
 
 [[package]]
 name = "blst"
-version = "0.3.6"
+version = "0.3.9"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1f073f59a150a1dca74aab43d794ae5a7578d52bb1e73121e559f3ee3e6a837e"
+checksum = "c521c26a784d5c4bcd98d483a7d3518376e9ff1efbcfa9e2d456ab8183752303"
 dependencies = [
  "cc",
  "glob",
  "threadpool",
+ "which",
  "zeroize",
 ]
 
@@ -538,9 +539,9 @@ dependencies = [
 
 [[package]]
 name = "bumpalo"
-version = "3.9.1"
+version = "3.10.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a4a45a46ab1f2412e53d3a0ade76ffad2025804294569aae387231a0cd6e0899"
+checksum = "37ccbd214614c6783386c1af30caf03192f17891059cecc394b4fb119e363de3"
 
 [[package]]
 name = "byte-slice-cast"
@@ -593,7 +594,7 @@ dependencies = [
  "eth2_ssz_derive",
  "eth2_ssz_types",
  "ethereum-types 0.12.1",
- "quickcheck 0.9.2",
+ "quickcheck",
  "quickcheck_macros",
  "smallvec",
  "tree_hash",
@@ -663,7 +664,7 @@ dependencies = [
  "libc",
  "num-integer",
  "num-traits",
- "time 0.1.43",
+ "time 0.1.44",
  "winapi",
 ]
 
@@ -678,9 +679,9 @@ dependencies = [
 
 [[package]]
 name = "clang-sys"
-version = "1.3.1"
+version = "1.3.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "4cc00842eed744b858222c4c9faf7243aafc6d33f92f96935263ef4d8a41ce21"
+checksum = "5a050e2153c5be08febd6734e29298e844fdb0fa21aeddd63b4eb7baa106c69b"
 dependencies = [
  "glob",
  "libc",
@@ -739,7 +740,7 @@ dependencies = [
  "lighthouse_network",
  "monitoring_api",
  "network",
- "parking_lot 0.12.0",
+ "parking_lot 0.12.1",
  "sensitive_url",
  "serde",
  "serde_derive",
@@ -889,9 +890,9 @@ dependencies = [
 
 [[package]]
 name = "crossbeam-channel"
-version = "0.5.4"
+version = "0.5.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5aaa7bd5fb665c6864b5f963dd9097905c54125909c7aa94c9e18507cdbe6c53"
+checksum = "4c02a4d71819009c192cf4872265391563fd6a84c81ff2c0f2a7026ca4c1d85c"
 dependencies = [
  "cfg-if",
  "crossbeam-utils",
@@ -910,26 +911,26 @@ dependencies = [
 
 [[package]]
 name = "crossbeam-epoch"
-version = "0.9.8"
+version = "0.9.9"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1145cf131a2c6ba0615079ab6a638f7e1973ac9c2634fcbeaaad6114246efe8c"
+checksum = "07db9d94cbd326813772c968ccd25999e5f8ae22f4f8d1b11effa37ef6ce281d"
 dependencies = [
  "autocfg 1.1.0",
  "cfg-if",
  "crossbeam-utils",
- "lazy_static",
  "memoffset",
+ "once_cell",
  "scopeguard",
 ]
 
 [[package]]
 name = "crossbeam-utils"
-version = "0.8.8"
+version = "0.8.9"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0bf124c720b7686e3c2663cf54062ab0f68a88af2fb6a030e87e30bf721fcb38"
+checksum = "8ff1f980957787286a554052d03c7aee98d99cc32e09f6d45f0a814133c87978"
 dependencies = [
  "cfg-if",
- "lazy_static",
+ "once_cell",
 ]
 
 [[package]]
@@ -1013,11 +1014,11 @@ dependencies = [
 
 [[package]]
 name = "ctrlc"
-version = "3.2.1"
+version = "3.2.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a19c6cedffdc8c03a3346d723eb20bd85a13362bb96dc2ac000842c6381ec7bf"
+checksum = "b37feaa84e6861e00a1f5e5aa8da3ee56d605c9992d33e082786754828e20865"
 dependencies = [
- "nix",
+ "nix 0.24.1",
  "winapi",
 ]
 
@@ -1049,19 +1050,19 @@ dependencies = [
 
 [[package]]
 name = "darling"
-version = "0.13.2"
+version = "0.13.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "4e92cb285610dd935f60ee8b4d62dd1988bd12b7ea50579bd6a138201525318e"
+checksum = "a01d95850c592940db9b8194bc39f4bc0e89dee5c4265e4b1807c34a9aba453c"
 dependencies = [
  "darling_core",
  "darling_macro",
 ]
 
 [[package]]
 name = "darling_core"
-version = "0.13.2"
+version = "0.13.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5c29e95ab498b18131ea460b2c0baa18cbf041231d122b0b7bfebef8c8e88989"
+checksum = "859d65a907b6852c9361e3185c862aae7fafd2887876799fa55f5f99dc40d610"
 dependencies = [
  "fnv",
  "ident_case",
@@ -1073,9 +1074,9 @@ dependencies = [
 
 [[package]]
 name = "darling_macro"
-version = "0.13.2"
+version = "0.13.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b21dd6b221dd547528bd6fb15f1a3b7ab03b9a06f76bff288a8c629bcfbe7f0e"
+checksum = "9c972679f83bdf9c42bd905396b6c3588a843a17f0f16dfcfa3e2c5d57441835"
 dependencies = [
  "darling_core",
  "quote",
@@ -1178,9 +1179,9 @@ dependencies = [
 
 [[package]]
 name = "derive_arbitrary"
-version = "1.1.0"
+version = "1.1.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "98e23c06c035dac87bd802d98f368df73a7f2cb05a66ffbd1f377e821fac4af9"
+checksum = "8728db27dd9033a7456655aaeb35fde74425d0f130b4cb18a19171ef38a1b454"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -1296,7 +1297,7 @@ dependencies = [
  "smallvec",
  "tokio",
  "tokio-stream",
- "tokio-util 0.6.9",
+ "tokio-util 0.6.10",
  "tracing",
  "tracing-subscriber",
  "uint",
@@ -1335,9 +1336,9 @@ dependencies = [
 
 [[package]]
 name = "ed25519"
-version = "1.4.1"
+version = "1.5.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "3d5c4b5e5959dc2c2b89918d8e2cc40fcdd623cef026ed09d2f0ee05199dc8e4"
+checksum = "1e9c280362032ea4203659fc489832d0204ef09f247a0506f170dafcac08c369"
 dependencies = [
  "signature",
 ]
@@ -1417,7 +1418,7 @@ dependencies = [
  "base16ct",
  "crypto-bigint",
  "der 0.5.1",
- "ff 0.11.0",
+ "ff 0.11.1",
  "generic-array",
  "group 0.11.0",
  "rand_core 0.6.3",
@@ -1428,9 +1429,9 @@ dependencies = [
 
 [[package]]
 name = "encoding_rs"
-version = "0.8.30"
+version = "0.8.31"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7896dc8abb250ffdda33912550faa54c88ec8b998dec0b2c55ab224921ce11df"
+checksum = "9852635589dc9f9ea1b6fe9f05b50ef208c85c834a562f0c6abb1c475736ec2b"
 dependencies = [
  "cfg-if",
 ]
@@ -1535,7 +1536,7 @@ dependencies = [
  "lazy_static",
  "lighthouse_metrics",
  "merkle_proof",
- "parking_lot 0.12.0",
+ "parking_lot 0.12.1",
  "reqwest",
  "sensitive_url",
  "serde",
@@ -1762,9 +1763,9 @@ dependencies = [
 
 [[package]]
 name = "ethabi"
-version = "17.0.0"
+version = "17.1.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b69517146dfab88e9238c00c724fd8e277951c3cc6f22b016d72f422a832213e"
+checksum = "f186de076b3e77b8e6d73c99d1b52edc2a229e604f4b5eb6992c06c11d79d537"
 dependencies = [
  "ethereum-types 0.13.1",
  "hex",
@@ -1839,7 +1840,7 @@ dependencies = [
  "arrayvec",
  "bytes",
  "elliptic-curve 0.11.12",
- "ethabi 17.0.0",
+ "ethabi 17.1.0",
  "generic-array",
  "hex",
  "k256 0.10.4",
@@ -1887,7 +1888,7 @@ dependencies = [
  "lazy_static",
  "lighthouse_metrics",
  "lru",
- "parking_lot 0.12.0",
+ "parking_lot 0.12.1",
  "rand 0.8.5",
  "reqwest",
  "sensitive_url",
@@ -1955,9 +1956,9 @@ dependencies = [
 
 [[package]]
 name = "ff"
-version = "0.11.0"
+version = "0.11.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b2958d04124b9f27f175eaeb9a9f383d026098aa837eadd8ba22c11f13a05b9e"
+checksum = "131655483be284720a17d74ff97592b8e76576dc25563148601df2d7c9080924"
 dependencies = [
  "rand_core 0.6.3",
  "subtle",
@@ -2007,13 +2008,11 @@ checksum = "279fb028e20b3c4c320317955b77c5e0c9701f05a1d309905d6fc702cdc5053e"
 
 [[package]]
 name = "flate2"
-version = "1.0.22"
+version = "1.0.24"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1e6988e897c1c9c485f43b47a529cef42fde0547f9d8d41a7062518f1d8fc53f"
+checksum = "f82b0f4c27ad9f8bfd1f3208d882da2b09c301bc1c828fd3a00d0216d2fbbff6"
 dependencies = [
- "cfg-if",
  "crc32fast",
- "libc",
  "libz-sys",
  "miniz_oxide",
 ]
@@ -2150,7 +2149,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "e01fe9932a224b72b45336d96040aa86386d674a31d0af27d800ea7bc8ca97fe"
 dependencies = [
  "futures-io",
- "rustls 0.20.4",
+ "rustls 0.20.6",
  "webpki 0.22.0",
 ]
 
@@ -2185,7 +2184,7 @@ dependencies = [
  "futures-sink",
  "futures-task",
  "memchr",
- "pin-project-lite 0.2.8",
+ "pin-project-lite 0.2.9",
  "pin-utils",
  "slab",
 ]
@@ -2236,13 +2235,13 @@ dependencies = [
 
 [[package]]
 name = "getrandom"
-version = "0.2.6"
+version = "0.2.7"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9be70c98951c83b8d2f8f60d7065fa6d5146873094452a1008da8c2f1e4205ad"
+checksum = "4eb1a864a501629691edf6c15a593b7a51eebaa1e8468e9ddc623de7c9b58ec6"
 dependencies = [
  "cfg-if",
  "libc",
- "wasi 0.10.2+wasi-snapshot-preview1",
+ "wasi 0.11.0+wasi-snapshot-preview1",
 ]
 
 [[package]]
@@ -2306,7 +2305,7 @@ version = "0.11.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "bc5ac374b108929de78460075f3dc439fa66df9d8fc77e8f12caa5165fcf0c89"
 dependencies = [
- "ff 0.11.0",
+ "ff 0.11.1",
  "rand_core 0.6.3",
  "subtle",
 ]
@@ -2326,7 +2325,7 @@ dependencies = [
  "indexmap",
  "slab",
  "tokio",
- "tokio-util 0.7.1",
+ "tokio-util 0.7.3",
  "tracing",
 ]
 
@@ -2345,13 +2344,19 @@ dependencies = [
  "ahash",
 ]
 
+[[package]]
+name = "hashbrown"
+version = "0.12.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "db0d4cf898abf0081f964436dc980e96670a0f36863e4b83aaacdb65c9d7ccc3"
+
 [[package]]
 name = "hashlink"
 version = "0.7.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "7249a3129cbc1ffccd74857f81464a323a152173cdb134e0fd81bc803b29facf"
 dependencies = [
- "hashbrown",
+ "hashbrown 0.11.2",
 ]
 
 [[package]]
@@ -2360,7 +2365,7 @@ version = "0.2.0"
 dependencies = [
  "futures",
  "tokio",
- "tokio-util 0.6.9",
+ "tokio-util 0.6.10",
 ]
 
 [[package]]
@@ -2478,24 +2483,24 @@ dependencies = [
 
 [[package]]
 name = "http"
-version = "0.2.6"
+version = "0.2.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "31f4c6746584866f0feabcc69893c5b51beef3831656a968ed7ae254cdc4fd03"
+checksum = "75f43d41e26995c17e71ee126451dd3941010b0514a81a9d11f3b341debc2399"
 dependencies = [
  "bytes",
  "fnv",
- "itoa 1.0.1",
+ "itoa 1.0.2",
 ]
 
 [[package]]
 name = "http-body"
-version = "0.4.4"
+version = "0.4.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1ff4f84919677303da5f147645dbea6b1881f368d03ac84e1dc09031ebd7b2c6"
+checksum = "d5f38f16d184e36f2408a55281cd658ecbd3ca05cce6d6510a176eca393e26d1"
 dependencies = [
  "bytes",
  "http",
- "pin-project-lite 0.2.8",
+ "pin-project-lite 0.2.9",
 ]
 
 [[package]]
@@ -2517,7 +2522,7 @@ dependencies = [
  "lighthouse_version",
  "logging",
  "network",
- "parking_lot 0.12.0",
+ "parking_lot 0.12.1",
  "safe_arith",
  "sensitive_url",
  "serde",
@@ -2557,9 +2562,9 @@ dependencies = [
 
 [[package]]
 name = "httparse"
-version = "1.6.0"
+version = "1.7.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9100414882e15fb7feccb4897e5f0ff0ff1ca7d1a86a23208ada4d7a18e6c6c4"
+checksum = "496ce29bb5a52785b44e0f7ca2847ae0bb839c9bd28f69acac9b99d461c0c04c"
 
 [[package]]
 name = "httpdate"
@@ -2575,9 +2580,9 @@ checksum = "9a3a5bfb195931eeb336b2a7b4d761daec841b97f947d34394601737a7bba5e4"
 
 [[package]]
 name = "hyper"
-version = "0.14.18"
+version = "0.14.19"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b26ae0a80afebe130861d90abf98e3814a4f28a4c6ffeb5ab8ebb2be311e0ef2"
+checksum = "42dc3c131584288d375f2d07f822b0cb012d8c6fb899a5b9fdb3cb7eb9b6004f"
 dependencies = [
  "bytes",
  "futures-channel",
@@ -2588,8 +2593,8 @@ dependencies = [
  "http-body",
  "httparse",
  "httpdate",
- "itoa 1.0.1",
- "pin-project-lite 0.2.8",
+ "itoa 1.0.2",
+ "pin-project-lite 0.2.9",
  "socket2",
  "tokio",
  "tower-service",
@@ -2686,7 +2691,7 @@ version = "0.6.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "ba6a270039626615617f3f36d15fc827041df3b78c439da2cadfa47455a77f2f"
 dependencies = [
- "parity-scale-codec 3.1.2",
+ "parity-scale-codec 3.1.5",
 ]
 
 [[package]]
@@ -2720,12 +2725,12 @@ dependencies = [
 
 [[package]]
 name = "indexmap"
-version = "1.8.1"
+version = "1.9.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0f647032dfaa1f8b6dc29bd3edb7bbef4861b8b8007ebb118d6db284fd59f6ee"
+checksum = "6c6392766afd7964e2531940894cffe4bd8d7d17dbc3c1c4857040fd4b33bdb3"
 dependencies = [
  "autocfg 1.1.0",
- "hashbrown",
+ "hashbrown 0.12.1",
 ]
 
 [[package]]
@@ -2769,9 +2774,9 @@ dependencies = [
 
 [[package]]
 name = "ipnet"
-version = "2.4.0"
+version = "2.5.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "35e70ee094dc02fd9c13fdad4940090f22dbd6ac7c9e7094a46cf0232a50bc7c"
+checksum = "879d54834c8c76457ef4293a689b2a8c59b076067ad77b15efafbb05f92a592b"
 
 [[package]]
 name = "itertools"
@@ -2790,15 +2795,15 @@ checksum = "b71991ff56294aa922b450139ee08b3bfc70982c6b2c7562771375cf73542dd4"
 
 [[package]]
 name = "itoa"
-version = "1.0.1"
+version = "1.0.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1aab8fc367588b89dcee83ab0fd66b72b50b72fa1904d7095045ace2b0c81c35"
+checksum = "112c678d4050afce233f4f2852bb2eb519230b3cf12f33585275537d7e41578d"
 
 [[package]]
 name = "js-sys"
-version = "0.3.56"
+version = "0.3.58"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a38fc24e30fd564ce974c02bf1d337caddff65be6cc4735a1f7eab22a7440f04"
+checksum = "c3fac17f7123a73ca62df411b1bf727ccc805daa070338fda671c86dac1bdc27"
 dependencies = [
  "wasm-bindgen",
 ]
@@ -2820,9 +2825,9 @@ dependencies = [
 
 [[package]]
 name = "jsonwebtoken"
-version = "8.0.1"
+version = "8.1.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "012bb02250fdd38faa5feee63235f7a459974440b9b57593822414c31f92839e"
+checksum = "1aa4b4af834c6cfd35d8763d359661b90f2e45d8f750a0849156c7f4671af09c"
 dependencies = [
  "base64",
  "pem",
@@ -2859,9 +2864,9 @@ dependencies = [
 
 [[package]]
 name = "keccak"
-version = "0.1.0"
+version = "0.1.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "67c21572b4949434e4fc1e1978b99c5f77064153c59d998bf13ecd96fb5ecba7"
+checksum = "f9b7d56ba4a8344d6be9729995e6b06f928af29998cdf79fe390cbf6b1fee838"
 
 [[package]]
 name = "lazy_static"
@@ -2936,9 +2941,9 @@ dependencies = [
 
 [[package]]
 name = "libc"
-version = "0.2.121"
+version = "0.2.126"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "efaa7b300f3b5fe8eb6bf21ce3895e1751d9665086af2d64b42f19701015ff4f"
+checksum = "349d5a591cd28b49e1d1037471617a32ddcda5731b99419008085f72d5a53836"
 
 [[package]]
 name = "libflate"
@@ -2988,7 +2993,7 @@ dependencies = [
  "indexmap",
  "libc",
  "mdbx-sys",
- "parking_lot 0.12.0",
+ "parking_lot 0.12.1",
  "thiserror",
 ]
 
@@ -3001,7 +3006,7 @@ dependencies = [
  "bytes",
  "futures",
  "futures-timer",
- "getrandom 0.2.6",
+ "getrandom 0.2.7",
  "instant",
  "lazy_static",
  "libp2p-core 0.33.0",
@@ -3018,7 +3023,7 @@ dependencies = [
  "libp2p-websocket",
  "libp2p-yamux",
  "multiaddr 0.14.0",
- "parking_lot 0.12.0",
+ "parking_lot 0.12.1",
  "pin-project 1.0.10",
  "rand 0.7.3",
  "smallvec",
@@ -3079,7 +3084,7 @@ dependencies = [
  "multiaddr 0.14.0",
  "multihash 0.16.2",
  "multistream-select 0.11.0",
- "parking_lot 0.12.0",
+ "parking_lot 0.12.1",
  "pin-project 1.0.10",
  "prost 0.10.4",
  "prost-build 0.10.4",
@@ -3103,16 +3108,16 @@ dependencies = [
  "futures",
  "libp2p-core 0.33.0",
  "log",
- "parking_lot 0.12.0",
+ "parking_lot 0.12.1",
  "smallvec",
  "trust-dns-resolver",
 ]
 
 [[package]]
 name = "libp2p-gossipsub"
-version = "0.38.0"
+version = "0.38.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c9be947d8cea8e6b469201314619395826896d2c051053c3723910ba98e68e04"
+checksum = "43e064ba4d7832e01c738626c6b274ae100baba05f5ffcc7b265c2a3ed398108"
 dependencies = [
  "asynchronous-codec",
  "base64",
@@ -3182,7 +3187,7 @@ dependencies = [
  "libp2p-core 0.33.0",
  "log",
  "nohash-hasher",
- "parking_lot 0.12.0",
+ "parking_lot 0.12.1",
  "rand 0.7.3",
  "smallvec",
  "unsigned-varint 0.7.1",
@@ -3249,9 +3254,9 @@ dependencies = [
 
 [[package]]
 name = "libp2p-swarm-derive"
-version = "0.27.1"
+version = "0.27.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "daf2fe8c80b43561355f4d51875273b5b6dfbac37952e8f64b1270769305c9d7"
+checksum = "4f693c8c68213034d472cbb93a379c63f4f307d97c06f1c41e4985de481687a5"
 dependencies = [
  "quote",
  "syn",
@@ -3285,7 +3290,7 @@ dependencies = [
  "futures-rustls",
  "libp2p-core 0.33.0",
  "log",
- "parking_lot 0.12.0",
+ "parking_lot 0.12.1",
  "quicksink",
  "rw-stream-sink 0.3.0",
  "soketto",
@@ -3301,7 +3306,7 @@ checksum = "8fe653639ad74877c759720febb0cbcbf4caa221adde4eed2d3126ce5c6f381f"
 dependencies = [
  "futures",
  "libp2p-core 0.33.0",
- "parking_lot 0.12.0",
+ "parking_lot 0.12.1",
  "thiserror",
  "yamux",
 ]
@@ -3367,9 +3372,9 @@ dependencies = [
 
 [[package]]
 name = "libz-sys"
-version = "1.1.5"
+version = "1.1.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6f35facd4a5673cb5a48822be2be1d4236c1c99cb4113cab7061ac720d5bf859"
+checksum = "9702761c3935f8cc2f101793272e202c72b99da8f4224a19ddcf1279a6450bbf"
 dependencies = [
  "cc",
  "pkg-config",
@@ -3443,7 +3448,7 @@ dependencies = [
  "lighthouse_metrics",
  "lighthouse_version",
  "lru",
- "parking_lot 0.12.0",
+ "parking_lot 0.12.1",
  "prometheus-client",
  "rand 0.8.5",
  "regex",
@@ -3462,7 +3467,7 @@ dependencies = [
  "tiny-keccak",
  "tokio",
  "tokio-io-timeout",
- "tokio-util 0.6.9",
+ "tokio-util 0.6.10",
  "types",
  "unsigned-varint 0.6.0",
  "unused_port",
@@ -3504,9 +3509,9 @@ dependencies = [
 
 [[package]]
 name = "log"
-version = "0.4.16"
+version = "0.4.17"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6389c490849ff5bc16be905ae24bc913a9c8892e19b2341dbc175e14c341c2b8"
+checksum = "abb12e687cfb44aa40f41fc3978ef76448f9b6038cad6aef4259d3c095a2382e"
 dependencies = [
  "cfg-if",
 ]
@@ -3524,11 +3529,11 @@ dependencies = [
 
 [[package]]
 name = "lru"
-version = "0.7.5"
+version = "0.7.7"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "32613e41de4c47ab04970c348ca7ae7382cf116625755af070b008a15516a889"
+checksum = "c84e6fe5655adc6ce00787cf7dcaf8dc4f998a0565d23eafc207a8b08ca3349a"
 dependencies = [
- "hashbrown",
+ "hashbrown 0.11.2",
 ]
 
 [[package]]
@@ -3563,7 +3568,7 @@ dependencies = [
  "lazy_static",
  "libc",
  "lighthouse_metrics",
- "parking_lot 0.12.0",
+ "parking_lot 0.12.1",
 ]
 
 [[package]]
@@ -3607,9 +3612,9 @@ dependencies = [
 
 [[package]]
 name = "memchr"
-version = "2.4.1"
+version = "2.5.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "308cc39be01b73d0d18f82a0e7b2a3df85245f84af96fdddc5d202d27e47b86a"
+checksum = "2dffe52ecf27772e601905b7522cb4ef790d2cc203488bbd0e2fe85fcb74566d"
 
 [[package]]
 name = "memoffset"
@@ -3627,7 +3632,7 @@ dependencies = [
  "eth2_hashing",
  "ethereum-types 0.12.1",
  "lazy_static",
- "quickcheck 0.9.2",
+ "quickcheck",
  "quickcheck_macros",
  "safe_arith",
 ]
@@ -3668,35 +3673,23 @@ checksum = "68354c5c6bd36d73ff3feceb05efa59b6acb7626617f4962be322a825e61f79a"
 
 [[package]]
 name = "miniz_oxide"
-version = "0.4.4"
+version = "0.5.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a92518e98c078586bc6c934028adcca4c92a53d6a958196de835170a01d84e4b"
+checksum = "6f5c75688da582b8ffc1f1799e9db273f32133c49e048f614d22ec3256773ccc"
 dependencies = [
  "adler",
- "autocfg 1.1.0",
 ]
 
 [[package]]
 name = "mio"
-version = "0.8.2"
+version = "0.8.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "52da4364ffb0e4fe33a9841a98a3f3014fb964045ce4f7a45a398243c8d6b0c9"
+checksum = "713d550d9b44d89174e066b7a6217ae06234c10cb47819a88290d2b353c31799"
 dependencies = [
  "libc",
  "log",
- "miow",
- "ntapi",
  "wasi 0.11.0+wasi-snapshot-preview1",
- "winapi",
-]
-
-[[package]]
-name = "miow"
-version = "0.3.7"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b9f1c5b025cda876f66ef43a113f91ebc9f4ccef34843000e0adf6ebbab84e21"
-dependencies = [
- "winapi",
+ "windows-sys",
 ]
 
 [[package]]
@@ -3918,7 +3911,7 @@ dependencies = [
  "task_executor",
  "tokio",
  "tokio-stream",
- "tokio-util 0.6.9",
+ "tokio-util 0.6.10",
  "types",
 ]
 
@@ -3935,6 +3928,17 @@ dependencies = [
  "memoffset",
 ]
 
+[[package]]
+name = "nix"
+version = "0.24.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "8f17df307904acd05aa8e32e97bb20f2a0df1728bbc2d771ae8f9a90463441e9"
+dependencies = [
+ "bitflags",
+ "cfg-if",
+ "libc",
+]
+
 [[package]]
 name = "node_test_rig"
 version = "0.2.0"
@@ -3971,15 +3975,6 @@ dependencies = [
  "minimal-lexical",
 ]
 
-[[package]]
-name = "ntapi"
-version = "0.3.7"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c28774a7fd2fbb4f0babd8237ce554b73af68021b5f695a3cebd6c59bac0980f"
-dependencies = [
- "winapi",
-]
-
 [[package]]
 name = "num-bigint"
 version = "0.4.3"
@@ -4012,19 +4007,19 @@ dependencies = [
 
 [[package]]
 name = "num-integer"
-version = "0.1.44"
+version = "0.1.45"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d2cc698a63b549a70bc047073d2949cce27cd1c7b0a4a862d08a8031bc2801db"
+checksum = "225d3389fb3509a24c93f5c29eb6bde2586b98d9f016636dff58d7c6f7569cd9"
 dependencies = [
  "autocfg 1.1.0",
  "num-traits",
 ]
 
 [[package]]
 name = "num-iter"
-version = "0.1.42"
+version = "0.1.43"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b2021c8337a54d21aca0d59a92577a029af9431cb59b909b03252b9c164fad59"
+checksum = "7d03e6c028c5dc5cac6e2dec0efda81fc887605bb3d884578bb6d6bf7514e252"
 dependencies = [
  "autocfg 1.1.0",
  "num-integer",
@@ -4033,9 +4028,9 @@ dependencies = [
 
 [[package]]
 name = "num-traits"
-version = "0.2.14"
+version = "0.2.15"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9a64b1ec5cda2586e284722486d802acf1f7dbdc623e2bfc57e65ca1cd099290"
+checksum = "578ede34cf02f8924ab9447f50c28075b4d3e5b269972345e7e0372b38c6cdcd"
 dependencies = [
  "autocfg 1.1.0",
 ]
@@ -4052,27 +4047,27 @@ dependencies = [
 
 [[package]]
 name = "num_threads"
-version = "0.1.5"
+version = "0.1.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "aba1801fb138d8e85e11d0fc70baf4fe1cdfffda7c6cd34a854905df588e5ed0"
+checksum = "2819ce041d2ee131036f4fc9d6ae7ae125a3a40e97ba64d04fe799ad9dabbb44"
 dependencies = [
  "libc",
 ]
 
 [[package]]
 name = "object"
-version = "0.27.1"
+version = "0.28.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "67ac1d3f9a1d3616fd9a60c8d74296f22406a238b6a72f5cc1e6f314df4ffbf9"
+checksum = "e42c982f2d955fac81dd7e1d0e1426a7d702acd9c98d19ab01083a6a0328c424"
 dependencies = [
  "memchr",
 ]
 
 [[package]]
 name = "once_cell"
-version = "1.10.0"
+version = "1.12.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "87f3e037eac156d1775da914196f0f37741a274155e34a0b7e427c35d2a2ecb9"
+checksum = "7709cef83f0c1f58f666e746a08b21e0085f7440fa6a29cc194d68aac97a4225"
 
 [[package]]
 name = "oorandom"
@@ -4088,18 +4083,30 @@ checksum = "624a8340c38c1b80fd549087862da4ba43e08858af025b236e509b6649fc13d5"
 
 [[package]]
 name = "openssl"
-version = "0.10.38"
+version = "0.10.40"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0c7ae222234c30df141154f159066c5093ff73b63204dcda7121eb082fc56a95"
+checksum = "fb81a6430ac911acb25fe5ac8f1d2af1b4ea8a4fdfda0f1ee4292af2e2d8eb0e"
 dependencies = [
  "bitflags",
  "cfg-if",
  "foreign-types",
  "libc",
  "once_cell",
+ "openssl-macros",
  "openssl-sys",
 ]
 
+[[package]]
+name = "openssl-macros"
+version = "0.1.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "b501e44f11665960c7e7fcf062c7d96a14ade4aa98116c004b2e37b5be7d736c"
+dependencies = [
+ "proc-macro2",
+ "quote",
+ "syn",
+]
+
 [[package]]
 name = "openssl-probe"
 version = "0.1.5"
@@ -4108,18 +4115,18 @@ checksum = "ff011a302c396a5197692431fc1948019154afc178baf7d8e37367442a4601cf"
 
 [[package]]
 name = "openssl-src"
-version = "111.18.0+1.1.1n"
+version = "111.20.0+1.1.1o"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7897a926e1e8d00219127dc020130eca4292e5ca666dd592480d72c3eca2ff6c"
+checksum = "92892c4f87d56e376e469ace79f1128fdaded07646ddf73aa0be4706ff712dec"
 dependencies = [
  "cc",
 ]
 
 [[package]]
 name = "openssl-sys"
-version = "0.9.72"
+version = "0.9.74"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7e46109c383602735fa0a2e48dd2b7c892b048e1bf69e5c3b1d804b7d9c203cb"
+checksum = "835363342df5fba8354c5b453325b110ffd54044e588c539cf2f20a8014e4cb1"
 dependencies = [
  "autocfg 1.1.0",
  "cc",
@@ -4140,7 +4147,7 @@ dependencies = [
  "itertools",
  "lazy_static",
  "lighthouse_metrics",
- "parking_lot 0.12.0",
+ "parking_lot 0.12.1",
  "rayon",
  "serde",
  "serde_derive",
@@ -4174,15 +4181,15 @@ dependencies = [
 
 [[package]]
 name = "parity-scale-codec"
-version = "3.1.2"
+version = "3.1.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e8b44461635bbb1a0300f100a841e571e7d919c81c73075ef5d152ffdb521066"
+checksum = "9182e4a71cae089267ab03e67c99368db7cd877baf50f931e5d6d4b71e195ac0"
 dependencies = [
  "arrayvec",
  "bitvec 1.0.0",
  "byte-slice-cast",
  "impl-trait-for-tuples",
- "parity-scale-codec-derive 3.1.2",
+ "parity-scale-codec-derive 3.1.3",
  "serde",
 ]
 
@@ -4200,9 +4207,9 @@ dependencies = [
 
 [[package]]
 name = "parity-scale-codec-derive"
-version = "3.1.2"
+version = "3.1.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c45ed1f39709f5a89338fab50e59816b2e8815f5bb58276e7ddf9afd495f73f8"
+checksum = "9299338969a3d2f491d65f140b00ddec470858402f888af98e8642fb5e8965cd"
 dependencies = [
  "proc-macro-crate",
  "proc-macro2",
@@ -4223,12 +4230,12 @@ dependencies = [
 
 [[package]]
 name = "parking_lot"
-version = "0.12.0"
+version = "0.12.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "87f5ec2493a61ac0506c0f4199f99070cbe83857b0337006a30f3e6719b8ef58"
+checksum = "3742b2c103b9f06bc9fff0a37ff4912935851bee6d36f3c02bcc755bcfec228f"
 dependencies = [
  "lock_api",
- "parking_lot_core 0.9.2",
+ "parking_lot_core 0.9.3",
 ]
 
 [[package]]
@@ -4247,9 +4254,9 @@ dependencies = [
 
 [[package]]
 name = "parking_lot_core"
-version = "0.9.2"
+version = "0.9.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "995f667a6c822200b0433ac218e05582f0e2efa1b922a3fd2fbaadc5f87bab37"
+checksum = "09a279cbf25cb0757810394fbc1e359949b59e348145c643a939a525692e6929"
 dependencies = [
  "cfg-if",
  "libc",
@@ -4314,9 +4321,9 @@ dependencies = [
 
 [[package]]
 name = "petgraph"
-version = "0.6.0"
+version = "0.6.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "4a13a2fa9d0b63e5f22328828741e523766fff0ee9e779316902290dff3f824f"
+checksum = "e6d5014253a1331579ce62aa67443b4a658c5e7dd03d4bc6d302b94474888143"
 dependencies = [
  "fixedbitset",
  "indexmap",
@@ -4370,9 +4377,9 @@ checksum = "257b64915a082f7811703966789728173279bdebb956b143dbcd23f6f970a777"
 
 [[package]]
 name = "pin-project-lite"
-version = "0.2.8"
+version = "0.2.9"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e280fbe77cc62c91527259e9442153f4688736748d24660126286329742b4c6c"
+checksum = "e0a7ae3ac2f1173085d398531c705756c94a4c56843785df85a60c1a0afac116"
 
 [[package]]
 name = "pin-utils"
@@ -4538,11 +4545,11 @@ checksum = "dbf0c48bc1d91375ae5c3cd81e3722dff1abcf81a30960240640d223f59fe0e5"
 
 [[package]]
 name = "proc-macro2"
-version = "1.0.36"
+version = "1.0.39"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c7342d5883fbccae1cc37a2353b09c87c9b0f3afd73f5fb9bba687a1f733b029"
+checksum = "c54b25569025b7fc9651de43004ae593a75ad88543b17178aa5e1b9c4f15f56f"
 dependencies = [
- "unicode-xid",
+ "unicode-ident",
 ]
 
 [[package]]
@@ -4559,15 +4566,15 @@ dependencies = [
 
 [[package]]
 name = "prometheus"
-version = "0.13.0"
+version = "0.13.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b7f64969ffd5dd8f39bd57a68ac53c163a095ed9d0fb707146da1b27025a3504"
+checksum = "cface98dfa6d645ea4c789839f176e4b072265d085bfcc48eaa8d137f58d3c39"
 dependencies = [
  "cfg-if",
  "fnv",
  "lazy_static",
  "memchr",
- "parking_lot 0.11.2",
+ "parking_lot 0.12.1",
  "protobuf",
  "thiserror",
 ]
@@ -4579,7 +4586,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "ac1abe0255c04d15f571427a2d1e00099016506cf3297b53853acd2b7eb87825"
 dependencies = [
  "dtoa",
- "itoa 1.0.1",
+ "itoa 1.0.2",
  "owning_ref",
  "prometheus-client-derive-text-encode",
 ]
@@ -4745,7 +4752,7 @@ dependencies = [
  "derive_more",
  "glob",
  "mach",
- "nix",
+ "nix 0.23.1",
  "num_cpus",
  "once_cell",
  "platforms",
@@ -4771,15 +4778,6 @@ dependencies = [
  "rand_core 0.5.1",
 ]
 
-[[package]]
-name = "quickcheck"
-version = "1.0.3"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "588f6378e4dd99458b60ec275b4477add41ce4fa9f64dcba6f15adccb19b50d6"
-dependencies = [
- "rand 0.8.5",
-]
-
 [[package]]
 name = "quickcheck_macros"
 version = "0.9.1"
@@ -4804,9 +4802,9 @@ dependencies = [
 
 [[package]]
 name = "quote"
-version = "1.0.17"
+version = "1.0.18"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "632d02bff7f874a36f33ea8bb416cd484b90cc66c1194b1a1110d067a7013f58"
+checksum = "a1feb54ed693b93a84e14094943b84b7c4eae204c512b7ccb95ab0c66d278ad1"
 dependencies = [
  "proc-macro2",
 ]
@@ -4903,7 +4901,7 @@ version = "0.6.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "d34f1408f55294453790c48b2f1ebbb1c5b4b7563eb1f418bcfcfdbb06ebb4e7"
 dependencies = [
- "getrandom 0.2.6",
+ "getrandom 0.2.7",
 ]
 
 [[package]]
@@ -4926,9 +4924,9 @@ dependencies = [
 
 [[package]]
 name = "rayon"
-version = "1.5.1"
+version = "1.5.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c06aca804d41dbc8ba42dfd964f0d01334eceb64314b9ecf7c5fad5188a06d90"
+checksum = "bd99e5772ead8baa5215278c9b15bf92087709e9c1b2d1f97cdb5a183c933a7d"
 dependencies = [
  "autocfg 1.1.0",
  "crossbeam-deque",
@@ -4938,14 +4936,13 @@ dependencies = [
 
 [[package]]
 name = "rayon-core"
-version = "1.9.1"
+version = "1.9.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d78120e2c850279833f1dd3582f730c4ab53ed95aeaaaa862a2a5c71b1656d8e"
+checksum = "258bcdb5ac6dad48491bb2992db6b7cf74878b0384908af124823d118c99683f"
 dependencies = [
  "crossbeam-channel",
  "crossbeam-deque",
  "crossbeam-utils",
- "lazy_static",
  "num_cpus",
 ]
 
@@ -4964,16 +4961,16 @@ version = "0.4.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "b033d837a7cf162d7993aded9304e30a83213c648b6e389db233191f891e5c2b"
 dependencies = [
- "getrandom 0.2.6",
+ "getrandom 0.2.7",
  "redox_syscall",
  "thiserror",
 ]
 
 [[package]]
 name = "regex"
-version = "1.5.5"
+version = "1.5.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1a11647b6b25ff05a515cb92c365cec08801e83423a235b51e231e1808747286"
+checksum = "d83f127d94bdbcda4c8cc2e50f6f84f4b611f69c902699ca385a39c3a75f9ff1"
 dependencies = [
  "aho-corasick",
  "memchr",
@@ -4991,9 +4988,9 @@ dependencies = [
 
 [[package]]
 name = "regex-syntax"
-version = "0.6.25"
+version = "0.6.26"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f497285884f3fcff424ffc933e56d7cbca511def0c9831a7f9b5f6153e3cc89b"
+checksum = "49b3de9ec5dc0a3417da371aab17d729997c15010e7fd24ff707773a33bddb64"
 
 [[package]]
 name = "remove_dir_all"
@@ -5006,9 +5003,9 @@ dependencies = [
 
 [[package]]
 name = "reqwest"
-version = "0.11.10"
+version = "0.11.11"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "46a1f7aa4f35e5e8b4160449f51afc758f0ce6454315a9fa7d0d113e958c41eb"
+checksum = "b75aa69a3f06bbcc66ede33af2af253c6f7a86b1ca0033f60c580a27074fbf92"
 dependencies = [
  "base64",
  "bytes",
@@ -5027,13 +5024,14 @@ dependencies = [
  "mime",
  "native-tls",
  "percent-encoding",
- "pin-project-lite 0.2.8",
+ "pin-project-lite 0.2.9",
  "serde",
  "serde_json",
  "serde_urlencoded",
  "tokio",
  "tokio-native-tls",
- "tokio-util 0.6.9",
+ "tokio-util 0.7.3",
+ "tower-service",
  "url",
  "wasm-bindgen",
  "wasm-bindgen-futures",
@@ -5171,7 +5169,7 @@ version = "0.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "bfa0f585226d2e68097d4f95d113b15b83a82e819ab25717ec0590d9584ef366"
 dependencies = [
- "semver 1.0.7",
+ "semver 1.0.10",
 ]
 
 [[package]]
@@ -5189,9 +5187,9 @@ dependencies = [
 
 [[package]]
 name = "rustls"
-version = "0.20.4"
+version = "0.20.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "4fbfeb8d0ddb84706bc597a5574ab8912817c52a397f819e5b614e2265206921"
+checksum = "5aab8ee6c7097ed6057f43c187a62418d0c05a4bd5f18b3571db50ee0f9ce033"
 dependencies = [
  "log",
  "ring",
@@ -5229,9 +5227,9 @@ dependencies = [
 
 [[package]]
 name = "ryu"
-version = "1.0.9"
+version = "1.0.10"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "73b4b750c782965c211b42f022f59af1fbceabdd026623714f104152f1ec149f"
+checksum = "f3f6f92acf49d1b98f7a81226834412ada05458b7364277387724a237f062695"
 
 [[package]]
 name = "safe_arith"
@@ -5263,21 +5261,21 @@ dependencies = [
 
 [[package]]
 name = "schannel"
-version = "0.1.19"
+version = "0.1.20"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8f05ba609c234e60bee0d547fe94a4c7e9da733d1c962cf6e59efa4cd9c8bc75"
+checksum = "88d6731146462ea25d9244b2ed5fd1d716d25c52e4d54aa4fb0f3c4e9854dbe2"
 dependencies = [
  "lazy_static",
- "winapi",
+ "windows-sys",
 ]
 
 [[package]]
 name = "scheduled-thread-pool"
-version = "0.2.5"
+version = "0.2.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "dc6f74fd1204073fa02d5d5d68bec8021be4c38690b61264b2fdb48083d0e7d7"
+checksum = "977a7519bff143a44f842fd07e80ad1329295bd71686457f18e496736f4bf9bf"
 dependencies = [
- "parking_lot 0.11.2",
+ "parking_lot 0.12.1",
 ]
 
 [[package]]
@@ -5398,9 +5396,9 @@ dependencies = [
 
 [[package]]
 name = "semver"
-version = "1.0.7"
+version = "1.0.10"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d65bd28f48be7196d222d95b9243287f48d27aca604e08497513019ff0502cc4"
+checksum = "a41d061efea015927ac527063765e73601444cdc344ba855bc7bd44578b25e1c"
 
 [[package]]
 name = "semver-parser"
@@ -5427,9 +5425,9 @@ dependencies = [
 
 [[package]]
 name = "serde"
-version = "1.0.136"
+version = "1.0.137"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "ce31e24b01e1e524df96f1c2fdd054405f8d7376249a5110886fb4b658484789"
+checksum = "61ea8d54c77f8315140a05f4c7237403bf38b72704d031543aa1d16abbf517d1"
 dependencies = [
  "serde_derive",
 ]
@@ -5456,9 +5454,9 @@ dependencies = [
 
 [[package]]
 name = "serde_derive"
-version = "1.0.136"
+version = "1.0.137"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "08597e7152fcd306f41838ed3e37be9eaeed2b61c42e2117266a554fab4662f9"
+checksum = "1f26faba0c3959972377d3b2d306ee9f71faee9714294e41bb777f83f88578be"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -5467,20 +5465,20 @@ dependencies = [
 
 [[package]]
 name = "serde_json"
-version = "1.0.79"
+version = "1.0.81"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8e8d9fa5c3b304765ce1fd9c4c8a3de2c8db365a5b91be52f186efc675681d95"
+checksum = "9b7ce2b32a1aed03c558dc61a5cd328f15aff2dbc17daad8fb8af04d2100e15c"
 dependencies = [
- "itoa 1.0.1",
+ "itoa 1.0.2",
  "ryu",
  "serde",
 ]
 
 [[package]]
 name = "serde_repr"
-version = "0.1.7"
+version = "0.1.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "98d0516900518c29efa217c298fa1f4e6c6ffc85ae29fd7f4ee48f176e1a9ed5"
+checksum = "a2ad84e47328a31223de7fed7a4f5087f2d6ddfe586cf3ca25b7a165bc0a5aed"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -5494,16 +5492,16 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "d3491c14715ca2294c4d6a88f15e84739788c1d030eed8c110436aafdaa2f3fd"
 dependencies = [
  "form_urlencoded",
- "itoa 1.0.1",
+ "itoa 1.0.2",
  "ryu",
  "serde",
 ]
 
 [[package]]
 name = "serde_yaml"
-version = "0.8.23"
+version = "0.8.24"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a4a521f2940385c165a24ee286aa8599633d162077a54bdcae2a6fd5a7bfa7a0"
+checksum = "707d15895415db6628332b737c838b88c598522e4dc70647e59b72312924aebc"
 dependencies = [
  "indexmap",
  "ryu",
@@ -5617,9 +5615,9 @@ dependencies = [
 
 [[package]]
 name = "simple_asn1"
-version = "0.6.1"
+version = "0.6.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "4a762b1c38b9b990c694b9c2f8abe3372ce6a9ceaae6bca39cfc46e054f45745"
+checksum = "adc4e5204eb1910f40f9cfa375f6f05b68c3abac4b6fd879c8ff5e7ae8a0a085"
 dependencies = [
  "num-bigint",
  "num-traits",
@@ -5637,7 +5635,7 @@ dependencies = [
  "eth1_test_rig",
  "futures",
  "node_test_rig",
- "parking_lot 0.12.0",
+ "parking_lot 0.12.1",
  "rayon",
  "sensitive_url",
  "tokio",
@@ -5666,7 +5664,7 @@ dependencies = [
  "logging",
  "lru",
  "maplit",
- "parking_lot 0.12.0",
+ "parking_lot 0.12.1",
  "rand 0.8.5",
  "rayon",
  "safe_arith",
@@ -5821,7 +5819,7 @@ version = "0.2.0"
 dependencies = [
  "lazy_static",
  "lighthouse_metrics",
- "parking_lot 0.12.0",
+ "parking_lot 0.12.1",
  "types",
 ]
 
@@ -5966,7 +5964,7 @@ dependencies = [
  "leveldb",
  "lighthouse_metrics",
  "lru",
- "parking_lot 0.12.0",
+ "parking_lot 0.12.1",
  "serde",
  "serde_derive",
  "slog",
@@ -5991,9 +5989,9 @@ checksum = "73473c0e59e6d5812c5dfe2a064a6444949f089e20eec9a2e5506596494e4623"
 
 [[package]]
 name = "strum"
-version = "0.24.0"
+version = "0.24.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e96acfc1b70604b8b2f1ffa4c57e59176c7dbb05d556c71ecd2f5498a1dee7f8"
+checksum = "063e6045c0e62079840579a7e47a355ae92f60eb74daaf156fb1e84ba164e63f"
 dependencies = [
  "strum_macros",
 ]
@@ -6042,13 +6040,13 @@ dependencies = [
 
 [[package]]
 name = "syn"
-version = "1.0.90"
+version = "1.0.96"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "704df27628939572cd88d33f171cd6f896f4eaca85252c6e0a72d8d8287ee86f"
+checksum = "0748dd251e24453cb8717f0354206b91557e4ec8703673a4b30208f2abaf1ebf"
 dependencies = [
  "proc-macro2",
  "quote",
- "unicode-xid",
+ "unicode-ident",
 ]
 
 [[package]]
@@ -6162,18 +6160,18 @@ dependencies = [
 
 [[package]]
 name = "thiserror"
-version = "1.0.30"
+version = "1.0.31"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "854babe52e4df1653706b98fcfc05843010039b406875930a70e4d9644e5c417"
+checksum = "bd829fe32373d27f76265620b5309d0340cb8550f523c1dda251d6298069069a"
 dependencies = [
  "thiserror-impl",
 ]
 
 [[package]]
 name = "thiserror-impl"
-version = "1.0.30"
+version = "1.0.31"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "aa32fd3f627f367fe16f893e2597ae3c05020f8bba2666a4e6ea73d377e5714b"
+checksum = "0396bc89e626244658bef819e22d0cc459e795a5ebe878e6ec336d1674a8d79a"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -6200,11 +6198,12 @@ dependencies = [
 
 [[package]]
 name = "time"
-version = "0.1.43"
+version = "0.1.44"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "ca8a50ef2360fbd1eeb0ecd46795a87a19024eb4b53c5dc916ca1fd95fe62438"
+checksum = "6db9e6914ab8b1ae1c260a4ae7a49b6c5611b40328a735b21862567685e73255"
 dependencies = [
  "libc",
+ "wasi 0.10.0+wasi-snapshot-preview1",
  "winapi",
 ]
 
@@ -6214,10 +6213,9 @@ version = "0.3.9"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "c2702e08a7a860f005826c6815dcac101b19b5eb330c27fe4a5928fec1d20ddd"
 dependencies = [
- "itoa 1.0.1",
+ "itoa 1.0.2",
  "libc",
  "num_threads",
- "quickcheck 1.0.3",
  "time-macros",
 ]
 
@@ -6278,9 +6276,9 @@ dependencies = [
 
 [[package]]
 name = "tinyvec"
-version = "1.5.1"
+version = "1.6.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "2c1c1d5a42b6245520c249549ec267180beaffcc0615401ac8e31853d4b6d8d2"
+checksum = "87cc5ceb3875bb20c2890005a4e226a4651264a5c75edb2421b52861a0a0cb50"
 dependencies = [
  "tinyvec_macros",
 ]
@@ -6293,18 +6291,18 @@ checksum = "cda74da7e1a664f795bb1f8a87ec406fb89a02522cf6e50620d016add6dbbf5c"
 
 [[package]]
 name = "tokio"
-version = "1.17.0"
+version = "1.19.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "2af73ac49756f3f7c01172e34a23e5d0216f6c32333757c2c61feb2bbff5a5ee"
+checksum = "c51a52ed6686dd62c320f9b89299e9dfb46f730c7a48e635c19f21d116cb1439"
 dependencies = [
  "bytes",
  "libc",
  "memchr",
  "mio",
  "num_cpus",
  "once_cell",
- "parking_lot 0.12.0",
- "pin-project-lite 0.2.8",
+ "parking_lot 0.12.1",
+ "pin-project-lite 0.2.9",
  "signal-hook-registry",
  "socket2",
  "tokio-macros",
@@ -6317,15 +6315,15 @@ version = "1.2.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "30b74022ada614a1b4834de765f9bb43877f910cc8ce4be40e89042c9223a8bf"
 dependencies = [
- "pin-project-lite 0.2.8",
+ "pin-project-lite 0.2.9",
  "tokio",
 ]
 
 [[package]]
 name = "tokio-macros"
-version = "1.7.0"
+version = "1.8.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b557f72f448c511a979e2564e55d74e6c4432fc96ff4f6241bc6bded342643b7"
+checksum = "9724f9a975fb987ef7a3cd9be0350edcbe130698af5b8f7a631e23d42d052484"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -6355,14 +6353,14 @@ dependencies = [
 
 [[package]]
 name = "tokio-stream"
-version = "0.1.8"
+version = "0.1.9"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "50145484efff8818b5ccd256697f36863f587da82cf8b409c53adf1e840798e3"
+checksum = "df54d54117d6fdc4e4fea40fe1e4e566b3505700e148a6827e59b34b0d2600d9"
 dependencies = [
  "futures-core",
- "pin-project-lite 0.2.8",
+ "pin-project-lite 0.2.9",
  "tokio",
- "tokio-util 0.6.9",
+ "tokio-util 0.7.3",
 ]
 
 [[package]]
@@ -6380,67 +6378,67 @@ dependencies = [
 
 [[package]]
 name = "tokio-util"
-version = "0.6.9"
+version = "0.6.10"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9e99e1983e5d376cd8eb4b66604d2e99e79f5bd988c3055891dcd8c9e2604cc0"
+checksum = "36943ee01a6d67977dd3f84a5a1d2efeb4ada3a1ae771cadfaa535d9d9fc6507"
 dependencies = [
  "bytes",
  "futures-core",
  "futures-io",
  "futures-sink",
  "log",
- "pin-project-lite 0.2.8",
+ "pin-project-lite 0.2.9",
  "slab",
  "tokio",
 ]
 
 [[package]]
 name = "tokio-util"
-version = "0.7.1"
+version = "0.7.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0edfdeb067411dba2044da6d1cb2df793dd35add7888d73c16e3381ded401764"
+checksum = "cc463cd8deddc3770d20f9852143d50bf6094e640b485cb2e189a2099085ff45"
 dependencies = [
  "bytes",
  "futures-core",
  "futures-sink",
- "pin-project-lite 0.2.8",
+ "pin-project-lite 0.2.9",
  "tokio",
  "tracing",
 ]
 
 [[package]]
 name = "toml"
-version = "0.5.8"
+version = "0.5.9"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a31142970826733df8241ef35dc040ef98c679ab14d7c3e54d827099b3acecaa"
+checksum = "8d82e1a7758622a465f8cee077614c73484dac5b836c02ff6a40d5d1010324d7"
 dependencies = [
  "serde",
 ]
 
 [[package]]
 name = "tower-service"
-version = "0.3.1"
+version = "0.3.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "360dfd1d6d30e05fda32ace2c8c70e9c0a9da713275777f5a4dbb8a1893930c6"
+checksum = "b6bc1c9ce2b5135ac7f93c72918fc37feb872bdc6a5533a8b85eb4b86bfdae52"
 
 [[package]]
 name = "tracing"
-version = "0.1.32"
+version = "0.1.35"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "4a1bdf54a7c28a2bbf701e1d2233f6c77f473486b94bee4f9678da5a148dca7f"
+checksum = "a400e31aa60b9d44a52a8ee0343b5b18566b03a8321e0d321f695cf56e940160"
 dependencies = [
  "cfg-if",
  "log",
- "pin-project-lite 0.2.8",
+ "pin-project-lite 0.2.9",
  "tracing-attributes",
  "tracing-core",
 ]
 
 [[package]]
 name = "tracing-attributes"
-version = "0.1.20"
+version = "0.1.21"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "2e65ce065b4b5c53e73bb28912318cb8c9e9ad3921f1d669eb0e68b4c8143a2b"
+checksum = "cc6b8ad3567499f98a1db7a752b07a7c8c7c7c34c332ec00effb2b0027974b7c"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -6449,19 +6447,19 @@ dependencies = [
 
 [[package]]
 name = "tracing-core"
-version = "0.1.24"
+version = "0.1.27"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "90442985ee2f57c9e1b548ee72ae842f4a9a20e3f417cc38dbc5dc684d9bb4ee"
+checksum = "7709595b8878a4965ce5e87ebf880a7d39c9afc6837721b21a5a816a8117d921"
 dependencies = [
- "lazy_static",
+ "once_cell",
  "valuable",
 ]
 
 [[package]]
 name = "tracing-log"
-version = "0.1.2"
+version = "0.1.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a6923477a48e41c1951f1999ef8bb5a3023eb723ceadafe78ffb65dc366761e3"
+checksum = "78ddad33d2d10b1ed7eb9d1f518a5674713876e97e5bb9b7345a7984fbb4f922"
 dependencies = [
  "lazy_static",
  "log",
@@ -6470,9 +6468,9 @@ dependencies = [
 
 [[package]]
 name = "tracing-subscriber"
-version = "0.3.10"
+version = "0.3.11"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b9df98b037d039d03400d9dd06b0f8ce05486b5f25e9a2d7d36196e142ebbc52"
+checksum = "4bc28f93baff38037f64e6f43d34cfa1605f27a49c34e8a04c5e78b0babf2596"
 dependencies = [
  "ansi_term",
  "lazy_static",
@@ -6566,7 +6564,7 @@ dependencies = [
  "lazy_static",
  "log",
  "lru-cache",
- "parking_lot 0.12.0",
+ "parking_lot 0.12.1",
  "resolv-conf",
  "smallvec",
  "thiserror",
@@ -6638,7 +6636,7 @@ dependencies = [
  "itertools",
  "lazy_static",
  "log",
- "parking_lot 0.12.0",
+ "parking_lot 0.12.1",
  "rand 0.8.5",
  "rand_xorshift",
  "rayon",
@@ -6696,9 +6694,15 @@ dependencies = [
 
 [[package]]
 name = "unicode-bidi"
-version = "0.3.7"
+version = "0.3.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1a01404663e3db436ed2746d9fefef640d868edae3cceb81c3b8d5732fda678f"
+checksum = "099b7128301d285f79ddd55b9a83d5e6b9e97c92e0ea0daebee7263e932de992"
+
+[[package]]
+name = "unicode-ident"
+version = "1.0.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "5bd2fe26506023ed7b5e1e315add59d6f584c621d037f9368fea9cfb988f368c"
 
 [[package]]
 name = "unicode-normalization"
@@ -6723,9 +6727,9 @@ checksum = "3ed742d4ea2bd1176e236172c8429aaf54486e7ac098db29ffe6529e0ce50973"
 
 [[package]]
 name = "unicode-xid"
-version = "0.2.2"
+version = "0.2.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8ccb82d61f80a663efe1f787a51b16b5a51e3314d6ac365b08639f52387b33f3"
+checksum = "957e51f3646910546462e67d5f7599b9e4fb8acdd304b087a6494730f9eebf04"
 
 [[package]]
 name = "universal-hash"
@@ -6744,7 +6748,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "35581ff83d4101e58b582e607120c7f5ffb17e632a980b1f38334d76b36908b2"
 dependencies = [
  "bytes",
- "tokio-util 0.6.9",
+ "tokio-util 0.6.10",
 ]
 
 [[package]]
@@ -6791,7 +6795,7 @@ version = "0.8.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "bc5cf98d8186244414c848017f0e2676b3fcb46807f6668a97dfe67359a3c4b7"
 dependencies = [
- "getrandom 0.2.6",
+ "getrandom 0.2.7",
  "serde",
 ]
 
@@ -6824,7 +6828,7 @@ dependencies = [
  "lockfile",
  "logging",
  "monitoring_api",
- "parking_lot 0.12.0",
+ "parking_lot 0.12.1",
  "rand 0.8.5",
  "reqwest",
  "ring",
@@ -6940,7 +6944,7 @@ dependencies = [
  "tokio-rustls",
  "tokio-stream",
  "tokio-tungstenite",
- "tokio-util 0.6.9",
+ "tokio-util 0.6.10",
  "tower-service",
  "tracing",
 ]
@@ -6971,9 +6975,9 @@ checksum = "cccddf32554fecc6acb585f82a32a72e28b48f8c4c1883ddfeeeaa96f7d8e519"
 
 [[package]]
 name = "wasi"
-version = "0.10.2+wasi-snapshot-preview1"
+version = "0.10.0+wasi-snapshot-preview1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "fd6fbd9a79829dd1ad0cc20627bf1ed606756a7f77edff7b66b7064f9cb327c6"
+checksum = "1a143597ca7c7793eff794def352d41792a93c481eb1042423ff7ff72ba2c31f"
 
 [[package]]
 name = "wasi"
@@ -6983,19 +6987,19 @@ checksum = "9c8d87e72b64a3b4db28d11ce29237c246188f4f51057d65a7eab63b7987e423"
 
 [[package]]
 name = "wasm-bindgen"
-version = "0.2.79"
+version = "0.2.81"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "25f1af7423d8588a3d840681122e72e6a24ddbcb3f0ec385cac0d12d24256c06"
+checksum = "7c53b543413a17a202f4be280a7e5c62a1c69345f5de525ee64f8cfdbc954994"
 dependencies = [
  "cfg-if",
  "wasm-bindgen-macro",
 ]
 
 [[package]]
 name = "wasm-bindgen-backend"
-version = "0.2.79"
+version = "0.2.81"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8b21c0df030f5a177f3cba22e9bc4322695ec43e7257d865302900290bcdedca"
+checksum = "5491a68ab4500fa6b4d726bd67408630c3dbe9c4fe7bda16d5c82a1fd8c7340a"
 dependencies = [
  "bumpalo",
  "lazy_static",
@@ -7008,9 +7012,9 @@ dependencies = [
 
 [[package]]
 name = "wasm-bindgen-futures"
-version = "0.4.29"
+version = "0.4.31"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "2eb6ec270a31b1d3c7e266b999739109abce8b6c87e4b31fcfcd788b65267395"
+checksum = "de9a9cec1733468a8c657e57fa2413d2ae2c0129b95e87c5b72b8ace4d13f31f"
 dependencies = [
  "cfg-if",
  "js-sys",
@@ -7020,19 +7024,19 @@ dependencies = [
 
 [[package]]
 name = "wasm-bindgen-macro"
-version = "0.2.79"
+version = "0.2.81"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "2f4203d69e40a52ee523b2529a773d5ffc1dc0071801c87b3d270b471b80ed01"
+checksum = "c441e177922bc58f1e12c022624b6216378e5febc2f0533e41ba443d505b80aa"
 dependencies = [
  "quote",
  "wasm-bindgen-macro-support",
 ]
 
 [[package]]
 name = "wasm-bindgen-macro-support"
-version = "0.2.79"
+version = "0.2.81"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "bfa8a30d46208db204854cadbb5d4baf5fcf8071ba5bf48190c3e59937962ebc"
+checksum = "7d94ac45fcf608c1f45ef53e748d35660f168490c10b23704c7779ab8f5c3048"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -7043,15 +7047,15 @@ dependencies = [
 
 [[package]]
 name = "wasm-bindgen-shared"
-version = "0.2.79"
+version = "0.2.81"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "3d958d035c4438e28c70e4321a2911302f10135ce78a9c7834c0cab4123d06a2"
+checksum = "6a89911bd99e5f3659ec4acf9c4d93b0a90fe4a2a11f15328472058edc5261be"
 
 [[package]]
 name = "wasm-bindgen-test"
-version = "0.3.29"
+version = "0.3.31"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "45c8d417d87eefa0087e62e3c75ad086be39433449e2961add9a5d9ce5acc2f1"
+checksum = "68b30cf2cba841a812f035c40c50f53eb9c56181192a9dd2c71b65e6a87a05ba"
 dependencies = [
  "console_error_panic_hook",
  "js-sys",
@@ -7063,9 +7067,9 @@ dependencies = [
 
 [[package]]
 name = "wasm-bindgen-test-macro"
-version = "0.3.29"
+version = "0.3.31"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d0e560d44db5e73b69a9757a15512fe7e1ef93ed2061c928871a4025798293dd"
+checksum = "88ad594bf33e73cafcac2ae9062fc119d4f75f9c77e25022f91c9a64bd5b6463"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -7088,9 +7092,9 @@ dependencies = [
 
 [[package]]
 name = "web-sys"
-version = "0.3.56"
+version = "0.3.58"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c060b319f29dd25724f09a2ba1418f142f539b2be99fbf4d2d5a8f7330afb8eb"
+checksum = "2fed94beee57daf8dd7d51f2b15dc2bcde92d7a72304cdf662a4371008b71b90"
 dependencies = [
  "js-sys",
  "wasm-bindgen",
@@ -7116,7 +7120,7 @@ dependencies = [
  "jsonrpc-core",
  "log",
  "once_cell",
- "parking_lot 0.12.0",
+ "parking_lot 0.12.1",
  "pin-project 1.0.10",
  "reqwest",
  "rlp",
@@ -7126,7 +7130,7 @@ dependencies = [
  "soketto",
  "tiny-keccak",
  "tokio",
- "tokio-util 0.6.9",
+ "tokio-util 0.6.10",
  "url",
  "web3-async-native-tls",
 ]
@@ -7190,9 +7194,9 @@ dependencies = [
 
 [[package]]
 name = "webpki-roots"
-version = "0.22.2"
+version = "0.22.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "552ceb903e957524388c4d3475725ff2c8b7960922063af6ce53c9a43da07449"
+checksum = "44d8de8415c823c8abd270ad483c6feeac771fad964890779f9a8cb24fbbc1bf"
 dependencies = [
  "webpki 0.22.0",
 ]
@@ -7265,9 +7269,9 @@ dependencies = [
 
 [[package]]
 name = "windows-sys"
-version = "0.34.0"
+version = "0.36.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5acdd78cb4ba54c0045ac14f62d8f94a03d10047904ae2a40afa1e99d8f70825"
+checksum = "ea04155a16a59f9eab786fe12a4a450e75cdb175f9e0d80da1e17db09f55b8d2"
 dependencies = [
  "windows_aarch64_msvc",
  "windows_i686_gnu",
@@ -7278,33 +7282,33 @@ dependencies = [
 
 [[package]]
 name = "windows_aarch64_msvc"
-version = "0.34.0"
+version = "0.36.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "17cffbe740121affb56fad0fc0e421804adf0ae00891205213b5cecd30db881d"
+checksum = "9bb8c3fd39ade2d67e9874ac4f3db21f0d710bee00fe7cab16949ec184eeaa47"
 
 [[package]]
 name = "windows_i686_gnu"
-version = "0.34.0"
+version = "0.36.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "2564fde759adb79129d9b4f54be42b32c89970c18ebf93124ca8870a498688ed"
+checksum = "180e6ccf01daf4c426b846dfc66db1fc518f074baa793aa7d9b9aaeffad6a3b6"
 
 [[package]]
 name = "windows_i686_msvc"
-version = "0.34.0"
+version = "0.36.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9cd9d32ba70453522332c14d38814bceeb747d80b3958676007acadd7e166956"
+checksum = "e2e7917148b2812d1eeafaeb22a97e4813dfa60a3f8f78ebe204bcc88f12f024"
 
 [[package]]
 name = "windows_x86_64_gnu"
-version = "0.34.0"
+version = "0.36.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "cfce6deae227ee8d356d19effc141a509cc503dfd1f850622ec4b0f84428e1f4"
+checksum = "4dcd171b8776c41b97521e5da127a2d86ad280114807d0b2ab1e462bc764d9e1"
 
 [[package]]
 name = "windows_x86_64_msvc"
-version = "0.34.0"
+version = "0.36.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d19538ccc21819d01deaf88d6a17eae6596a12e9aafdbb97916fb49896d89de9"
+checksum = "c811ca4a8c853ef420abd8592ba53ddbbac90410fab6903b3e79972a631f7680"
 
 [[package]]
 name = "winreg"
@@ -7383,7 +7387,7 @@ dependencies = [
  "futures",
  "log",
  "nohash-hasher",
- "parking_lot 0.12.0",
+ "parking_lot 0.12.1",
  "rand 0.8.5",
  "static_assertions",
 ]
@@ -7420,5 +7424,5 @@ dependencies = [
  "crc32fast",
  "flate2",
  "thiserror",
- "time 0.1.43",
+ "time 0.1.44",
 ]
```
