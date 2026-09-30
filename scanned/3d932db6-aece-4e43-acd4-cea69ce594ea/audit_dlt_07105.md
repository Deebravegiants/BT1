# [?] Fix RUSTSEC-2022-0032 (#3311)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2022-07-05
Source: https://github.com/sigp/lighthouse/commit/3dc323b035d3c29f8f680be9df29d34d051dc71d
Type: security-commit

## Details
Fix RUSTSEC-2022-0032 (#3311)

## Issue Addressed
Failure of cargo audit for [RUSTSEC-2022-0032](https://rustsec.org/advisories/RUSTSEC-2022-0032)

## Proposed Changes
Cargo update does the trick again

## Additional Info
na

## Patch
### Cargo.lock
```diff
@@ -141,15 +141,15 @@ dependencies = [
 
 [[package]]
 name = "anyhow"
-version = "1.0.57"
+version = "1.0.58"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "08f9b8508dccb7687a1d6c4ce66b2b0ecef467c94667de27d8d7fe1f8d2a9cdc"
+checksum = "bb07d2053ccdbe10e2af2995a2f116c1330396493dc1269f6a91d0ae82e19704"
 
 [[package]]
 name = "arbitrary"
-version = "1.1.2"
+version = "1.1.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "25e0a02cf12f1b1f48b14cb7f8217b876d09992b39c816ffb3b1ba64dd979a87"
+checksum = "5a7924531f38b1970ff630f03eb20a2fde69db5c590c93b0f3482e95dcc5fd60"
 dependencies = [
  "derive_arbitrary",
 ]
@@ -268,9 +268,9 @@ checksum = "904dfeac50f3cdaba28fc6f57fdcddb75f49ed61346676a78c4ffe55877802fd"
 
 [[package]]
 name = "base64ct"
-version = "1.5.0"
+version = "1.5.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "dea908e7347a8c64e378c17e30ef880ad73e3b4498346b055c2c00ea342f3179"
+checksum = "3bdca834647821e0b13d9539a8634eb62d3501b6b6c2cec1722786ee6671b851"
 
 [[package]]
 name = "beacon_chain"
@@ -472,9 +472,9 @@ dependencies = [
 
 [[package]]
 name = "blst"
-version = "0.3.9"
+version = "0.3.10"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c521c26a784d5c4bcd98d483a7d3518376e9ff1efbcfa9e2d456ab8183752303"
+checksum = "6a30d0edd9dd1c60ddb42b80341c7852f6f985279a5c1a83659dcb65899dec99"
 dependencies = [
  "cc",
  "glob",
@@ -762,7 +762,7 @@ dependencies = [
  "slot_clock",
  "store",
  "task_executor",
- "time 0.3.9",
+ "time 0.3.11",
  "timer",
  "tokio",
  "types",
@@ -936,9 +936,9 @@ dependencies = [
 
 [[package]]
 name = "crossbeam-utils"
-version = "0.8.9"
+version = "0.8.10"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8ff1f980957787286a554052d03c7aee98d99cc32e09f6d45f0a814133c87978"
+checksum = "7d82ee10ce34d7bc12c2122495e7593a9c41347ecdd64185af4ecf72cb1a7f83"
 dependencies = [
  "cfg-if",
  "once_cell",
@@ -964,9 +964,9 @@ dependencies = [
 
 [[package]]
 name = "crypto-common"
-version = "0.1.3"
+version = "0.1.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "57952ca27b5e3606ff4dd79b0020231aaf9d6aa76dc05fd30137538c50bd3ce8"
+checksum = "5999502d32b9c48d492abe66392408144895020ec4709e549e840799f3bb74c0"
 dependencies = [
  "generic-array",
  "typenum",
@@ -1190,9 +1190,9 @@ dependencies = [
 
 [[package]]
 name = "derive_arbitrary"
-version = "1.1.2"
+version = "1.1.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8728db27dd9033a7456655aaeb35fde74425d0f130b4cb18a19171ef38a1b454"
+checksum = "c9a577516173adb681466d517d39bd468293bc2c2a16439375ef0f35bba45f3d"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -1400,9 +1400,9 @@ dependencies = [
 
 [[package]]
 name = "either"
-version = "1.6.1"
+version = "1.7.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e78d4f1cc4ae33bbfc157ed5d5a5ef3bc29227303d595861deb238fcec4e9457"
+checksum = "3f107b87b6afc2a64fd13cac55fe06d6c8859f12d4b14cbcdd2c67d0976781be"
 
 [[package]]
 name = "elliptic-curve"
@@ -2017,9 +2017,9 @@ dependencies = [
 
 [[package]]
 name = "fixedbitset"
-version = "0.4.1"
+version = "0.4.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "279fb028e20b3c4c320317955b77c5e0c9701f05a1d309905d6fc702cdc5053e"
+checksum = "0ce7134b9999ecaf8bcd65542e436736ef32ddca1b3e06094cb6ec5755203b80"
 
 [[package]]
 name = "flate2"
@@ -2743,9 +2743,9 @@ dependencies = [
 
 [[package]]
 name = "indexmap"
-version = "1.9.0"
+version = "1.9.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6c6392766afd7964e2531940894cffe4bd8d7d17dbc3c1c4857040fd4b33bdb3"
+checksum = "10a35a97730320ffe8e2d410b5d3b69279b98d2c14bdb8b70ea89ecf7888d41e"
 dependencies = [
  "autocfg 1.1.0",
  "hashbrown 0.12.1",
@@ -3042,7 +3042,7 @@ dependencies = [
  "libp2p-yamux",
  "multiaddr 0.14.0",
  "parking_lot 0.12.1",
- "pin-project 1.0.10",
+ "pin-project 1.0.11",
  "rand 0.7.3",
  "smallvec",
 ]
@@ -3068,7 +3068,7 @@ dependencies = [
  "multihash 0.14.0",
  "multistream-select 0.10.4",
  "parking_lot 0.11.2",
- "pin-project 1.0.10",
+ "pin-project 1.0.11",
  "prost 0.9.0",
  "prost-build 0.9.0",
  "rand 0.8.5",
@@ -3103,7 +3103,7 @@ dependencies = [
  "multihash 0.16.2",
  "multistream-select 0.11.0",
  "parking_lot 0.12.1",
- "pin-project 1.0.10",
+ "pin-project 1.0.11",
  "prost 0.10.4",
  "prost-build 0.10.4",
  "rand 0.8.5",
@@ -3182,9 +3182,9 @@ dependencies = [
 
 [[package]]
 name = "libp2p-metrics"
-version = "0.6.0"
+version = "0.6.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "adc4357140141ba9739eee71b20aa735351c0fc642635b2bffc7f57a6b5c1090"
+checksum = "564a7e5284d7d9b3140fdfc3cb6567bc32555e86a21de5604c2ec85da05cf384"
 dependencies = [
  "libp2p-core 0.33.0",
  "libp2p-gossipsub",
@@ -3263,7 +3263,7 @@ dependencies = [
  "instant",
  "libp2p-core 0.33.0",
  "log",
- "pin-project 1.0.10",
+ "pin-project 1.0.11",
  "rand 0.7.3",
  "smallvec",
  "thiserror",
@@ -3506,9 +3506,9 @@ dependencies = [
 
 [[package]]
 name = "linked-hash-map"
-version = "0.5.4"
+version = "0.5.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7fb9b38af92608140b86b693604b9ffcc5824240a484d1ecd4795bacb2fe88f3"
+checksum = "0717cef1bc8b636c6e1c1bbdefc09e6322da8a9321966e8928ef80d20f7f770f"
 
 [[package]]
 name = "lock_api"
@@ -3703,9 +3703,9 @@ dependencies = [
 
 [[package]]
 name = "mio"
-version = "0.8.3"
+version = "0.8.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "713d550d9b44d89174e066b7a6217ae06234c10cb47819a88290d2b353c31799"
+checksum = "57ee1c23c7c63b0c9250c339ffdc69255f110b298b901b9f6c82547b7b87caaf"
 dependencies = [
  "libc",
  "log",
@@ -3856,7 +3856,7 @@ dependencies = [
  "bytes",
  "futures",
  "log",
- "pin-project 1.0.10",
+ "pin-project 1.0.11",
  "smallvec",
  "unsigned-varint 0.7.1",
 ]
@@ -3870,7 +3870,7 @@ dependencies = [
  "bytes",
  "futures",
  "log",
- "pin-project 1.0.10",
+ "pin-project 1.0.11",
  "smallvec",
  "unsigned-varint 0.7.1",
 ]
@@ -4086,9 +4086,9 @@ dependencies = [
 
 [[package]]
 name = "once_cell"
-version = "1.12.0"
+version = "1.13.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7709cef83f0c1f58f666e746a08b21e0085f7440fa6a29cc194d68aac97a4225"
+checksum = "18a6dbe30758c9f83eb00cbea4ac95966305f5a7772f3f42ebfc7fc7eddbd8e1"
 
 [[package]]
 name = "oorandom"
@@ -4136,9 +4136,9 @@ checksum = "ff011a302c396a5197692431fc1948019154afc178baf7d8e37367442a4601cf"
 
 [[package]]
 name = "openssl-src"
-version = "111.20.0+1.1.1o"
+version = "111.22.0+1.1.1q"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "92892c4f87d56e376e469ace79f1128fdaded07646ddf73aa0be4706ff712dec"
+checksum = "8f31f0d509d1c1ae9cada2f9539ff8f37933831fd5098879e482aa687d659853"
 dependencies = [
  "cc",
 ]
@@ -4353,27 +4353,27 @@ dependencies = [
 
 [[package]]
 name = "pin-project"
-version = "0.4.29"
+version = "0.4.30"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9615c18d31137579e9ff063499264ddc1278e7b1982757ebc111028c4d1dc909"
+checksum = "3ef0f924a5ee7ea9cbcea77529dba45f8a9ba9f622419fe3386ca581a3ae9d5a"
 dependencies = [
- "pin-project-internal 0.4.29",
+ "pin-project-internal 0.4.30",
 ]
 
 [[package]]
 name = "pin-project"
-version = "1.0.10"
+version = "1.0.11"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "58ad3879ad3baf4e44784bc6a718a8698867bb991f8ce24d1bcbe2cfb4c3a75e"
+checksum = "78203e83c48cffbe01e4a2d35d566ca4de445d79a85372fc64e378bfc812a260"
 dependencies = [
- "pin-project-internal 1.0.10",
+ "pin-project-internal 1.0.11",
 ]
 
 [[package]]
 name = "pin-project-internal"
-version = "0.4.29"
+version = "0.4.30"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "044964427019eed9d49d9d5bbce6047ef18f37100ea400912a9fa4a3523ab12a"
+checksum = "851c8d0ce9bebe43790dedfc86614c23494ac9f423dd618d3a61fc693eafe61e"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -4382,9 +4382,9 @@ dependencies = [
 
 [[package]]
 name = "pin-project-internal"
-version = "1.0.10"
+version = "1.0.11"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "744b6f092ba29c3650faf274db506afd39944f48420f6c86b17cfe0ee1cb36bb"
+checksum = "710faf75e1b33345361201d36d04e98ac1ed8909151a017ed384700836104c74"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -4567,9 +4567,9 @@ checksum = "dbf0c48bc1d91375ae5c3cd81e3722dff1abcf81a30960240640d223f59fe0e5"
 
 [[package]]
 name = "proc-macro2"
-version = "1.0.39"
+version = "1.0.40"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c54b25569025b7fc9651de43004ae593a75ad88543b17178aa5e1b9c4f15f56f"
+checksum = "dd96a1e8ed2596c337f8eae5f24924ec83f5ad5ab21ea8e455d3566c69fbcaf7"
 dependencies = [
  "unicode-ident",
 ]
@@ -4824,21 +4824,21 @@ dependencies = [
 
 [[package]]
 name = "quote"
-version = "1.0.18"
+version = "1.0.20"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a1feb54ed693b93a84e14094943b84b7c4eae204c512b7ccb95ab0c66d278ad1"
+checksum = "3bcdf212e9776fbcb2d23ab029360416bb1706b1aea2d1a5ba002727cbcab804"
 dependencies = [
  "proc-macro2",
 ]
 
 [[package]]
 name = "r2d2"
-version = "0.8.9"
+version = "0.8.10"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "545c5bc2b880973c9c10e4067418407a0ccaa3091781d1671d46eb35107cb26f"
+checksum = "51de85fb3fb6524929c8a2eb85e6b6d363de4e8c48f9e2c2eac4944abc181c93"
 dependencies = [
  "log",
- "parking_lot 0.11.2",
+ "parking_lot 0.12.1",
  "scheduled-thread-pool",
 ]
 
@@ -4990,9 +4990,9 @@ dependencies = [
 
 [[package]]
 name = "regex"
-version = "1.5.6"
+version = "1.6.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d83f127d94bdbcda4c8cc2e50f6f84f4b611f69c902699ca385a39c3a75f9ff1"
+checksum = "4c4eb3267174b8c6c2f654116623910a0fef09c4753f8dd83db29c48a0df988b"
 dependencies = [
  "aho-corasick",
  "memchr",
@@ -5010,9 +5010,9 @@ dependencies = [
 
 [[package]]
 name = "regex-syntax"
-version = "0.6.26"
+version = "0.6.27"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "49b3de9ec5dc0a3417da371aab17d729997c15010e7fd24ff707773a33bddb64"
+checksum = "a3f87b73ce11b1619a3c6332f45341e0047173771e8b8b73f87bfeefb7b56244"
 
 [[package]]
 name = "remove_dir_all"
@@ -5191,7 +5191,7 @@ version = "0.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "bfa0f585226d2e68097d4f95d113b15b83a82e819ab25717ec0590d9584ef366"
 dependencies = [
- "semver 1.0.10",
+ "semver 1.0.12",
 ]
 
 [[package]]
@@ -5221,9 +5221,9 @@ dependencies = [
 
 [[package]]
 name = "rustversion"
-version = "1.0.6"
+version = "1.0.7"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f2cc38e8fa666e2de3c4aba7edeb5ffc5246c1c2ed0e3d17e560aeeba736b23f"
+checksum = "a0a5f7c728f5d284929a1cccb5bc19884422bfe6ef4d6c409da2c41838983fcf"
 
 [[package]]
 name = "rw-stream-sink"
@@ -5232,7 +5232,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "4da5fcb054c46f5a5dff833b129285a93d3f0179531735e6c866e8cc307d2020"
 dependencies = [
  "futures",
- "pin-project 0.4.29",
+ "pin-project 0.4.30",
  "static_assertions",
 ]
 
@@ -5243,7 +5243,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "26338f5e09bb721b85b135ea05af7767c90b52f6de4f087d4f4a3a9d64e7dc04"
 dependencies = [
  "futures",
- "pin-project 1.0.10",
+ "pin-project 1.0.11",
  "static_assertions",
 ]
 
@@ -5418,9 +5418,9 @@ dependencies = [
 
 [[package]]
 name = "semver"
-version = "1.0.10"
+version = "1.0.12"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a41d061efea015927ac527063765e73601444cdc344ba855bc7bd44578b25e1c"
+checksum = "a2333e6df6d6598f2b1974829f853c2b4c5f4a6e503c10af918081aa6f8564e1"
 
 [[package]]
 name = "semver-parser"
@@ -5447,9 +5447,9 @@ dependencies = [
 
 [[package]]
 name = "serde"
-version = "1.0.137"
+version = "1.0.138"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "61ea8d54c77f8315140a05f4c7237403bf38b72704d031543aa1d16abbf517d1"
+checksum = "1578c6245786b9d168c5447eeacfb96856573ca56c9d68fdcf394be134882a47"
 dependencies = [
  "serde_derive",
 ]
@@ -5476,9 +5476,9 @@ dependencies = [
 
 [[package]]
 name = "serde_derive"
-version = "1.0.137"
+version = "1.0.138"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1f26faba0c3959972377d3b2d306ee9f71faee9714294e41bb777f83f88578be"
+checksum = "023e9b1467aef8a10fb88f25611870ada9800ef7e22afce356bb0d2387b6f27c"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -5487,9 +5487,9 @@ dependencies = [
 
 [[package]]
 name = "serde_json"
-version = "1.0.81"
+version = "1.0.82"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9b7ce2b32a1aed03c558dc61a5cd328f15aff2dbc17daad8fb8af04d2100e15c"
+checksum = "82c2c1fdcd807d1098552c5b9a36e425e42e9fbd7c6a37a8425f390f781f7fa7"
 dependencies = [
  "itoa 1.0.2",
  "ryu",
@@ -5666,7 +5666,7 @@ dependencies = [
  "num-bigint",
  "num-traits",
  "thiserror",
- "time 0.3.9",
+ "time 0.3.11",
 ]
 
 [[package]]
@@ -5786,7 +5786,7 @@ dependencies = [
  "serde",
  "serde_json",
  "slog",
- "time 0.3.9",
+ "time 0.3.11",
 ]
 
 [[package]]
@@ -5831,7 +5831,7 @@ dependencies = [
  "slog",
  "term",
  "thread_local",
- "time 0.3.9",
+ "time 0.3.11",
 ]
 
 [[package]]
@@ -5870,9 +5870,9 @@ dependencies = [
 
 [[package]]
 name = "smallvec"
-version = "1.8.0"
+version = "1.9.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f2dd574626839106c320a323308629dcb1acfc96e32a8cba364ddc61ac23ee83"
+checksum = "2fd0db749597d91ff862fd1d55ea87f7855a744a8425a64695b6fca237d1dad1"
 
 [[package]]
 name = "snap"
@@ -6045,9 +6045,9 @@ dependencies = [
 
 [[package]]
 name = "strum_macros"
-version = "0.24.0"
+version = "0.24.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6878079b17446e4d3eba6192bb0a2950d5b14f0ed8424b852310e5a94345d0ef"
+checksum = "4faebde00e8ff94316c01800f9054fd2ba77d30d9e922541913051d1d978918b"
 dependencies = [
  "heck 0.4.0",
  "proc-macro2",
@@ -6087,9 +6087,9 @@ dependencies = [
 
 [[package]]
 name = "syn"
-version = "1.0.96"
+version = "1.0.98"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0748dd251e24453cb8717f0354206b91557e4ec8703673a4b30208f2abaf1ebf"
+checksum = "c50aef8a904de4c23c788f104b7dddc7d6f79c647c7c8ce4cc8f73eb0ca773dd"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -6256,9 +6256,9 @@ dependencies = [
 
 [[package]]
 name = "time"
-version = "0.3.9"
+version = "0.3.11"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c2702e08a7a860f005826c6815dcac101b19b5eb330c27fe4a5928fec1d20ddd"
+checksum = "72c91f41dcb2f096c05f0873d667dceec1087ce5bcf984ec8ffb19acddbb3217"
 dependencies = [
  "itoa 1.0.2",
  "libc",
@@ -6418,7 +6418,7 @@ checksum = "511de3f85caf1c98983545490c3d09685fa8eb634e57eec22bb4db271f46cbd8"
 dependencies = [
  "futures-util",
  "log",
- "pin-project 1.0.10",
+ "pin-project 1.0.11",
  "tokio",
  "tungstenite",
 ]
@@ -6483,9 +6483,9 @@ dependencies = [
 
 [[package]]
 name = "tracing-attributes"
-version = "0.1.21"
+version = "0.1.22"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "cc6b8ad3567499f98a1db7a752b07a7c8c7c7c34c332ec00effb2b0027974b7c"
+checksum = "11c75893af559bc8e10716548bdef5cb2b983f8e637db9d0e15126b61b484ee2"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -6494,9 +6494,9 @@ dependencies = [
 
 [[package]]
 name = "tracing-core"
-version = "0.1.27"
+version = "0.1.28"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7709595b8878a4965ce5e87ebf880a7d39c9afc6837721b21a5a816a8117d921"
+checksum = "7b7358be39f2f274f322d2aaed611acc57f382e8eb1e5b48cb9ae30933495ce7"
 dependencies = [
  "once_cell",
  "valuable",
@@ -6515,13 +6515,13 @@ dependencies = [
 
 [[package]]
 name = "tracing-subscriber"
-version = "0.3.11"
+version = "0.3.14"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "4bc28f93baff38037f64e6f43d34cfa1605f27a49c34e8a04c5e78b0babf2596"
+checksum = "3a713421342a5a666b7577783721d3117f1b69a393df803ee17bb73b1e122a59"
 dependencies = [
  "ansi_term",
- "lazy_static",
  "matchers",
+ "once_cell",
  "regex",
  "sharded-slab",
  "smallvec",
@@ -6709,9 +6709,9 @@ dependencies = [
 
 [[package]]
 name = "ucd-trie"
-version = "0.1.3"
+version = "0.1.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "56dee185309b50d1f11bfedef0fe6d036842e3fb77413abef29f8f8d1c5d4c1c"
+checksum = "89570599c4fe5585de2b388aab47e99f7fa4e9238a1399f707a02e356058141c"
 
 [[package]]
 name = "uint"
@@ -6755,9 +6755,9 @@ checksum = "5bd2fe26506023ed7b5e1e315add59d6f584c621d037f9368fea9cfb988f368c"
 
 [[package]]
 name = "unicode-normalization"
-version = "0.1.19"
+version = "0.1.21"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d54590932941a9e9266f0832deed84ebe1bf2e4c9e4a3554d393d18f5e854bf9"
+checksum = "854cbdc4f7bc6ae19c820d44abdc3277ac3e1b2b93db20a636825d9322fb60e6"
 dependencies = [
  "tinyvec",
 ]
@@ -6985,7 +6985,7 @@ dependencies = [
  "mime_guess",
  "multipart",
  "percent-encoding",
- "pin-project 1.0.10",
+ "pin-project 1.0.11",
  "scoped-tls",
  "serde",
  "serde_json",
@@ -7171,7 +7171,7 @@ dependencies = [
  "log",
  "once_cell",
  "parking_lot 0.12.1",
- "pin-project 1.0.10",
+ "pin-project 1.0.11",
  "reqwest",
  "rlp",
  "secp256k1",
```
