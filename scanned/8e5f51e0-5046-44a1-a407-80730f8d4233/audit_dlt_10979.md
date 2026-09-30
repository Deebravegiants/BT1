# [?] chore: rename `unsound` to `experimental` (#184)

## Summary
Severity: Unknown
Chain: ZK
Component: succinctlabs/sp1
Published: 2025-10-22
Source: https://github.com/succinctlabs/sp1/commit/b51936e95a50bc5396dddfb032cf82d119e7cdd1
Type: security-commit

## Details
chore: rename `unsound` to `experimental` (#184)

* commit

* Cargo files

## Patch
### Cargo.lock
```diff
@@ -66,7 +66,7 @@ dependencies = [
  "const-hex",
  "derive_more 2.0.1",
  "hashbrown 0.16.0",
- "indexmap 2.11.4",
+ "indexmap 2.12.0",
  "itoa",
  "k256",
  "paste",
@@ -245,7 +245,7 @@ checksum = "c7c24de15d275a1ecfd47a380fb4d5ec9bfe0933f309ed5e705b775596a3574d"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
@@ -256,7 +256,16 @@ checksum = "9035ad2d096bed7955a320ee7e2230574d28fd3c3a0f186cbea1ff3c7eed5dbb"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
+]
+
+[[package]]
+name = "atomic"
+version = "0.6.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "a89cbf775b137e9b968e67227ef7f775587cde3fd31b0d8599dbd0f598a48340"
+dependencies = [
+ "bytemuck",
 ]
 
 [[package]]
@@ -446,7 +455,7 @@ version = "0.70.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "f49d8fed880d473ea71efb9bf597651e77201bdd4893efe54c9e5d65ae04ce6f"
 dependencies = [
- "bitflags 2.9.4",
+ "bitflags 2.10.0",
  "cexpr",
  "clang-sys",
  "itertools 0.13.0",
@@ -457,7 +466,7 @@ dependencies = [
  "regex",
  "rustc-hash 1.1.0",
  "shlex",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
@@ -468,9 +477,9 @@ checksum = "bef38d45163c2f1dde094a7dfd33ccf595c92905c8f8f4fdc18d06fb1037718a"
 
 [[package]]
 name = "bitflags"
-version = "2.9.4"
+version = "2.10.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "2261d10cca569e4643e526d8dc2e62e433cc8aba21ab764233731f8d369bf394"
+checksum = "812e12b5285cc515a9c72a5c1d3b6d46a19dac5acfef5265968c166106e31dd3"
 
 [[package]]
 name = "bitvec"
@@ -612,13 +621,13 @@ checksum = "3fce8dd7fcfcbf3a0a87d8f515194b49d6135acab73e18bd380d1d93bb1a15eb"
 dependencies = [
  "clap",
  "heck 0.4.1",
- "indexmap 2.11.4",
+ "indexmap 2.12.0",
  "log",
  "proc-macro2",
  "quote",
  "serde",
  "serde_json",
- "syn 2.0.106",
+ "syn 2.0.107",
  "tempfile",
  "toml",
 ]
@@ -680,19 +689,19 @@ dependencies = [
 
 [[package]]
 name = "clap"
-version = "4.5.49"
+version = "4.5.50"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f4512b90fa68d3a9932cea5184017c5d200f5921df706d45e853537dea51508f"
+checksum = "0c2cfd7bf8a6017ddaa4e32ffe7403d547790db06bd171c1c53926faab501623"
 dependencies = [
  "clap_builder",
  "clap_derive",
 ]
 
 [[package]]
 name = "clap_builder"
-version = "4.5.49"
+version = "4.5.50"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0025e98baa12e766c67ba13ff4695a887a1eba19569aad00a472546795bd6730"
+checksum = "0a4c05b9e80c5ccd3a7ef080ad7b6ba7d6fc00a985b8b157197075677c82c7a0"
 dependencies = [
  "anstream",
  "anstyle",
@@ -709,7 +718,7 @@ dependencies = [
  "heck 0.5.0",
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
@@ -1234,21 +1243,21 @@ dependencies = [
 
 [[package]]
 name = "csv"
-version = "1.3.1"
+version = "1.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "acdc4883a9c96732e4733212c01447ebd805833b7275a73ca3ee080fd77afdaf"
+checksum = "52cd9d68cf7efc6ddfaaee42e7288d3a99d613d4b50f76ce9827ae0c6e14f938"
 dependencies = [
  "csv-core",
  "itoa",
  "ryu",
- "serde",
+ "serde_core",
 ]
 
 [[package]]
 name = "csv-core"
-version = "0.1.12"
+version = "0.1.13"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7d02f3b0da4c6504f86e9cd789d8dbafab48c2321be74e9987593de5a894d93d"
+checksum = "704a3c26996a80471189265814dbc2c257598b96b8a7feae2d31ace646bb9782"
 dependencies = [
  "memchr",
 ]
@@ -1274,6 +1283,20 @@ dependencies = [
  "tracing-subscriber",
 ]
 
+[[package]]
+name = "dashmap"
+version = "6.1.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "5041cc499144891f3790297212f32a74fb938e5136a14943f338ef9e0ae276cf"
+dependencies = [
+ "cfg-if",
+ "crossbeam-utils",
+ "hashbrown 0.14.5",
+ "lock_api",
+ "once_cell",
+ "parking_lot_core",
+]
+
 [[package]]
 name = "dashu"
 version = "0.4.2"
@@ -1370,7 +1393,7 @@ checksum = "e0f8817865cacf3b93b943ca06b0fc5fd8e99eabfdb7ea5d296efcbc4afc4f69"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
@@ -1412,7 +1435,7 @@ checksum = "ef941ded77d15ca19b40374869ac6000af1c9f2a4c0f3d4c70926287e6364a8f"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
@@ -1441,7 +1464,7 @@ checksum = "cb7330aeadfbe296029522e6c40f315320aba36fc43a5b3632f3795348f3bd22"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
@@ -1452,7 +1475,7 @@ checksum = "bda628edc44c4bb645fbe0f758797143e4e07926f7ebf4e9bdfbd3d2ce621df3"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
  "unicode-xid",
 ]
 
@@ -1518,7 +1541,7 @@ checksum = "97369cbbc041bc366949bc74d34658d6cda5621039731c6310521892a3a20ae0"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
@@ -1547,13 +1570,13 @@ version = "3.2.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "7f7d4c414c94bc830797115b8e5f434d58e7e80cb42ba88508c14bc6ea270625"
 dependencies = [
- "bitflags 2.9.4",
+ "bitflags 2.10.0",
  "byteorder",
  "lazy_static",
  "proc-macro-error2",
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
@@ -1640,7 +1663,7 @@ checksum = "f282cfdfe92516eb26c2af8589c274c7c17681f5ecc03c18255fe741c6aa64eb"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
@@ -1820,7 +1843,7 @@ checksum = "162ee34ebcb7c64a8abebc059ce0fee27c2262618d7b60ed8faf72fef13c3650"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
@@ -1970,7 +1993,7 @@ dependencies = [
  "futures-sink",
  "futures-util",
  "http 0.2.12",
- "indexmap 2.11.4",
+ "indexmap 2.12.0",
  "slab",
  "tokio",
  "tokio-util",
@@ -1989,7 +2012,7 @@ dependencies = [
  "futures-core",
  "futures-sink",
  "http 1.3.1",
- "indexmap 2.11.4",
+ "indexmap 2.12.0",
  "slab",
  "tokio",
  "tokio-util",
@@ -2419,7 +2442,7 @@ checksum = "a0eb5a3343abf848c0984fe4604b2b105da9539376e24fc0a3b0007411ae4fd9"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
@@ -2440,9 +2463,9 @@ dependencies = [
 
 [[package]]
 name = "indexmap"
-version = "2.11.4"
+version = "2.12.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "4b0f83760fb341a774ed326568e19f5a863af4a952def8c39f9ab92fd95b88e5"
+checksum = "6717a8d2a5a929a1a2eb43a12812498ed141a0bcfb7e8f7844fbdbe4303bba9f"
 dependencies = [
  "equivalent",
  "hashbrown 0.16.0",
@@ -2501,9 +2524,9 @@ dependencies = [
 
 [[package]]
 name = "is_terminal_polyfill"
-version = "1.70.1"
+version = "1.70.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7943c866cc5cd64cbc25b2e01621d07fa8eb2a1a23160ee81ce38704e97b8ecf"
+checksum = "a6cb138bb79a146c1bd460005623e142ef0181e3d0219cb493e02f7d08a35695"
 
 [[package]]
 name = "itertools"
@@ -2642,7 +2665,7 @@ version = "0.1.10"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "416f7e718bdb06000964960ffa43b4335ad4012ae8b99060261aa4a8088d5ccb"
 dependencies = [
- "bitflags 2.9.4",
+ "bitflags 2.10.0",
  "libc",
 ]
 
@@ -2709,6 +2732,16 @@ version = "0.7.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "0e7465ac9959cc2b1404e8e2367b43684a6d13790fe23056cc8c6c5a6b7bcb94"
 
+[[package]]
+name = "md-5"
+version = "0.10.6"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "d89e7ee0cfbedfc4da3340218492196241d89eefb6dab27de5df917a6d2e78cf"
+dependencies = [
+ "cfg-if",
+ "digest",
+]
+
 [[package]]
 name = "memchr"
 version = "2.7.6"
@@ -2726,9 +2759,9 @@ dependencies = [
 
 [[package]]
 name = "memmap2"
-version = "0.9.8"
+version = "0.9.9"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "843a98750cd611cc2965a8213b53b43e715f13c37a9e096c6408e69990961db7"
+checksum = "744133e4a0e0a658e1374cf3bf8e415c4052a15a111acd372764c55b4177d490"
 dependencies = [
  "libc",
 ]
@@ -2762,13 +2795,23 @@ dependencies = [
 
 [[package]]
 name = "mio"
-version = "1.0.4"
+version = "1.1.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "78bed444cc8a2160f01cbcf811ef18cac863ad68ae8ca62092e8db51d51c761c"
+checksum = "69d83b0086dc8ecf3ce9ae2874b2d1290252e2a30720bea58a5c6639b0092873"
 dependencies = [
  "libc",
  "wasi",
- "windows-sys 0.59.0",
+ "windows-sys 0.61.2",
+]
+
+[[package]]
+name = "mti"
+version = "1.0.7-beta.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "73e89058909957124fd8271ac984c38733f080e0f0edd93322f82d7bd6a0010a"
+dependencies = [
+ "typeid_prefix",
+ "typeid_suffix",
 ]
 
 [[package]]
@@ -2959,9 +3002,9 @@ checksum = "42f5e15c9953c5e4ccceeb2e7382a716482c34515315f7b03532b8b4e8393d2d"
 
 [[package]]
 name = "once_cell_polyfill"
-version = "1.70.1"
+version = "1.70.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a4895175b425cb1f87721b59f0f286c2092bd4af812243672510e1ac53e2e0ad"
+checksum = "384b8ab6d37215f3c5301a95a4accb5d64aa607f1fcb26a11b5303878451b4fe"
 
 [[package]]
 name = "openssl-probe"
@@ -3340,7 +3383,7 @@ dependencies = [
  "proc-macro-crate 3.4.0",
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
@@ -3440,7 +3483,7 @@ checksum = "6e918e4ff8c4549eb882f14b3a4bc8c8bc93de829416eacf579f1207a8fbf861"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
@@ -3508,7 +3551,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "479ca8adacdd7ce8f1fb39ce9ecccbfe93a3f1344b3d0d97f20bc0196208f62b"
 dependencies = [
  "proc-macro2",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
@@ -3572,7 +3615,7 @@ dependencies = [
  "proc-macro-error-attr2",
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
@@ -3590,7 +3633,7 @@ version = "1.8.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "2bb0be07becd10686a0bb407298fb425360a5c44a663774406340c59a22de4ce"
 dependencies = [
- "bitflags 2.9.4",
+ "bitflags 2.10.0",
  "num-traits",
  "rand 0.9.2",
  "rand_chacha 0.9.0",
@@ -3628,7 +3671,7 @@ dependencies = [
  "itertools 0.12.1",
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
@@ -3641,7 +3684,7 @@ dependencies = [
  "itertools 0.14.0",
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
@@ -3837,7 +3880,7 @@ version = "0.5.18"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "ed2bf2547551a7053d6fdfafda3f938979645c44812fbfcda098faae3f1a362d"
 dependencies = [
- "bitflags 2.9.4",
+ "bitflags 2.10.0",
 ]
 
 [[package]]
@@ -4036,7 +4079,7 @@ version = "0.38.44"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "fdb5bc1ae2baa591800df16c9ca78619bf65c0488b41b96ccec5d11220d8c154"
 dependencies = [
- "bitflags 2.9.4",
+ "bitflags 2.10.0",
  "errno",
  "libc",
  "linux-raw-sys 0.4.15",
@@ -4049,7 +4092,7 @@ version = "1.1.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "cd15f8a2c5551a84d56efdc1cd049089e409ac19a3072d5037a17fd70719ff3e"
 dependencies = [
- "bitflags 2.9.4",
+ "bitflags 2.10.0",
  "errno",
  "libc",
  "linux-raw-sys 0.11.0",
@@ -4058,9 +4101,9 @@ dependencies = [
 
 [[package]]
 name = "rustls"
-version = "0.23.32"
+version = "0.23.33"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "cd3c25631629d034ce7cd9940adc9d45762d46de2b0f57193c4443b92c6d4d40"
+checksum = "751e04a496ca00bb97a5e043158d23d66b5aabf2e1d5aa2a0aaebb1aafe6f82c"
 dependencies = [
  "log",
  "once_cell",
@@ -4146,7 +4189,7 @@ dependencies = [
  "proc-macro-crate 3.4.0",
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
@@ -4200,7 +4243,7 @@ version = "3.5.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "b3297343eaf830f66ede390ea39da1d462b6b0c1b000f420d0a83f898bbbe6ef"
 dependencies = [
- "bitflags 2.9.4",
+ "bitflags 2.10.0",
  "core-foundation",
  "core-foundation-sys",
  "libc",
@@ -4263,7 +4306,7 @@ checksum = "d540f220d3187173da220f885ab66608367b6574e925011a9353e4badda91d79"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
@@ -4343,9 +4386,15 @@ checksum = "5d69265a08751de7844521fd15003ae0a888e035773ba05695c5c759a6f89eef"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
+[[package]]
+name = "sha1_smol"
+version = "1.0.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "bbfa15b3dddfee50a0fff136974b3e1bde555604ba463834a7eb7deb6417705d"
+
 [[package]]
 name = "sha2"
 version = "0.10.9"
@@ -4410,15 +4459,15 @@ checksum = "7a2ae44ef20feb57a68b23d846850f861394c2e02dc425a50098ae8c90267589"
 [[package]]
 name = "slop-air"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "p3-air",
 ]
 
 [[package]]
 name = "slop-algebra"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "itertools 0.13.0",
  "p3-field",
@@ -4428,7 +4477,7 @@ dependencies = [
 [[package]]
 name = "slop-alloc"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "serde",
  "slop-algebra",
@@ -4438,7 +4487,7 @@ dependencies = [
 [[package]]
 name = "slop-baby-bear"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "lazy_static",
  "p3-baby-bear",
@@ -4452,7 +4501,7 @@ dependencies = [
 [[package]]
 name = "slop-basefold"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "derive-where",
  "itertools 0.13.0",
@@ -4473,7 +4522,7 @@ dependencies = [
 [[package]]
 name = "slop-basefold-prover"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "derive-where",
  "itertools 0.13.0",
@@ -4500,7 +4549,7 @@ dependencies = [
 [[package]]
 name = "slop-bn254"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "ff 0.13.1",
  "p3-bn254-fr",
@@ -4515,7 +4564,7 @@ dependencies = [
 [[package]]
 name = "slop-challenger"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "futures",
  "p3-challenger",
@@ -4527,7 +4576,7 @@ dependencies = [
 [[package]]
 name = "slop-commit"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "p3-commit",
  "serde",
@@ -4537,7 +4586,7 @@ dependencies = [
 [[package]]
 name = "slop-dft"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "p3-dft",
  "serde",
@@ -4550,28 +4599,29 @@ dependencies = [
 [[package]]
 name = "slop-fri"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "p3-fri",
 ]
 
 [[package]]
 name = "slop-futures"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "crossbeam",
  "futures",
  "pin-project",
  "rayon",
  "thiserror 1.0.69",
  "tokio",
+ "tracing",
 ]
 
 [[package]]
 name = "slop-jagged"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "derive-where",
  "futures",
@@ -4604,15 +4654,15 @@ dependencies = [
 [[package]]
 name = "slop-keccak-air"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "p3-keccak-air",
 ]
 
 [[package]]
 name = "slop-koala-bear"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "lazy_static",
  "p3-koala-bear",
@@ -4626,23 +4676,23 @@ dependencies = [
 [[package]]
 name = "slop-matrix"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "p3-matrix",
 ]
 
 [[package]]
 name = "slop-maybe-rayon"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "p3-maybe-rayon",
 ]
 
 [[package]]
 name = "slop-merkle-tree"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "derive-where",
  "ff 0.13.1",
@@ -4669,7 +4719,7 @@ dependencies = [
 [[package]]
 name = "slop-multilinear"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "derive-where",
  "futures",
@@ -4690,15 +4740,15 @@ dependencies = [
 [[package]]
 name = "slop-poseidon2"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "p3-poseidon2",
 ]
 
 [[package]]
 name = "slop-stacked"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "derive-where",
  "futures",
@@ -4718,7 +4768,7 @@ dependencies = [
 [[package]]
 name = "slop-sumcheck"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "futures",
  "itertools 0.13.0",
@@ -4735,15 +4785,15 @@ dependencies = [
 [[package]]
 name = "slop-symmetric"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "p3-symmetric",
 ]
 
 [[package]]
 name = "slop-tensor"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "arrayvec",
  "derive-where",
@@ -4763,15 +4813,15 @@ dependencies = [
 [[package]]
 name = "slop-uni-stark"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "p3-uni-stark",
 ]
 
 [[package]]
 name = "slop-utils"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "p3-util",
  "tracing-forest",
@@ -4781,7 +4831,7 @@ dependencies = [
 [[package]]
 name = "slop-whir"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "derive-where",
  "futures",
@@ -4849,7 +4899,7 @@ dependencies = [
 [[package]]
 name = "sp1-build"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "anyhow",
  "cargo_metadata",
@@ -4862,7 +4912,7 @@ dependencies = [
 [[package]]
 name = "sp1-core-executor"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "bincode",
  "bytemuck",
@@ -4901,7 +4951,7 @@ dependencies = [
 [[package]]
 name = "sp1-core-machine"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "bincode",
  "cfg-if",
@@ -4947,7 +4997,7 @@ dependencies = [
 [[package]]
 name = "sp1-cuda"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "bincode",
  "bytes",
@@ -4966,7 +5016,7 @@ dependencies = [
 [[package]]
 name = "sp1-curves"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "cfg-if",
  "dashu",
@@ -4987,7 +5037,7 @@ dependencies = [
 [[package]]
 name = "sp1-derive"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -4997,7 +5047,7 @@ dependencies = [
 [[package]]
 name = "sp1-hypercube"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "arrayref",
  "deepsize2",
@@ -5041,7 +5091,7 @@ dependencies = [
 [[package]]
 name = "sp1-jit"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "dynasmrt",
  "hashbrown 0.14.5",
@@ -5055,7 +5105,7 @@ dependencies = [
 [[package]]
 name = "sp1-primitives"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "bincode",
  "blake3",
@@ -5077,11 +5127,12 @@ dependencies = [
 [[package]]
 name = "sp1-prover"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "anyhow",
  "bincode",
  "clap",
+ "dashmap",
  "dirs",
  "downloader",
  "enum-map",
@@ -5091,7 +5142,10 @@ dependencies = [
  "hex",
  "itertools 0.13.0",
  "lru",
+ "mti",
  "num-bigint 0.4.6",
+ "opentelemetry",
+ "pin-project",
  "rand 0.8.5",
  "serde",
  "serde_json",
@@ -5108,7 +5162,9 @@ dependencies = [
  "slop-symmetric",
  "sp1-core-executor",
  "sp1-core-machine",
+ "sp1-derive",
  "sp1-hypercube",
+ "sp1-jit",
  "sp1-primitives",
  "sp1-recursion-circuit",
  "sp1-recursion-compiler",
@@ -5127,7 +5183,7 @@ dependencies = [
 [[package]]
 name = "sp1-recursion-circuit"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "itertools 0.13.0",
  "rand 0.8.5",
@@ -5165,7 +5221,7 @@ dependencies = [
 [[package]]
 name = "sp1-recursion-compiler"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "backtrace",
  "cfg-if",
@@ -5185,7 +5241,7 @@ dependencies = [
 [[package]]
 name = "sp1-recursion-executor"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "backtrace",
  "cfg-if",
@@ -5208,7 +5264,7 @@ dependencies = [
 [[package]]
 name = "sp1-recursion-gnark-ffi"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "anyhow",
  "bincode",
@@ -5231,7 +5287,7 @@ dependencies = [
 [[package]]
 name = "sp1-recursion-machine"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "itertools 0.13.0",
  "rand 0.8.5",
@@ -5252,7 +5308,7 @@ dependencies = [
 [[package]]
 name = "sp1-sdk"
 version = "6.0.0"
-source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#8bd0a403a5ba8651f81b6b1c22e397c8be7c9b7b"
+source = "git+https://github.com/succinctlabs/sp1-wip.git?branch=multilinear_v6#3ca2c456194622a0ec800b18c8d2cde80a852784"
 dependencies = [
  "alloy-primitives",
  "anyhow",
@@ -5346,7 +5402,7 @@ dependencies = [
  "heck 0.5.0",
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
@@ -5358,7 +5414,7 @@ dependencies = [
  "heck 0.5.0",
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
@@ -5380,9 +5436,9 @@ dependencies = [
 
 [[package]]
 name = "syn"
-version = "2.0.106"
+version = "2.0.107"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "ede7c438028d4436d71104916910f5bb611972c5cfd7f89b8300a8186e6fada6"
+checksum = "2a26dbd934e5451d21ef060c018dae56fc073894c5a7896f882928a76e6d081b"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -5412,7 +5468,7 @@ checksum = "728a70f3dbaf5bab7f0c4b1ac8d7ae5ea60a4b5549c8a5914361c99147a709d2"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
@@ -5500,7 +5556,7 @@ checksum = "4fee6c4efc90059e10f81e6d42c60a18f76588c3d74cb83a0b242a2b6c7504c1"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
@@ -5511,7 +5567,7 @@ checksum = "3ff15c8ecd7de3849db632e14d18d2571fa09dfc5ed93479bc4485c7a517c913"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
@@ -5525,19 +5581,19 @@ dependencies = [
 
 [[package]]
 name = "tikv-jemalloc-sys"
-version = "0.6.0+5.3.0-1-ge13ca993e8ccb9ba9847cc330696e02839f328f7"
+version = "0.6.1+5.3.0-1-ge13ca993e8ccb9ba9847cc330696e02839f328f7"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "cd3c60906412afa9c2b5b5a48ca6a5abe5736aec9eb48ad05037a677e52e4e2d"
+checksum = "cd8aa5b2ab86a2cefa406d889139c162cbb230092f7d1d7cbc1716405d852a3b"
 dependencies = [
  "cc",
  "libc",
 ]
 
 [[package]]
 name = "tikv-jemallocator"
-version = "0.6.0"
+version = "0.6.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "4cec5ff18518d81584f477e9bfdf957f5bb0979b0bac3af4ca30b5b3ae2d2865"
+checksum = "0359b4327f954e0567e69fb191cf1436617748813819c94b8cd4a431422d053a"
 dependencies = [
  "libc",
  "tikv-jemalloc-sys",
@@ -5643,7 +5699,7 @@ checksum = "af407857209536a95c8e56f8231ef2c2e2aff839b22e07a1ffcbc617e9db9fa5"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
@@ -5716,7 +5772,7 @@ version = "0.19.15"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "1b5bb770da30e5cbfde35a2d7b9b8a2c4b8ef89548a7a6aeab5c9a576e3e7421"
 dependencies = [
- "indexmap 2.11.4",
+ "indexmap 2.12.0",
  "toml_datetime 0.6.11",
  "winnow 0.5.40",
 ]
@@ -5727,7 +5783,7 @@ version = "0.22.27"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "41fe8c660ae4257887cf66394862d21dbca4a6ddd26f04a3560410406a2f819a"
 dependencies = [
- "indexmap 2.11.4",
+ "indexmap 2.12.0",
  "serde",
  "serde_spanned",
  "toml_datetime 0.6.11",
@@ -5741,7 +5797,7 @@ version = "0.23.7"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "6485ef6d0d9b5d0ec17244ff7eb05310113c3f316f2d14200d4de56b3cb98f8d"
 dependencies = [
- "indexmap 2.11.4",
+ "indexmap 2.12.0",
  "toml_datetime 0.7.3",
  "toml_parser",
  "winnow 0.7.13",
@@ -5864,7 +5920,7 @@ version = "0.6.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "adc82fd73de2a9722ac5da747f12383d2bfdb93591ee6c58486e0097890f05f2"
 dependencies = [
- "bitflags 2.9.4",
+ "bitflags 2.10.0",
  "bytes",
  "futures-util",
  "http 1.3.1",
@@ -5920,7 +5976,7 @@ checksum = "81383ab64e72a7a8b8e13130c49e3dab29def6d0c7d76a03087b3cf71c5c6903"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
@@ -6031,6 +6087,21 @@ dependencies = [
  "url",
 ]
 
+[[package]]
+name = "typeid_prefix"
+version = "1.1.1-beta.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "257608c6fd0cbb5a8e00fe11ef14e9c285eb02f9e29624aaaba79e59a829a9e2"
+
+[[package]]
+name = "typeid_suffix"
+version = "1.2.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "8d46b723d74f5ede0160048deba99670a898b7905682a7a77be7cf8e8b75df50"
+dependencies = [
+ "uuid",
+]
+
 [[package]]
 name = "typenum"
 version = "1.19.0"
@@ -6045,9 +6116,9 @@ checksum = "eaea85b334db583fe3274d12b4cd1880032beab409c0d774be044d4480ab9a94"
 
 [[package]]
 name = "unicode-ident"
-version = "1.0.19"
+version = "1.0.20"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f63a545481291138910575129486daeaf8ac54aee4387fe7906919f7830c7d9d"
+checksum = "462eeb75aeb73aea900253ce739c8e18a67423fadf006037cd3ff27e82748a06"
 
 [[package]]
 name = "unicode-width"
@@ -6103,8 +6174,11 @@ version = "1.18.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "2f87b8aa10b915a06587d0dec516c282ff295b475d94abf425d62b57710070a2"
 dependencies = [
+ "atomic",
  "getrandom 0.3.4",
  "js-sys",
+ "md-5",
+ "sha1_smol",
  "wasm-bindgen",
 ]
 
@@ -6176,7 +6250,7 @@ dependencies = [
  "log",
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
  "wasm-bindgen-shared",
 ]
 
@@ -6211,7 +6285,7 @@ checksum = "9f07d2f20d4da7b26400c9f4a0511e6e0345b040694e8a75bd41d578fa4421d7"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
  "wasm-bindgen-backend",
  "wasm-bindgen-shared",
 ]
@@ -6363,7 +6437,7 @@ checksum = "9107ddc059d5b6fbfbffdfa7a7fe3e22a226def0b2608f72e9d552763d3e1ad7"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
@@ -6374,7 +6448,7 @@ checksum = "053e2e040ab57b9dc951b72c264860db7eb3b0200ba345b4e4c3b14f67855ddf"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
@@ -6385,7 +6459,7 @@ checksum = "29bee4b38ea3cde66011baa44dba677c432a78593e202392d1e9070cf2a7fca7"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
@@ -6396,7 +6470,7 @@ checksum = "3f316c4a2570ba26bbec722032c4099d8c8bc095efccdc15688708623367e358"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
@@ -6728,7 +6802,7 @@ checksum = "38da3c9736e16c5d3c8c597a9aaa5d1fa565d0532ae05e27c24aa62fb32c0ab6"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
  "synstructure",
 ]
 
@@ -6749,7 +6823,7 @@ checksum = "88d2b8d9c68ad2b9e4340d7832716a4d21a22a1154777ad56ea55c51a9cf3831"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
@@ -6769,7 +6843,7 @@ checksum = "d71e5d6e06ab090c67b5e44993ec16b72dcbaabc526db883a360057678b48502"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
  "synstructure",
 ]
 
@@ -6790,7 +6864,7 @@ checksum = "ce36e65b0d2999d2aafac989fb249189a141aee1f53c612c1f37d72631959f69"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
@@ -6823,7 +6897,7 @@ checksum = "5b96237efa0c878c64bd89c436f661be4e46b2f3eff1ebb976f7ef2321d2f58f"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.106",
+ "syn 2.0.107",
 ]
 
 [[package]]
```

### crates/cuslop/Cargo.toml
```diff
@@ -13,7 +13,7 @@ sp1-cuda = { workspace = true }
 sp1-core-machine = { workspace = true }
 sp1-hypercube = { workspace = true }
 sp1-core-executor = { workspace = true }
-sp1-prover = { workspace = true, features = ["unsound"] }
+sp1-prover = { workspace = true, features = ["experimental"] }
 sp1-primitives = { workspace = true }
 csl-prover = { workspace = true }
 csl-cuda = { workspace = true }
```

### crates/perf/Cargo.toml
```diff
@@ -13,7 +13,7 @@ csl-prover = { workspace = true }
 csl-tracing = { workspace = true }
 sp1-core-machine = { workspace = true }
 sp1-core-executor = { workspace = true }
-sp1-prover = { workspace = true, features = ["unsound"] }
+sp1-prover = { workspace = true, features = ["experimental"] }
 
 
 csv = "1.3.0"
```

### crates/prover-clean/Cargo.toml
```diff
@@ -52,7 +52,7 @@ rayon = "1.10.0"
 [dev-dependencies]
 serial_test = "3.1"
 zstd = "0.13.3"
-sp1-sdk = { workspace = true, features = ["unsound"] }
+sp1-sdk = { workspace = true, features = ["experimental"] }
 sp1-recursion-circuit = { workspace = true }
 
 [[bin]]
```

### crates/prover/Cargo.toml
```diff
@@ -22,7 +22,7 @@ slop-jagged = { workspace = true }
 sp1-hypercube = { workspace = true }
 sp1-core-machine = { workspace = true }
 sp1-core-executor = { workspace = true }
-sp1-prover = { workspace = true, features = ["unsound"] }
+sp1-prover = { workspace = true, features = ["experimental"] }
 sp1-primitives = { workspace = true }
 
 tracing = { workspace = true }
```
