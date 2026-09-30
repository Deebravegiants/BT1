# [?] Fix cargo audit RUSTSEC-2024-0336 (#5612)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2024-04-22
Source: https://github.com/sigp/lighthouse/commit/9b5895ca8969a6b76e52e9d0e15445b2c6f69404
Type: security-commit

## Details
Fix cargo audit RUSTSEC-2024-0336 (#5612)

* replace unmaintained rust_yaml with serde_yml

* update warp

## Patch
### Cargo.lock
```diff
@@ -18,7 +18,7 @@ version = "0.3.5"
 dependencies = [
  "account_utils",
  "bls",
- "clap",
+ "clap 2.34.0",
  "clap_utils",
  "directory",
  "environment",
@@ -126,14 +126,14 @@ dependencies = [
 
 [[package]]
 name = "aes-gcm"
-version = "0.9.4"
+version = "0.9.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "df5f85a83a7d8b0442b6aa7b504b8212c1733da07b98aae43d4bc21b2cb3cdf6"
+checksum = "bc3be92e19a7ef47457b8e6f90707e12b6ac5d20c6f3866584fa3be0787d839f"
 dependencies = [
  "aead 0.4.3",
  "aes 0.7.5",
  "cipher 0.3.0",
- "ctr 0.8.0",
+ "ctr 0.7.0",
  "ghash 0.4.4",
  "subtle",
 ]
@@ -148,15 +148,15 @@ dependencies = [
  "aes 0.8.4",
  "cipher 0.4.4",
  "ctr 0.9.2",
- "ghash 0.5.0",
+ "ghash 0.5.1",
  "subtle",
 ]
 
 [[package]]
 name = "ahash"
-version = "0.8.10"
+version = "0.8.11"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8b79b82693f705137f8fb9b37871d99e4f9a7df12b917eed79c3d3954830a60b"
+checksum = "e89da841a80418a9b391ebaea17f5c112ffaaa96f621d2c285b5174da76b9011"
 dependencies = [
  "cfg-if",
  "once_cell",
@@ -166,18 +166,18 @@ dependencies = [
 
 [[package]]
 name = "aho-corasick"
-version = "1.1.2"
+version = "1.1.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b2969dcb958b36655471fc61f7e416fa76033bdd4bfed0678d8fee1e2d07a1f0"
+checksum = "8e60d3430d3a69478ad0993f19238d2df97c507009a52b3c10addcd7f6bcb916"
 dependencies = [
  "memchr",
 ]
 
 [[package]]
 name = "allocator-api2"
-version = "0.2.16"
+version = "0.2.18"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0942ffc6dcaadf03badf6e6a2d0228460359d5e34b57ccdc720b7382dfbd5ec5"
+checksum = "5c6cb57a04249c6480766f7f7cef5467412af1490f8d1e243141daddada3264f"
 
 [[package]]
 name = "alloy-consensus"
@@ -265,7 +265,7 @@ checksum = "1a047897373be4bbb0224c1afdabca92648dc57a9c9ef6e7b0be3aff7a859c83"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.52",
+ "syn 2.0.60",
 ]
 
 [[package]]
@@ -292,11 +292,59 @@ dependencies = [
  "winapi",
 ]
 
+[[package]]
+name = "anstream"
+version = "0.6.13"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "d96bd03f33fe50a863e394ee9718a706f988b9079b20c3784fb726e7678b62fb"
+dependencies = [
+ "anstyle",
+ "anstyle-parse",
+ "anstyle-query",
+ "anstyle-wincon",
+ "colorchoice",
+ "utf8parse",
+]
+
+[[package]]
+name = "anstyle"
+version = "1.0.6"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "8901269c6307e8d93993578286ac0edf7f195079ffff5ebdeea6a59ffb7e36bc"
+
+[[package]]
+name = "anstyle-parse"
+version = "0.2.3"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "c75ac65da39e5fe5ab759307499ddad880d724eed2f6ce5b5e8a26f4f387928c"
+dependencies = [
+ "utf8parse",
+]
+
+[[package]]
+name = "anstyle-query"
+version = "1.0.2"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "e28923312444cdd728e4738b3f9c9cac739500909bb3d3c94b43551b16517648"
+dependencies = [
+ "windows-sys 0.52.0",
+]
+
+[[package]]
+name = "anstyle-wincon"
+version = "3.0.2"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "1cd54b81ec8d6180e24654d0b371ad22fc3dd083b6ff8ba325b72e00c87660a7"
+dependencies = [
+ "anstyle",
+ "windows-sys 0.52.0",
+]
+
 [[package]]
 name = "anyhow"
-version = "1.0.80"
+version = "1.0.82"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5ad32ce52e4161730f7098c077cd2ed6229b5804ccf99e5366be1ab72a98b4e1"
+checksum = "f538837af36e6f6a9be0faa67f9a314f8119e4e4b5867c6ab40ed60360142519"
 
 [[package]]
 name = "arbitrary"
@@ -309,9 +357,9 @@ dependencies = [
 
 [[package]]
 name = "arc-swap"
-version = "1.6.0"
+version = "1.7.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "bddcadddf5e9015d310179a59bb28c4d4b9920ad0f11e8e14dbadf654890c9a6"
+checksum = "69f7f8c3906b62b754cd5326047894316021dcfe5a194c8ea52bdd94934a3457"
 
 [[package]]
 name = "ark-ff"
@@ -507,9 +555,9 @@ dependencies = [
 
 [[package]]
 name = "async-io"
-version = "2.3.1"
+version = "2.3.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8f97ab0c5b00a7cdbe5a371b9a782ee7be1316095885c8a4ea1daf490eb0ef65"
+checksum = "dcccb0f599cfa2f8ace422d3555572f47424da5648a4382a9dd0310ff8210884"
 dependencies = [
  "async-lock",
  "cfg-if",
@@ -518,7 +566,7 @@ dependencies = [
  "futures-lite",
  "parking",
  "polling",
- "rustix 0.38.31",
+ "rustix 0.38.33",
  "slab",
  "tracing",
  "windows-sys 0.52.0",
@@ -537,13 +585,13 @@ dependencies = [
 
 [[package]]
 name = "async-trait"
-version = "0.1.77"
+version = "0.1.80"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c980ee35e870bd1a4d2c8294d4c04d0499e67bca1e4b5cefcc693c2fa00caea9"
+checksum = "c6fa2087f2753a7da8cc1c0dbfcf89579dd57458e36769de5ac750b4671737ca"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.52",
+ "syn 2.0.60",
 ]
 
 [[package]]
@@ -589,7 +637,7 @@ version = "0.24.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "8d9a9bf8b79a749ee0b911b91b671cc2b6c670bdbc7e3dfd537576ddc94bb2a2"
 dependencies = [
- "http 0.2.11",
+ "http 0.2.12",
  "log",
  "url",
 ]
@@ -613,29 +661,29 @@ checksum = "3c87f3f15e7794432337fc718554eaa4dc8f04c9677a950ffe366f20a162ae42"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.52",
+ "syn 2.0.60",
 ]
 
 [[package]]
 name = "autocfg"
-version = "1.1.0"
+version = "1.2.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d468802bab17cbc0cc575e9b053f41e72aa36bfa6b7f55e3529ffa43161b97fa"
+checksum = "f1fdabc7756949593fe60f30ec81974b613357de856987752631dea1e3394c80"
 
 [[package]]
 name = "axum"
-version = "0.7.4"
+version = "0.7.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1236b4b292f6c4d6dc34604bb5120d85c3fe1d1aa596bd5cc52ca054d13e7b9e"
+checksum = "3a6c9af12842a67734c9a2e355436e5d03b22383ed60cf13cd0c18fbfe3dcbcf"
 dependencies = [
  "async-trait",
  "axum-core",
  "bytes",
  "futures-util",
- "http 1.0.0",
+ "http 1.1.0",
  "http-body 1.0.0",
  "http-body-util",
- "hyper 1.2.0",
+ "hyper 1.3.1",
  "hyper-util",
  "itoa",
  "matchit",
@@ -648,7 +696,7 @@ dependencies = [
  "serde_json",
  "serde_path_to_error",
  "serde_urlencoded",
- "sync_wrapper",
+ "sync_wrapper 1.0.1",
  "tokio",
  "tower",
  "tower-layer",
@@ -665,23 +713,23 @@ dependencies = [
  "async-trait",
  "bytes",
  "futures-util",
- "http 1.0.0",
+ "http 1.1.0",
  "http-body 1.0.0",
  "http-body-util",
  "mime",
  "pin-project-lite",
  "rustversion",
- "sync_wrapper",
+ "sync_wrapper 0.1.2",
  "tower-layer",
  "tower-service",
  "tracing",
 ]
 
 [[package]]
 name = "backtrace"
-version = "0.3.69"
+version = "0.3.71"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "2089b7e3f35b9dd2d0ed921ead4f6d318c27680d4a5bd167b3ee120edb105837"
+checksum = "26b05800d2e817c8b3b4b54abd461726265fa9789ae34330622f2db9ee696f9d"
 dependencies = [
  "addr2line",
  "cc",
@@ -722,6 +770,12 @@ version = "0.21.7"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "9d297deb1925b89f2ccc13d7635fa0714f12c87adce1c75356b39ca9b7178567"
 
+[[package]]
+name = "base64"
+version = "0.22.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "9475866fec1451be56a3c2400fd081ff546538961565ccb5b7142cbd22bc7a51"
+
 [[package]]
 name = "base64ct"
 version = "1.6.0"
@@ -793,7 +847,7 @@ name = "beacon_node"
 version = "5.1.3"
 dependencies = [
  "beacon_chain",
- "clap",
+ "clap 2.34.0",
  "clap_utils",
  "client",
  "directory",
@@ -806,7 +860,7 @@ dependencies = [
  "genesis",
  "hex",
  "http_api",
- "hyper 1.2.0",
+ "hyper 1.3.1",
  "lighthouse_network",
  "lighthouse_version",
  "monitoring_api",
@@ -900,9 +954,9 @@ checksum = "bef38d45163c2f1dde094a7dfd33ccf595c92905c8f8f4fdc18d06fb1037718a"
 
 [[package]]
 name = "bitflags"
-version = "2.4.2"
+version = "2.5.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "ed570934406eb16438a4e976b1b4500774099c13b8cb96eec99f620f05090ddf"
+checksum = "cf4b9d6a944f767f8e5e0db018570623c85f3d925ac718db4e06d0187adb21c1"
 
 [[package]]
 name = "bitvec"
@@ -1006,7 +1060,7 @@ name = "boot_node"
 version = "5.1.3"
 dependencies = [
  "beacon_node",
- "clap",
+ "clap 2.34.0",
  "clap_utils",
  "eth2_network_config",
  "ethereum_ssz",
@@ -1034,9 +1088,9 @@ checksum = "771fe0050b883fcc3ea2359b1a96bcfbc090b7116eae7c3c512c7a083fdf23d3"
 
 [[package]]
 name = "bs58"
-version = "0.5.0"
+version = "0.5.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f5353f36341f7451062466f0b755b96ac3a9547e4d7f6b70d603fc721a7d7896"
+checksum = "bf88ba1141d185c399bee5288d850d63b8369520c1eafc32a0430b5b6c287bf4"
 dependencies = [
  "tinyvec",
 ]
@@ -1055,9 +1109,9 @@ dependencies = [
 
 [[package]]
 name = "bumpalo"
-version = "3.15.3"
+version = "3.16.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8ea184aa71bb362a1157c896979544cc23974e08fd265f29ea96b59f0b4a555b"
+checksum = "79296716171880943b8470b5f8d03aa55eb2e645a4874bdbb28adb49162e012c"
 
 [[package]]
 name = "byte-slice-cast"
@@ -1073,9 +1127,9 @@ checksum = "1fd0f2584146f6f2ef48085050886acf353beff7305ebd1ae69500e27c67f64b"
 
 [[package]]
 name = "bytes"
-version = "1.5.0"
+version = "1.6.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a2bd12c1caf447e69cd4528f47f94d203fd2582878ecb9e9465484c4148a8223"
+checksum = "514de17de45fdb8dc022b1a7975556c53c86f9f0aa5f534b98977b171857c2c9"
 dependencies = [
  "serde",
 ]
@@ -1141,9 +1195,9 @@ dependencies = [
 
 [[package]]
 name = "cargo-platform"
-version = "0.1.7"
+version = "0.1.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "694c8807f2ae16faecc43dc17d74b3eb042482789fd0eb64b39a2e04e087053f"
+checksum = "24b1f0365a6c6bb4020cd05806fd0d33c44d38046b8bd7f0e40814b9763cabfc"
 dependencies = [
  "serde",
 ]
@@ -1170,12 +1224,13 @@ checksum = "37b2a672a2cb129a2e41c10b1224bb368f9f37a2b16b612598138befd7b37eb5"
 
 [[package]]
 name = "cc"
-version = "1.0.90"
+version = "1.0.95"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8cd6604a82acf3039f1144f54b8eb34e91ffba622051189e71b781822d5ee1f5"
+checksum = "d32a725bc159af97c3e629873bb9f88fb8cf8a4867175f76dc987815ea07c83b"
 dependencies = [
  "jobserver",
  "libc",
+ "once_cell",
 ]
 
 [[package]]
@@ -1193,6 +1248,12 @@ version = "1.0.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "baf1de4339761588bc0619e3cbc0120ee582ebb74b53b4efbf79117bd2da40fd"
 
+[[package]]
+name = "cfg_aliases"
+version = "0.1.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "fd16c4719339c4530435d38e511904438d07cce7950afa3718a84ac36c10e89e"
+
 [[package]]
 name = "chacha20"
 version = "0.9.1"
@@ -1219,14 +1280,14 @@ dependencies = [
 
 [[package]]
 name = "chrono"
-version = "0.4.34"
+version = "0.4.38"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5bc015644b92d5890fab7489e49d21f879d5c990186827d42ec511919404f38b"
+checksum = "a21f936df1771bf62b77f047b726c4625ff2e8aa607c01ec06e5a05bd8463401"
 dependencies = [
  "android-tzdata",
  "iana-time-zone",
  "num-traits",
- "windows-targets 0.52.4",
+ "windows-targets 0.52.5",
 ]
 
 [[package]]
@@ -1275,11 +1336,38 @@ dependencies = [
  "vec_map",
 ]
 
+[[package]]
+name = "clap"
+version = "4.5.4"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "90bc066a67923782aa8515dbaea16946c5bcc5addbd668bb80af688e53e548a0"
+dependencies = [
+ "clap_builder",
+]
+
+[[package]]
+name = "clap_builder"
+version = "4.5.2"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "ae129e2e766ae0ec03484e609954119f123cc1fe650337e155d03b022f24f7b4"
+dependencies = [
+ "anstream",
+ "anstyle",
+ "clap_lex",
+ "strsim 0.11.1",
+]
+
+[[package]]
+name = "clap_lex"
+version = "0.7.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "98cc8fbded0c607b7ba9dd60cd98df59af97e84d24e49c8557331cfc26d301ce"
+
 [[package]]
 name = "clap_utils"
 version = "0.1.0"
 dependencies = [
- "clap",
+ "clap 2.34.0",
  "dirs",
  "eth2_network_config",
  "ethereum-types 0.14.1",
@@ -1344,6 +1432,12 @@ dependencies = [
  "cc",
 ]
 
+[[package]]
+name = "colorchoice"
+version = "1.0.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "acbf1af155f9b9ef647e42cdc158db4b64a1b61f743629225fde6f3e0be2a7c7"
+
 [[package]]
 name = "compare_fields"
 version = "0.2.0"
@@ -1369,11 +1463,24 @@ dependencies = [
  "crossbeam-utils",
 ]
 
+[[package]]
+name = "console"
+version = "0.15.8"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "0e1f83fc076bd6dd27517eacdf25fef6c4dfe5f1d7448bafaaf3a26f13b5e4eb"
+dependencies = [
+ "encode_unicode",
+ "lazy_static",
+ "libc",
+ "unicode-width",
+ "windows-sys 0.52.0",
+]
+
 [[package]]
 name = "const-hex"
-version = "1.11.1"
+version = "1.11.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "efbd12d49ab0eaf8193ba9175e45f56bbc2e4b27d57b8cfe62aa47942a46b9a9"
+checksum = "5ba00838774b4ab0233e355d26710fbfc8327a05c017f6dc4873f876d1f79f78"
 dependencies = [
  "cfg-if",
  "cpufeatures",
@@ -1451,7 +1558,7 @@ checksum = "b01d6de93b2b6c65e17c634a26653a29d107b3c98c607c765bf38d041531cd8f"
 dependencies = [
  "atty",
  "cast",
- "clap",
+ "clap 2.34.0",
  "criterion-plot",
  "csv",
  "itertools",
@@ -1566,9 +1673,9 @@ dependencies = [
 
 [[package]]
 name = "crypto-mac"
-version = "0.11.1"
+version = "0.11.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b1d1a86f49236c215f271d40892d5fc950490551400b02ef360692c29815c714"
+checksum = "25fab6889090c8133f3deb8f73ba3c65a7f456f66436fc012a1b1e272b1e103e"
 dependencies = [
  "generic-array",
  "subtle",
@@ -1595,6 +1702,15 @@ dependencies = [
  "memchr",
 ]
 
+[[package]]
+name = "ctr"
+version = "0.7.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "a232f92a03f37dd7d7dd2adc67166c77e9cd88de5b019b9a9eecfaeaf7bfd481"
+dependencies = [
+ "cipher 0.3.0",
+]
+
 [[package]]
 name = "ctr"
 version = "0.8.0"
@@ -1615,11 +1731,11 @@ dependencies = [
 
 [[package]]
 name = "ctrlc"
-version = "3.4.2"
+version = "3.4.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b467862cc8610ca6fc9a1532d7777cee0804e678ab45410897b9396495994a0b"
+checksum = "672465ae37dc1bc6380a6547a8883d5dd397b0f1faaad4f265726cc7042a5345"
 dependencies = [
- "nix 0.27.1",
+ "nix 0.28.0",
  "windows-sys 0.52.0",
 ]
 
@@ -1634,7 +1750,7 @@ dependencies = [
  "curve25519-dalek-derive",
  "digest 0.10.7",
  "fiat-crypto",
- "platforms 3.3.0",
+ "platforms 3.4.0",
  "rustc_version 0.4.0",
  "subtle",
  "zeroize",
@@ -1648,7 +1764,7 @@ checksum = "f46882e17999c6cc590af592290432be3bce0428cb0d5f8b6715e4dc7b383eb3"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.52",
+ "syn 2.0.60",
 ]
 
 [[package]]
@@ -1657,8 +1773,18 @@ version = "0.13.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "a01d95850c592940db9b8194bc39f4bc0e89dee5c4265e4b1807c34a9aba453c"
 dependencies = [
- "darling_core",
- "darling_macro",
+ "darling_core 0.13.4",
+ "darling_macro 0.13.4",
+]
+
+[[package]]
+name = "darling"
+version = "0.14.4"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "7b750cb3417fd1b327431a470f388520309479ab0bf5e323505daf0290cd3850"
+dependencies = [
+ "darling_core 0.14.4",
+ "darling_macro 0.14.4",
 ]
 
 [[package]]
@@ -1675,13 +1801,38 @@ dependencies = [
  "syn 1.0.109",
 ]
 
+[[package]]
+name = "darling_core"
+version = "0.14.4"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "109c1ca6e6b7f82cc233a97004ea8ed7ca123a9af07a8230878fcfda9b158bf0"
+dependencies = [
+ "fnv",
+ "ident_case",
+ "proc-macro2",
+ "quote",
+ "strsim 0.10.0",
+ "syn 1.0.109",
+]
+
 [[package]]
 name = "darling_macro"
 version = "0.13.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "9c972679f83bdf9c42bd905396b6c3588a843a17f0f16dfcfa3e2c5d57441835"
 dependencies = [
- "darling_core",
+ "darling_core 0.13.4",
+ "quote",
+ "syn 1.0.109",
+]
+
+[[package]]
+name = "darling_macro"
+version = "0.14.4"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "a4aab4dbc9f7611d8b55048a3a16d2d010c2c8334e46304b40ac1cc14bf3b48e"
+dependencies = [
+ "darling_core 0.14.4",
  "quote",
  "syn 1.0.109",
 ]
@@ -1744,7 +1895,7 @@ version = "0.1.0"
 dependencies = [
  "beacon_chain",
  "beacon_node",
- "clap",
+ "clap 2.34.0",
  "clap_utils",
  "environment",
  "hex",
@@ -1799,9 +1950,9 @@ dependencies = [
 
 [[package]]
 name = "der"
-version = "0.7.8"
+version = "0.7.9"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "fffa369a668c8af7dbf8b5e56c9f744fbd399949ed171606040001947de40b1c"
+checksum = "f55bf8e7b65898637379c1b74eb1551107c8294ed26d855ceb9fd1a09cfc9bc0"
 dependencies = [
  "const-oid",
  "pem-rfc7468",
@@ -1850,7 +2001,38 @@ checksum = "67e77553c4162a157adbf834ebae5b415acbecbeafc7a74b0e886657506a7611"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.52",
+ "syn 2.0.60",
+]
+
+[[package]]
+name = "derive_builder"
+version = "0.12.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "8d67778784b508018359cbc8696edb3db78160bab2c2a28ba7f56ef6932997f8"
+dependencies = [
+ "derive_builder_macro",
+]
+
+[[package]]
+name = "derive_builder_core"
+version = "0.12.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "c11bdc11a0c47bc7d37d582b5285da6849c96681023680b906673c5707af7b0f"
+dependencies = [
+ "darling 0.14.4",
+ "proc-macro2",
+ "quote",
+ "syn 1.0.109",
+]
+
+[[package]]
+name = "derive_builder_macro"
+version = "0.12.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "ebcda35c7a396850a55ffeac740804b40ffec779b98fffbb1738f4033f0ee79e"
+dependencies = [
+ "derive_builder_core",
+ "syn 1.0.109",
 ]
 
 [[package]]
@@ -1866,13 +2048,26 @@ dependencies = [
  "syn 1.0.109",
 ]
 
+[[package]]
+name = "dialoguer"
+version = "0.11.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "658bce805d770f407bc62102fca7c2c64ceef2fbcb2b8bd19d2765ce093980de"
+dependencies = [
+ "console",
+ "shell-words",
+ "tempfile",
+ "thiserror",
+ "zeroize",
+]
+
 [[package]]
 name = "diesel"
-version = "2.1.4"
+version = "2.1.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "62c6fcf842f17f8c78ecf7c81d75c5ce84436b41ee07e03f490fbb5f5a8731d8"
+checksum = "ff236accb9a5069572099f0b350a92e9560e8e63a9b8d546162f4a5e03026bb2"
 dependencies = [
- "bitflags 2.4.2",
+ "bitflags 2.5.0",
  "byteorder",
  "diesel_derives",
  "itoa",
@@ -1882,14 +2077,14 @@ dependencies = [
 
 [[package]]
 name = "diesel_derives"
-version = "2.1.2"
+version = "2.1.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "ef8337737574f55a468005a83499da720f20c65586241ffea339db9ecdfd2b44"
+checksum = "14701062d6bed917b5c7103bdffaee1e4609279e240488ad24e7bd979ca6866c"
 dependencies = [
  "diesel_table_macro_syntax",
  "proc-macro2",
  "quote",
- "syn 2.0.52",
+ "syn 2.0.60",
 ]
 
 [[package]]
@@ -1909,7 +2104,7 @@ version = "0.1.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "fc5557efc453706fed5e4fa85006fe9817c224c3f480a34c7e5959fd700921c5"
 dependencies = [
- "syn 2.0.52",
+ "syn 2.0.60",
 ]
 
 [[package]]
@@ -1937,7 +2132,7 @@ dependencies = [
 name = "directory"
 version = "0.1.0"
 dependencies = [
- "clap",
+ "clap 2.34.0",
  "clap_utils",
  "eth2_network_config",
 ]
@@ -1990,7 +2185,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "bac33cb3f99889a57e56a8c6ccb77aaf0cfc7787602b7af09783f736d77314e1"
 dependencies = [
  "aes 0.7.5",
- "aes-gcm 0.9.4",
+ "aes-gcm 0.9.2",
  "arrayvec",
  "delay_map",
  "enr",
@@ -2022,7 +2217,7 @@ checksum = "487585f4d0c6655fe74905e2504d8ad6908e4db67f744eb140876906c2f3175d"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.52",
+ "syn 2.0.60",
 ]
 
 [[package]]
@@ -2031,6 +2226,29 @@ version = "1.0.9"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "dcbb2bf8e87535c23f7a8a321e364ce21462d0ff10cb6407820e8e96dfff6653"
 
+[[package]]
+name = "dtt"
+version = "0.0.5"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "d6b2dd9ee2d76888dc4c17d6da74629fa11b3cb1e8094fdc159b7f8ff259fc88"
+dependencies = [
+ "regex",
+ "serde",
+ "time",
+]
+
+[[package]]
+name = "duct"
+version = "0.13.7"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "e4ab5718d1224b63252cd0c6f74f6480f9ffeb117438a2e0f5cf6d9a4798929c"
+dependencies = [
+ "libc",
+ "once_cell",
+ "os_pipe",
+ "shared_child",
+]
+
 [[package]]
 name = "dunce"
 version = "1.0.4"
@@ -2055,7 +2273,7 @@ version = "0.16.9"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "ee27f32b5c5292967d2d4a9d7f1e0b0aed2c15daded5a60300e4abb9d8020bca"
 dependencies = [
- "der 0.7.8",
+ "der 0.7.9",
  "digest 0.10.7",
  "elliptic-curve 0.13.8",
  "rfc6979 0.4.0",
@@ -2125,9 +2343,9 @@ dependencies = [
 
 [[package]]
 name = "either"
-version = "1.10.0"
+version = "1.11.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "11157ac094ffbdde99aa67b23417ebdd801842852b500e395a45a9c0aac03e4a"
+checksum = "a47c1c47d2f5964e29c61246e81db715514cd532db6b5116a25ea3c03d6780a2"
 
 [[package]]
 name = "elliptic-curve"
@@ -2168,11 +2386,17 @@ dependencies = [
  "zeroize",
 ]
 
+[[package]]
+name = "encode_unicode"
+version = "0.3.6"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "a357d28ed41a50f9c765dbfe56cbc04a64e53e5fc58ba79fbc34c10ef3df831f"
+
 [[package]]
 name = "encoding_rs"
-version = "0.8.33"
+version = "0.8.34"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7268b386296a025e474d5140678f75d6de9493ae55a5d709eeb9dd08149945e1"
+checksum = "b45de904aa0b010bce2ab45264d0631681847fa7b6f2eaa7dab7619943bc4f59"
 dependencies = [
  "cfg-if",
 ]
@@ -2205,7 +2429,17 @@ dependencies = [
  "heck",
  "proc-macro2",
  "quote",
- "syn 2.0.52",
+ "syn 2.0.60",
+]
+
+[[package]]
+name = "env_filter"
+version = "0.1.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "a009aa4810eb158359dda09d0c87378e4bbb89b5a801f016885a4707ba24f7ea"
+dependencies = [
+ "log",
+ "regex",
 ]
 
 [[package]]
@@ -2231,6 +2465,19 @@ dependencies = [
  "termcolor",
 ]
 
+[[package]]
+name = "env_logger"
+version = "0.11.3"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "38b35839ba51819680ba087cd351788c9a3c476841207e0b8cee0b04722343b9"
+dependencies = [
+ "anstream",
+ "anstyle",
+ "env_filter",
+ "humantime",
+ "log",
+]
+
 [[package]]
 name = "environment"
 version = "0.1.2"
@@ -2418,7 +2665,7 @@ dependencies = [
  "sha2 0.9.9",
  "tempfile",
  "unicode-normalization",
- "uuid",
+ "uuid 0.8.2",
  "zeroize",
 ]
 
@@ -2458,7 +2705,7 @@ dependencies = [
  "serde_repr",
  "tempfile",
  "tiny-bip39",
- "uuid",
+ "uuid 0.8.2",
 ]
 
 [[package]]
@@ -2602,7 +2849,7 @@ version = "0.5.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "6085d7fd3cf84bd2b8fec150d54c8467fb491d8db9c460607c5534f653a0ee38"
 dependencies = [
- "darling",
+ "darling 0.13.4",
  "proc-macro2",
  "quote",
  "syn 1.0.109",
@@ -2712,7 +2959,7 @@ dependencies = [
  "getrandom",
  "hashers",
  "hex",
- "http 0.2.11",
+ "http 0.2.12",
  "once_cell",
  "parking_lot 0.11.2",
  "pin-project",
@@ -2858,9 +3105,9 @@ checksum = "7360491ce676a36bf9bb3c56c1aa791658183a54d2744120f27285738d90465a"
 
 [[package]]
 name = "fastrand"
-version = "2.0.1"
+version = "2.0.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "25cbce373ec4653f1a01a31e8a5e5ec0c622dc27ff9c4e6606eefef5cbbed4a5"
+checksum = "658bd65b1cf4c852a3cc96f18a8ce7b5640f6b703f905c7d74532294c2a63984"
 
 [[package]]
 name = "fastrlp"
@@ -2901,9 +3148,9 @@ checksum = "ec54ac60a7f2ee9a97cad9946f9bf629a3bc6a7ae59e68983dc9318f5a54b81a"
 
 [[package]]
 name = "fiat-crypto"
-version = "0.2.6"
+version = "0.2.7"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1676f435fc1dadde4d03e43f5d62b259e1ce5f40bd4ffb21db2b42ebe59c1382"
+checksum = "c007b1ae3abe1cb6f85a16305acd418b7ca6343b953633fee2b76d8f108b830f"
 
 [[package]]
 name = "field-offset"
@@ -2915,6 +3162,12 @@ dependencies = [
  "rustc_version 0.4.0",
 ]
 
+[[package]]
+name = "figlet-rs"
+version = "0.1.5"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "4742a071cd9694fc86f9fa1a08fa3e53d40cc899d7ee532295da2d085639fbc5"
+
 [[package]]
 name = "filesystem"
 version = "0.1.0"
@@ -3020,6 +3273,12 @@ dependencies = [
  "winapi",
 ]
 
+[[package]]
+name = "fs_extra"
+version = "1.3.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "42703706b716c37f96a77aea830392ad231f44c9e9a67872fa5548707e11b11c"
+
 [[package]]
 name = "funty"
 version = "1.1.0"
@@ -3093,9 +3352,9 @@ checksum = "a44623e20b9681a318efdd71c299b6b222ed6f231972bfe2f224ebad6311f0c1"
 
 [[package]]
 name = "futures-lite"
-version = "2.2.0"
+version = "2.3.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "445ba825b27408685aaecefd65178908c36c6e96aaf6d8599419d46e624192ba"
+checksum = "52527eb5074e35e9339c6b4e8d12600c7128b68fb25dcb9fa9dec18f7c25f3a5"
 dependencies = [
  "futures-core",
  "pin-project-lite",
@@ -3109,7 +3368,7 @@ checksum = "87750cf4b7a4c0625b1529e4c543c2182106e4dedc60a2a6455e00d212c489ac"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.52",
+ "syn 2.0.60",
 ]
 
 [[package]]
@@ -3119,7 +3378,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "35bd3cf68c183738046838e300353e4716c674dc5e56890de4826801a6622a28"
 dependencies = [
  "futures-io",
- "rustls",
+ "rustls 0.21.11",
 ]
 
 [[package]]
@@ -3212,9 +3471,9 @@ dependencies = [
 
 [[package]]
 name = "getrandom"
-version = "0.2.12"
+version = "0.2.14"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "190092ea657667030ac6a35e305e62fc4dd69fd98ac98631e5d3a2b1575a12b5"
+checksum = "94b22e06ecb0110981051723910cbf0b5f5e09a2062dd7663334ee79a9d1286c"
 dependencies = [
  "cfg-if",
  "js-sys",
@@ -3235,12 +3494,12 @@ dependencies = [
 
 [[package]]
 name = "ghash"
-version = "0.5.0"
+version = "0.5.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d930750de5717d2dd0b8c0d42c076c0e884c81a73e6cab859bbd2339c71e3e40"
+checksum = "f0d8a4362ccb29cb0b265253fb0a2728f592895ee6854fd9bc13f2ffda266ff1"
 dependencies = [
  "opaque-debug",
- "polyval 0.6.1",
+ "polyval 0.6.2",
 ]
 
 [[package]]
@@ -3266,7 +3525,7 @@ checksum = "53010ccb100b96a67bc32c0175f0ed1426b31b655d562898e57325f81c023ac0"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.52",
+ "syn 2.0.60",
 ]
 
 [[package]]
@@ -3339,27 +3598,8 @@ dependencies = [
  "futures-core",
  "futures-sink",
  "futures-util",
- "http 0.2.11",
- "indexmap 2.2.5",
- "slab",
- "tokio",
- "tokio-util 0.7.10",
- "tracing",
-]
-
-[[package]]
-name = "h2"
-version = "0.4.4"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "816ec7294445779408f36fe57bc5b7fc1cf59664059096c65f905c1c61f58069"
-dependencies = [
- "bytes",
- "fnv",
- "futures-core",
- "futures-sink",
- "futures-util",
- "http 1.0.0",
- "indexmap 2.2.5",
+ "http 0.2.12",
+ "indexmap 2.2.6",
  "slab",
  "tokio",
  "tokio-util 0.7.10",
@@ -3439,7 +3679,7 @@ dependencies = [
  "base64 0.21.7",
  "bytes",
  "headers-core",
- "http 0.2.11",
+ "http 0.2.12",
  "httpdate",
  "mime",
  "sha1",
@@ -3451,7 +3691,7 @@ version = "0.2.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "e7f66481bfee273957b1f20485a4ff3362987f85b2c236580d81b4eb7a326429"
 dependencies = [
- "http 0.2.11",
+ "http 0.2.12",
 ]
 
 [[package]]
@@ -3498,9 +3738,9 @@ checksum = "b07f60793ff0a4d9cef0f18e63b5357e06209987153a64648c972c1e5aff336f"
 
 [[package]]
 name = "hickory-proto"
-version = "0.24.0"
+version = "0.24.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "091a6fbccf4860009355e3efc52ff4acf37a63489aad7435372d44ceeb6fbbcf"
+checksum = "07698b8420e2f0d6447a436ba999ec85d8fbf2a398bbd737b82cac4a2e96e512"
 dependencies = [
  "async-trait",
  "cfg-if",
@@ -3523,9 +3763,9 @@ dependencies = [
 
 [[package]]
 name = "hickory-resolver"
-version = "0.24.0"
+version = "0.24.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "35b8f021164e6a984c9030023544c57789c51760065cd510572fedcfb04164e8"
+checksum = "28757f23aa75c98f254cf0405e6d8c25b831b32921b050a66692427679b1f243"
 dependencies = [
  "cfg-if",
  "futures-util",
@@ -3567,7 +3807,7 @@ version = "0.11.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "2a2a2320eb7ec0ebe8da8f744d7812d9fc4cb4d09344ac01898dbcb6a20ae69b"
 dependencies = [
- "crypto-mac 0.11.1",
+ "crypto-mac 0.11.0",
  "digest 0.9.0",
 ]
 
@@ -3604,9 +3844,9 @@ dependencies = [
 
 [[package]]
 name = "http"
-version = "0.2.11"
+version = "0.2.12"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8947b1a6fad4393052c7ba1f4cd97bed3e953a95c79c92ad9b051a04611d9fbb"
+checksum = "601cbb57e577e2f5ef5be8e7b83f0f63994f25aa94d673e54a92d5c516d101f1"
 dependencies = [
  "bytes",
  "fnv",
@@ -3615,9 +3855,9 @@ dependencies = [
 
 [[package]]
 name = "http"
-version = "1.0.0"
+version = "1.1.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b32afd38673a8016f7c9ae69e5af41a58f81b1d31689040f2f1959594ce194ea"
+checksum = "21b9ddb458710bc376481b842f5da65cdf31522de232c1ca8146abce2a358258"
 dependencies = [
  "bytes",
  "fnv",
@@ -3631,7 +3871,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "7ceab25649e9960c0311ea418d17bee82c0dcec1bd053b5f9a66e265a693bed2"
 dependencies = [
  "bytes",
- "http 0.2.11",
+ "http 0.2.12",
  "pin-project-lite",
 ]
 
@@ -3642,18 +3882,18 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "1cac85db508abc24a2e48553ba12a996e87244a0395ce011e62b37158745d643"
 dependencies = [
  "bytes",
- "http 1.0.0",
+ "http 1.1.0",
 ]
 
 [[package]]
 name = "http-body-util"
-version = "0.1.0"
+version = "0.1.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "41cb79eb393015dadd30fc252023adb0b2400a0caee0fa2a077e6e21a551e840"
+checksum = "0475f8b2ac86659c21b64320d5d653f9efe42acd2a4e560073ec61a155a34f1d"
 dependencies = [
  "bytes",
- "futures-util",
- "http 1.0.0",
+ "futures-core",
+ "http 1.1.0",
  "http-body 1.0.0",
  "pin-project-lite",
 ]
@@ -3754,8 +3994,8 @@ dependencies = [
  "futures-channel",
  "futures-core",
  "futures-util",
- "h2 0.3.26",
- "http 0.2.11",
+ "h2",
+ "http 0.2.12",
  "http-body 0.4.6",
  "httparse",
  "httpdate",
@@ -3770,15 +4010,14 @@ dependencies = [
 
 [[package]]
 name = "hyper"
-version = "1.2.0"
+version = "1.3.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "186548d73ac615b32a73aafe38fb4f56c0d340e110e5a200bcadbaf2e199263a"
+checksum = "fe575dd17d0862a9a33781c8c4696a55c320909004a67a00fb286ba8b1bc496d"
 dependencies = [
  "bytes",
  "futures-channel",
  "futures-util",
- "h2 0.4.4",
- "http 1.0.0",
+ "http 1.1.0",
  "http-body 1.0.0",
  "httparse",
  "httpdate",
@@ -3795,11 +4034,11 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "ec3efd23720e2049821a693cbc7e65ea87c72f1c58ff2f9522ff332b1491e590"
 dependencies = [
  "futures-util",
- "http 0.2.11",
+ "http 0.2.12",
  "hyper 0.14.28",
- "rustls",
+ "rustls 0.21.11",
  "tokio",
- "tokio-rustls",
+ "tokio-rustls 0.24.1",
 ]
 
 [[package]]
@@ -3823,9 +4062,9 @@ checksum = "ca38ef113da30126bbff9cd1705f9273e15d45498615d138b0c20279ac7a76aa"
 dependencies = [
  "bytes",
  "futures-util",
- "http 1.0.0",
+ "http 1.1.0",
  "http-body 1.0.0",
- "hyper 1.2.0",
+ "hyper 1.3.1",
  "pin-project-lite",
  "socket2 0.5.6",
  "tokio",
@@ -3919,7 +4158,7 @@ dependencies = [
  "attohttpc",
  "bytes",
  "futures",
- "http 0.2.11",
+ "http 0.2.12",
  "hyper 0.14.28",
  "log",
  "rand",
@@ -4002,9 +4241,9 @@ dependencies = [
 
 [[package]]
 name = "indexmap"
-version = "2.2.5"
+version = "2.2.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7b0b929d511467233429c45a44ac1dcaa21ba0f5ba11e4879e6ed28ddb4f9df4"
+checksum = "168fb715dda47215e360912c096649d23d58bf392ac62f73919e831745e40f26"
 dependencies = [
  "equivalent",
  "hashbrown 0.14.3",
@@ -4037,7 +4276,7 @@ version = "0.2.0"
 dependencies = [
  "bytes",
  "hex",
- "yaml-rust",
+ "serde_yml",
 ]
 
 [[package]]
@@ -4067,7 +4306,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "b58db92f96b720de98181bbbe63c831e87005ab460c1bf306eb2622b4707997f"
 dependencies = [
  "socket2 0.5.6",
- "widestring 1.0.2",
+ "widestring 1.1.0",
  "windows-sys 0.48.0",
  "winreg",
 ]
@@ -4100,9 +4339,9 @@ dependencies = [
 
 [[package]]
 name = "itoa"
-version = "1.0.10"
+version = "1.0.11"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b1a46d1a171d865aa5f83f92695765caa047a9b4cbae2cbf37dbd613a793fd4c"
+checksum = "49f1f14873335454500d59611f1cf4a4b0f786f9ac11f4312a78e4cf2566695b"
 
 [[package]]
 name = "jemalloc-ctl"
@@ -4137,18 +4376,18 @@ dependencies = [
 
 [[package]]
 name = "jobserver"
-version = "0.1.28"
+version = "0.1.30"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "ab46a6e9526ddef3ae7f787c06f0f2600639ba80ea3eade3d8e670a2230f51d6"
+checksum = "685a7d121ee3f65ae4fddd72b25a04bb36b6af81bc0828f7d5434c0fe60fa3a2"
 dependencies = [
  "libc",
 ]
 
 [[package]]
 name = "js-sys"
-version = "0.3.68"
+version = "0.3.69"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "406cda4b368d531c842222cf9d2600a9a4acce8d29423695379c6868a143a9ee"
+checksum = "29c15563dc2726973df627357ce0c9ddddbea194836909d655df6a75d2cf296d"
 dependencies = [
  "wasm-bindgen",
 ]
@@ -4261,7 +4500,7 @@ dependencies = [
  "account_utils",
  "beacon_chain",
  "bls",
- "clap",
+ "clap 2.34.0",
  "clap_utils",
  "deposit_contract",
  "directory",
@@ -4349,12 +4588,12 @@ dependencies = [
 
 [[package]]
 name = "libloading"
-version = "0.8.2"
+version = "0.8.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "2caa5afb8bf9f3a2652760ce7d4f62d21c4d5a423e68466fca30df82f2330164"
+checksum = "0c2a198fb6b0eada2a8df47933734e6d35d350665a33a3593d7164fa52c75c19"
 dependencies = [
  "cfg-if",
- "windows-targets 0.52.4",
+ "windows-targets 0.52.5",
 ]
 
 [[package]]
@@ -4509,7 +4748,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "999ec70441b2fb35355076726a6bc466c932e9bdc66f6a11c6c0aa17c7ab9be0"
 dependencies = [
  "asn1_der",
- "bs58 0.5.0",
+ "bs58 0.5.1",
  "ed25519-dalek",
  "hkdf",
  "libsecp256k1",
@@ -4640,7 +4879,7 @@ dependencies = [
  "quinn",
  "rand",
  "ring 0.16.20",
- "rustls",
+ "rustls 0.21.11",
  "socket2 0.5.6",
  "thiserror",
  "tokio",
@@ -4679,7 +4918,7 @@ dependencies = [
  "heck",
  "proc-macro2",
  "quote",
- "syn 2.0.52",
+ "syn 2.0.60",
 ]
 
 [[package]]
@@ -4711,8 +4950,8 @@ dependencies = [
  "libp2p-identity",
  "rcgen",
  "ring 0.16.20",
- "rustls",
- "rustls-webpki",
+ "rustls 0.21.11",
+ "rustls-webpki 0.101.7",
  "thiserror",
  "x509-parser",
  "yasna",
@@ -4751,13 +4990,12 @@ dependencies = [
 
 [[package]]
 name = "libredox"
-version = "0.0.1"
+version = "0.1.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "85c833ca1e66078851dba29046874e38f08b2c883700aa29a03ddd3b23814ee8"
+checksum = "c0ff37bd590ca25063e35af745c343cb7a0271906fb7b37e4813e8f79f00268d"
 dependencies = [
- "bitflags 2.4.2",
+ "bitflags 2.5.0",
  "libc",
- "redox_syscall 0.4.1",
 ]
 
 [[package]]
@@ -4821,9 +5059,9 @@ dependencies = [
 
 [[package]]
 name = "libz-sys"
-version = "1.1.15"
+version = "1.1.16"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "037731f5d3aaa87a5675e895b63ddff1a87624bc29f77004ea829809654e48f6"
+checksum = "5e143b5e666b2695d28f6bca6497720813f699c9602dd7f5cac91008b8ada7f9"
 dependencies = [
  "cc",
  "pkg-config",
@@ -4840,7 +5078,7 @@ dependencies = [
  "beacon_processor",
  "bls",
  "boot_node",
- "clap",
+ "clap 2.34.0",
  "clap_utils",
  "database_manager",
  "directory",
@@ -5148,15 +5386,15 @@ checksum = "8878cd8d1b3c8c8ae4b2ba0a36652b7cf192f618a599a7fbdfa25cffd4ea72dd"
 
 [[package]]
 name = "memchr"
-version = "2.7.1"
+version = "2.7.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "523dc4f511e55ab87b694dc30d0f820d60906ef06413f93d4d7a1385599cc149"
+checksum = "6c8640c5d730cb13ebd907d8d04b52f55ac9a2eec55b440c8892f40d56c76c1d"
 
 [[package]]
 name = "memoffset"
-version = "0.9.0"
+version = "0.9.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5a634b1c61a95585bd15607c6ab0c4e5b226e695ff2800ba0cdccddf208c406c"
+checksum = "488016bfae457b036d996092f6cb448677611ce4449e970ceaf42695203f218a"
 dependencies = [
  "autocfg",
 ]
@@ -5188,7 +5426,7 @@ version = "0.1.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "37cb4045d5677b7da537f8cb5d0730d5b6414e3cc81c61e4b50e1f0cbdc73909"
 dependencies = [
- "darling",
+ "darling 0.13.4",
  "itertools",
  "proc-macro2",
  "quote",
@@ -5417,9 +5655,9 @@ dependencies = [
 
 [[package]]
 name = "netlink-sys"
-version = "0.8.5"
+version = "0.8.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6471bf08e7ac0135876a9581bf3217ef0333c191c128d34878079f42ee150411"
+checksum = "416060d346fbaf1f23f9512963e3e878f1a78e707cb699ba9215761754244307"
 dependencies = [
  "bytes",
  "futures",
@@ -5492,12 +5730,13 @@ dependencies = [
 
 [[package]]
 name = "nix"
-version = "0.27.1"
+version = "0.28.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "2eb04e9c688eff1c89d72b407f168cf79bb9e867a9d3323ed6c01519eb9cc053"
+checksum = "ab2156c4fce2f8df6c499cc1c763e4394b7482525bf2a9701c9d79d215f519e4"
 dependencies = [
- "bitflags 2.4.2",
+ "bitflags 2.5.0",
  "cfg-if",
+ "cfg_aliases",
  "libc",
 ]
 
@@ -5701,7 +5940,7 @@ version = "0.10.64"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "95a0481286a310808298130d22dd1fef0fa571e05a8f44ec801801e84b216b1f"
 dependencies = [
- "bitflags 2.4.2",
+ "bitflags 2.5.0",
  "cfg-if",
  "foreign-types",
  "libc",
@@ -5718,7 +5957,7 @@ checksum = "a948666b637a0f465e8564c73e89d4dde00d72d4d473cc972f390fc3dcee7d9c"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.52",
+ "syn 2.0.60",
 ]
 
 [[package]]
@@ -5738,9 +5977,9 @@ dependencies = [
 
 [[package]]
 name = "openssl-sys"
-version = "0.9.101"
+version = "0.9.102"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "dda2b0f344e78efc2facf7d195d098df0dd72151b26ab98da807afc26c198dff"
+checksum = "c597637d56fbc83893a35eb0dd04b2b8e7a50c91e64e9493e398b5df4fb45fa2"
 dependencies = [
  "cc",
  "libc",
@@ -5772,6 +6011,16 @@ dependencies = [
  "types",
 ]
 
+[[package]]
+name = "os_pipe"
+version = "1.1.5"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "57119c3b893986491ec9aa85056780d3a0f3cf4da7cc09dd3650dbd6c6738fb9"
+dependencies = [
+ "libc",
+ "windows-sys 0.52.0",
+]
+
 [[package]]
 name = "overload"
 version = "0.1.1"
@@ -5919,7 +6168,7 @@ version = "0.8.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "d95f5254224e617595d2cc3cc73ff0a5eaf2637519e25f03388154e9378b6ffa"
 dependencies = [
- "crypto-mac 0.11.1",
+ "crypto-mac 0.11.0",
 ]
 
 [[package]]
@@ -5951,11 +6200,11 @@ dependencies = [
 
 [[package]]
 name = "pem"
-version = "3.0.3"
+version = "3.0.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1b8fcc794035347fb64beda2d3b462595dd2753e3f268d89c5aae77e8cf2c310"
+checksum = "8e459365e590736a54c3fa561947c84837534b8e9af6fc5bf781307e82658fae"
 dependencies = [
- "base64 0.21.7",
+ "base64 0.22.0",
  "serde",
 ]
 
@@ -5976,9 +6225,9 @@ checksum = "e3148f5046208a5d56bcfc03053e3ca6334e51da8dfb19b6cdc8b306fae3283e"
 
 [[package]]
 name = "pest"
-version = "2.7.8"
+version = "2.7.9"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "56f8023d0fb78c8e03784ea1c7f3fa36e68a723138990b8d5a47d916b651e7a8"
+checksum = "311fb059dee1a7b802f036316d790138c613a4e8b180c822e3925a662e9f0c95"
 dependencies = [
  "memchr",
  "thiserror",
@@ -6015,29 +6264,29 @@ dependencies = [
 
 [[package]]
 name = "pin-project"
-version = "1.1.4"
+version = "1.1.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0302c4a0442c456bd56f841aee5c3bfd17967563f6fadc9ceb9f9c23cf3807e0"
+checksum = "b6bf43b791c5b9e34c3d182969b4abb522f9343702850a2e57f460d00d09b4b3"
 dependencies = [
  "pin-project-internal",
 ]
 
 [[package]]
 name = "pin-project-internal"
-version = "1.1.4"
+version = "1.1.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "266c042b60c9c76b8d53061e52b2e0d1116abc57cefc8c5cd671619a56ac3690"
+checksum = "2f38a4412a78282e09a2cf38d195ea5420d15ba0602cb375210efbc877243965"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.52",
+ "syn 2.0.60",
 ]
 
 [[package]]
 name = "pin-project-lite"
-version = "0.2.13"
+version = "0.2.14"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8afb450f006bf6385ca15ef45d71d2288452bc3683ce2e2cacc0d18e4be60b58"
+checksum = "bda66fc9667c18cb2758a2ac84d1167245054bcf85d5d1aaa6923f45801bdd02"
 
 [[package]]
 name = "pin-utils"
@@ -6061,7 +6310,7 @@ version = "0.10.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "f950b2377845cebe5cf8b5165cb3cc1a5e0fa5cfa3e1f7f55707d8fd82e0a7b7"
 dependencies = [
- "der 0.7.8",
+ "der 0.7.9",
  "spki 0.7.3",
 ]
 
@@ -6079,9 +6328,9 @@ checksum = "e8d0eef3571242013a0d5dc84861c3ae4a652e56e12adf8bdc26ff5f8cb34c94"
 
 [[package]]
 name = "platforms"
-version = "3.3.0"
+version = "3.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "626dec3cac7cc0e1577a2ec3fc496277ec2baa084bebad95bb6fdbfae235f84c"
+checksum = "db23d408679286588f4d4644f965003d056e3dd5abcaaa938116871d7ce2fee7"
 
 [[package]]
 name = "plotters"
@@ -6113,14 +6362,15 @@ dependencies = [
 
 [[package]]
 name = "polling"
-version = "3.5.0"
+version = "3.6.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "24f040dee2588b4963afb4e420540439d126f73fdacf4a9c486a96d840bac3c9"
+checksum = "e0c976a60b2d7e99d6f229e414670a9b85d13ac305cc6d1e9c134de58c5aaaf6"
 dependencies = [
  "cfg-if",
  "concurrent-queue",
+ "hermit-abi 0.3.9",
  "pin-project-lite",
- "rustix 0.38.31",
+ "rustix 0.38.33",
  "tracing",
  "windows-sys 0.52.0",
 ]
@@ -6145,14 +6395,14 @@ dependencies = [
  "cfg-if",
  "cpufeatures",
  "opaque-debug",
- "universal-hash 0.4.1",
+ "universal-hash 0.4.0",
 ]
 
 [[package]]
 name = "polyval"
-version = "0.6.1"
+version = "0.6.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d52cff9d1d4dee5fe6d03729099f4a310a41179e0a10dbf542039873f2e826fb"
+checksum = "9d1fe60d06143b2430aa532c94cfe9e29783047f06c0d7fd359a9a51b729fa25"
 dependencies = [
  "cfg-if",
  "cpufeatures",
@@ -6275,9 +6525,9 @@ dependencies = [
 
 [[package]]
 name = "proc-macro2"
-version = "1.0.78"
+version = "1.0.81"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e2422ad645d89c99f8f3e6b88a9fdeca7fabeac836b1002371c4367c8f984aae"
+checksum = "3d1597b0c024618f09a9c3b8655b7e430397a36d23fdafec26d6965e9eec3eba"
 dependencies = [
  "unicode-ident",
 ]
@@ -6314,9 +6564,9 @@ dependencies = [
 
 [[package]]
 name = "prometheus-client"
-version = "0.22.1"
+version = "0.22.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6f87c10af16e0af74010d2a123d202e8363c04db5acfa91d8747f64a8524da3a"
+checksum = "c1ca959da22a332509f2a73ae9e5f23f9dcfc31fd3a54d71f159495bd5909baa"
 dependencies = [
  "dtoa",
  "itoa",
@@ -6332,7 +6582,7 @@ checksum = "440f724eba9f6996b75d63681b0a92b06947f1457076d503a4d2e2c8f56442b8"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.52",
+ "syn 2.0.60",
 ]
 
 [[package]]
@@ -6343,13 +6593,13 @@ checksum = "31b476131c3c86cb68032fdc5cb6d5a1045e3e42d96b69fa599fd77701e1f5bf"
 dependencies = [
  "bit-set",
  "bit-vec",
- "bitflags 2.4.2",
+ "bitflags 2.5.0",
  "lazy_static",
  "num-traits",
  "rand",
  "rand_chacha",
  "rand_xorshift",
- "regex-syntax 0.8.2",
+ "regex-syntax 0.8.3",
  "rusty-fork",
  "tempfile",
  "unarray",
@@ -6468,7 +6718,7 @@ dependencies = [
  "quinn-proto",
  "quinn-udp",
  "rustc-hash",
- "rustls",
+ "rustls 0.21.11",
  "thiserror",
  "tokio",
  "tracing",
@@ -6484,7 +6734,7 @@ dependencies = [
  "rand",
  "ring 0.16.20",
  "rustc-hash",
- "rustls",
+ "rustls 0.21.11",
  "slab",
  "thiserror",
  "tinyvec",
@@ -6506,9 +6756,9 @@ dependencies = [
 
 [[package]]
 name = "quote"
-version = "1.0.35"
+version = "1.0.36"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "291ec9ab5efd934aaf503a6466c5d5251535d108ee747472c3977cc5acc868ef"
+checksum = "0fa76aaf39101c457836aec0ce2316dbdc3ab723cdda1c6bd4e6ad4208acaca7"
 dependencies = [
  "proc-macro2",
 ]
@@ -6587,9 +6837,9 @@ dependencies = [
 
 [[package]]
 name = "rayon"
-version = "1.9.0"
+version = "1.10.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e4963ed1bc86e4f3ee217022bd855b297cef07fb9eac5dfa1f788b220b49b3bd"
+checksum = "b418a60154510ca1a002a752ca9714984e21e4241e804d32555251faf8b78ffa"
 dependencies = [
  "either",
  "rayon-core",
@@ -6611,7 +6861,7 @@ version = "0.11.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "52c4f3084aa3bc7dfbba4eff4fab2a54db4324965d8872ab933565e6fbd83bc6"
 dependencies = [
- "pem 3.0.3",
+ "pem 3.0.4",
  "ring 0.16.20",
  "time",
  "yasna",
@@ -6637,9 +6887,9 @@ dependencies = [
 
 [[package]]
 name = "redox_users"
-version = "0.4.4"
+version = "0.4.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a18479200779601e498ada4e8c1e1f50e3ee19deb0259c25825a98b5603b2cb4"
+checksum = "bd283d9651eeda4b2a83a43c1c91b266c40fd76ecd39a50a8c630ae69dc72891"
 dependencies = [
  "getrandom",
  "libredox",
@@ -6648,14 +6898,14 @@ dependencies = [
 
 [[package]]
 name = "regex"
-version = "1.10.3"
+version = "1.10.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b62dbe01f0b06f9d8dc7d49e05a0785f153b00b2c227856282f671e0318c9b15"
+checksum = "c117dbdfde9c8308975b6a18d71f3f385c89461f7b3fb054288ecf2a2058ba4c"
 dependencies = [
  "aho-corasick",
  "memchr",
- "regex-automata 0.4.5",
- "regex-syntax 0.8.2",
+ "regex-automata 0.4.6",
+ "regex-syntax 0.8.3",
 ]
 
 [[package]]
@@ -6669,13 +6919,13 @@ dependencies = [
 
 [[package]]
 name = "regex-automata"
-version = "0.4.5"
+version = "0.4.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5bb987efffd3c6d0d8f5f89510bb458559eab11e4f869acb20bf845e016259cd"
+checksum = "86b83b8b9847f9bf95ef68afb0b8e6cdb80f498442f5179a29fad448fcc1eaea"
 dependencies = [
  "aho-corasick",
  "memchr",
- "regex-syntax 0.8.2",
+ "regex-syntax 0.8.3",
 ]
 
 [[package]]
@@ -6686,23 +6936,23 @@ checksum = "f162c6dd7b008981e4d40210aca20b4bd0f9b60ca9271061b07f78537722f2e1"
 
 [[package]]
 name = "regex-syntax"
-version = "0.8.2"
+version = "0.8.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c08c74e62047bb2de4ff487b251e4a92e24f48745648451635cec7d591162d9f"
+checksum = "adad44e29e4c806119491a7f06f03de4d1af22c3a680dd47f1e6e179439d1f56"
 
 [[package]]
 name = "reqwest"
-version = "0.11.24"
+version = "0.11.27"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c6920094eb85afde5e4a138be3f2de8bbdf28000f0029e72c45025a56b042251"
+checksum = "dd67538700a17451e7cba03ac727fb961abb7607553461627b97de0b89cf4a62"
 dependencies = [
  "base64 0.21.7",
  "bytes",
  "encoding_rs",
  "futures-core",
  "futures-util",
- "h2 0.3.26",
- "http 0.2.11",
+ "h2",
+ "http 0.2.12",
  "http-body 0.4.6",
  "hyper 0.14.28",
  "hyper-rustls",
@@ -6715,16 +6965,16 @@ dependencies = [
  "once_cell",
  "percent-encoding",
  "pin-project-lite",
- "rustls",
- "rustls-pemfile",
+ "rustls 0.21.11",
+ "rustls-pemfile 1.0.4",
  "serde",
  "serde_json",
  "serde_urlencoded",
- "sync_wrapper",
+ "sync_wrapper 0.1.2",
  "system-configuration",
  "tokio",
  "tokio-native-tls",
- "tokio-rustls",
+ "tokio-rustls 0.24.1",
  "tokio-util 0.7.10",
  "tower-service",
  "url",
@@ -6803,6 +7053,30 @@ version = "1.0.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "3582f63211428f83597b51b2ddb88e2a91a9d52d12831f9d08f5e624e8977422"
 
+[[package]]
+name = "rlg"
+version = "0.0.2"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "c6ccf670238310d5c31a52fed1a3314620d037a64f1e5fbdc71b2c50909134dc"
+dependencies = [
+ "dtt",
+ "tokio",
+ "vrd 0.0.4",
+]
+
+[[package]]
+name = "rlg"
+version = "0.0.3"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "9e02c717e23f67b23032a4acb01cf63534d6259938d592e6d2451c02f09fc368"
+dependencies = [
+ "dtt",
+ "hostname",
+ "serde_json",
+ "tokio",
+ "vrd 0.0.5",
+]
+
 [[package]]
 name = "rlp"
 version = "0.5.2"
@@ -6851,9 +7125,9 @@ dependencies = [
 
 [[package]]
 name = "ruint"
-version = "1.12.0"
+version = "1.12.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "49b1d9521f889713d1221270fdd63370feca7e5c71a18745343402fa86e4f04f"
+checksum = "8f308135fef9fc398342da5472ce7c484529df23743fb7c734e0f3d472971e62"
 dependencies = [
  "alloy-rlp",
  "ark-ff 0.3.0",
@@ -6954,11 +7228,11 @@ dependencies = [
 
 [[package]]
 name = "rustix"
-version = "0.38.31"
+version = "0.38.33"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6ea3e1a662af26cd7a3ba09c0297a31af215563ecf42817c98df621387f4e949"
+checksum = "e3cc72858054fcff6d7dea32df2aeaee6a7c24227366d7ea429aada2f26b16ad"
 dependencies = [
- "bitflags 2.4.2",
+ "bitflags 2.5.0",
  "errno",
  "libc",
  "linux-raw-sys 0.4.13",
@@ -6967,16 +7241,30 @@ dependencies = [
 
 [[package]]
 name = "rustls"
-version = "0.21.10"
+version = "0.21.11"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f9d5a6813c0759e4609cd494e8e725babae6a2ca7b62a5536a13daaec6fcb7ba"
+checksum = "7fecbfb7b1444f477b345853b1fce097a2c6fb637b2bfb87e6bc5db0f043fae4"
 dependencies = [
  "log",
  "ring 0.17.8",
- "rustls-webpki",
+ "rustls-webpki 0.101.7",
  "sct",
 ]
 
+[[package]]
+name = "rustls"
+version = "0.22.4"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "bf4ef73721ac7bcd79b2b315da7779d8fc09718c6b3d2d1b2d94850eb8c18432"
+dependencies = [
+ "log",
+ "ring 0.17.8",
+ "rustls-pki-types",
+ "rustls-webpki 0.102.2",
+ "subtle",
+ "zeroize",
+]
+
 [[package]]
 name = "rustls-pemfile"
 version = "1.0.4"
@@ -6986,6 +7274,22 @@ dependencies = [
  "base64 0.21.7",
 ]
 
+[[package]]
+name = "rustls-pemfile"
+version = "2.1.2"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "29993a25686778eb88d4189742cd713c9bce943bc54251a33509dc63cbacf73d"
+dependencies = [
+ "base64 0.22.0",
+ "rustls-pki-types",
+]
+
+[[package]]
+name = "rustls-pki-types"
+version = "1.4.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "ecd36cc4259e3e4514335c4a138c6b43171a8d61d8f5c9348f9fc7529416f247"
+
 [[package]]
 name = "rustls-webpki"
 version = "0.101.7"
@@ -6996,11 +7300,22 @@ dependencies = [
  "untrusted 0.9.0",
 ]
 
+[[package]]
+name = "rustls-webpki"
+version = "0.102.2"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "faaa0a62740bedb9b2ef5afa303da42764c012f743917351dc9a237ea1663610"
+dependencies = [
+ "ring 0.17.8",
+ "rustls-pki-types",
+ "untrusted 0.9.0",
+]
+
 [[package]]
 name = "rustversion"
-version = "1.0.14"
+version = "1.0.15"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7ffc183a10b4478d04cbbbfc96d0873219d962dd5accaff2ffbd4ceb7df837f4"
+checksum = "80af6f9131f277a45a3fba6ce8e2258037bb0477a67e610d3c1fe046ab31de47"
 
 [[package]]
 name = "rusty-fork"
@@ -7055,9 +7370,9 @@ dependencies = [
 
 [[package]]
 name = "scale-info"
-version = "2.10.0"
+version = "2.11.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7f7d66a1128282b7ef025a8ead62a4a9fcf017382ec53b8ffbf4d7bf77bd3c60"
+checksum = "7c453e59a955f81fb62ee5d596b450383d699f152d350e9d23a0db2adb78e4c0"
 dependencies = [
  "cfg-if",
  "derive_more",
@@ -7067,9 +7382,9 @@ dependencies = [
 
 [[package]]
 name = "scale-info-derive"
-version = "2.10.0"
+version = "2.11.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "abf2c68b89cafb3b8d918dd07b42be0da66ff202cf1155c5739a4e0c1ea0dc19"
+checksum = "18cf6c6447f813ef19eb450e985bcce6705f9ce7660db221b59093d15c79c4b7"
 dependencies = [
  "proc-macro-crate 1.3.1",
  "proc-macro2",
@@ -7150,7 +7465,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "d3e97a565f76233a6003f9f5c54be1d9c5bdfa3eccfb189469f11ec4901c47dc"
 dependencies = [
  "base16ct 0.2.0",
- "der 0.7.8",
+ "der 0.7.9",
  "generic-array",
  "pkcs8 0.10.2",
  "subtle",
@@ -7159,9 +7474,9 @@ dependencies = [
 
 [[package]]
 name = "security-framework"
-version = "2.9.2"
+version = "2.10.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "05b64fb303737d99b81884b2c63433e9ae28abebe5eb5045dcdd175dc2ecf4de"
+checksum = "770452e37cad93e0a50d5abc3990d2bc351c36d0328f86cefec2f2fb206eaef6"
 dependencies = [
  "bitflags 1.3.2",
  "core-foundation",
@@ -7172,9 +7487,9 @@ dependencies = [
 
 [[package]]
 name = "security-framework-sys"
-version = "2.9.1"
+version = "2.10.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e932934257d3b408ed8f30db49d85ea163bfe74961f017f405b025af298f0c7a"
+checksum = "41f3cc463c0ef97e11c3461a9d3787412d30e8e7eb907c79180c4a57bf7c04ef"
 dependencies = [
  "core-foundation-sys",
  "libc",
@@ -7223,9 +7538,9 @@ dependencies = [
 
 [[package]]
 name = "serde"
-version = "1.0.197"
+version = "1.0.198"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "3fb1c873e1b9b056a4dc4c0c198b24c3ffa059243875552b2bd0933b1aee4ce2"
+checksum = "9846a40c979031340571da2545a4e5b7c4163bdae79b301d5f86d03979451fcc"
 dependencies = [
  "serde_derive",
 ]
@@ -7252,20 +7567,20 @@ dependencies = [
 
 [[package]]
 name = "serde_derive"
-version = "1.0.197"
+version = "1.0.198"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7eb0b34b42edc17f6b7cac84a52a1c5f0e1bb2227e997ca9011ea3dd34e8610b"
+checksum = "e88edab869b01783ba905e7d0153f9fc1a6505a96e4ad3018011eedb838566d9"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.52",
+ "syn 2.0.60",
 ]
 
 [[package]]
 name = "serde_json"
-version = "1.0.114"
+version = "1.0.116"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c5f09b1bd632ef549eaa9f60a1f8de742bdbc698e6cee2095fc84dde5f549ae0"
+checksum = "3e17db7126d17feb94eb3fad46bf1a96b034e8aacbc2e775fe81505f8b0b2813"
 dependencies = [
  "itoa",
  "ryu",
@@ -7274,23 +7589,23 @@ dependencies = [
 
 [[package]]
 name = "serde_path_to_error"
-version = "0.1.15"
+version = "0.1.16"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "ebd154a240de39fdebcf5775d2675c204d7c13cf39a4c697be6493c8e734337c"
+checksum = "af99884400da37c88f5e9146b7f1fd0fbcae8f6eec4e9da38b67d05486f814a6"
 dependencies = [
  "itoa",
  "serde",
 ]
 
 [[package]]
 name = "serde_repr"
-version = "0.1.18"
+version = "0.1.19"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0b2e6b945e9d3df726b65d6ee24060aff8e3533d431f677a9695db04eff9dfdb"
+checksum = "6c64451ba24fc7a6a2d60fc75dd9c83c90903b19028d4eff35e88fc1e86564e9"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.52",
+ "syn 2.0.60",
 ]
 
 [[package]]
@@ -7330,25 +7645,46 @@ version = "1.5.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "e182d6ec6f05393cc0e5ed1bf81ad6db3a8feedf8ee515ecdd369809bcce8082"
 dependencies = [
- "darling",
+ "darling 0.13.4",
  "proc-macro2",
  "quote",
  "syn 1.0.109",
 ]
 
 [[package]]
 name = "serde_yaml"
-version = "0.9.32"
+version = "0.9.34+deprecated"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8fd075d994154d4a774f95b51fb96bdc2832b0ea48425c92546073816cda1f2f"
+checksum = "6a8b1a1a2ebf674015cc02edccce75287f1a0130d394307b36743c2f5d504b47"
 dependencies = [
- "indexmap 2.2.5",
+ "indexmap 2.2.6",
  "itoa",
  "ryu",
  "serde",
  "unsafe-libyaml",
 ]
 
+[[package]]
+name = "serde_yml"
+version = "0.0.4"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "196c3750ff0411738366b0d9534ca55fc74d04a3d4284a450039de950bd11938"
+dependencies = [
+ "dtt",
+ "env_logger 0.11.3",
+ "figlet-rs",
+ "indexmap 2.2.6",
+ "itoa",
+ "log",
+ "openssl",
+ "rlg 0.0.3",
+ "ryu",
+ "serde",
+ "unsafe-libyaml",
+ "uuid 1.8.0",
+ "xtasks",
+]
+
 [[package]]
 name = "sha1"
 version = "0.10.6"
@@ -7425,6 +7761,22 @@ dependencies = [
  "lazy_static",
 ]
 
+[[package]]
+name = "shared_child"
+version = "1.0.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "b0d94659ad3c2137fef23ae75b03d5241d633f8acded53d672decfa0e6e0caef"
+dependencies = [
+ "libc",
+ "winapi",
+]
+
+[[package]]
+name = "shell-words"
+version = "1.1.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "24188a676b6ae68c3b2cb3a01be17fbf7240ce009799bb56d5b1409051e78fde"
+
 [[package]]
 name = "shlex"
 version = "1.3.0"
@@ -7433,9 +7785,9 @@ checksum = "0fda2ff0d084019ba4d7c6f371c95d8fd75ce3524c3cb8fb653a3023f6323e64"
 
 [[package]]
 name = "signal-hook-registry"
-version = "1.4.1"
+version = "1.4.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d8229b473baa5980ac72ef434c4415e70c4b5e71b423043adb4ba059f89c99a1"
+checksum = "a9e9e0b4211b72e7b8b6e85c807d36c212bdb33ea8587f7569562a84df5465b1"
 dependencies = [
  "libc",
 ]
@@ -7476,7 +7828,7 @@ dependencies = [
 name = "simulator"
 version = "0.2.0"
 dependencies = [
- "clap",
+ "clap 2.34.0",
  "env_logger 0.9.3",
  "eth1",
  "eth1_test_rig",
@@ -7686,9 +8038,9 @@ dependencies = [
 
 [[package]]
 name = "smallvec"
-version = "1.13.1"
+version = "1.13.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e6ecd384b10a64542d77071bd64bd7b231f4ed5940fba55e98c3de13824cf3d7"
+checksum = "3c5e1a9a646d36c3599cd173a41282daf47c44583ad367b8e6837255952e5c67"
 
 [[package]]
 name = "snap"
@@ -7762,7 +8114,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "d91ed6c858b01f942cd56b37a94b3e0a1798290327d1236e4d9cf4eaca44d29d"
 dependencies = [
  "base64ct",
- "der 0.7.8",
+ "der 0.7.9",
 ]
 
 [[package]]
@@ -7875,6 +8227,12 @@ version = "0.10.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "73473c0e59e6d5812c5dfe2a064a6444949f089e20eec9a2e5506596494e4623"
 
+[[package]]
+name = "strsim"
+version = "0.11.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "7da8b5736845d9f2fcb837ea5d9e2628564b3b043a70948a3f0b778838c5fb4f"
+
 [[package]]
 name = "strum"
 version = "0.24.1"
@@ -7899,17 +8257,17 @@ dependencies = [
 
 [[package]]
 name = "subtle"
-version = "2.4.1"
+version = "2.5.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6bdef32e8150c2a081110b42772ffe7d7c9032b606bc226c8260fd97e0976601"
+checksum = "81cdd64d312baedb58e21336b31bc043b77e01cc99033ce76ef539f78e965ebc"
 
 [[package]]
 name = "superstruct"
 version = "0.6.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "75b9e5728aa1a87141cefd4e7509903fc01fa0dcb108022b1e841a67c5159fc5"
 dependencies = [
- "darling",
+ "darling 0.13.4",
  "itertools",
  "proc-macro2",
  "quote",
@@ -7939,9 +8297,9 @@ dependencies = [
 
 [[package]]
 name = "syn"
-version = "2.0.52"
+version = "2.0.60"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b699d15b36d1f02c3e7c69f8ffef53de37aefae075d8488d4ba1a7788d574a07"
+checksum = "909518bc7b1c9b779f1bbf07f2929d35af9f0f37e47c6e9ef7f9dddc1e1821f3"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -7954,6 +8312,12 @@ version = "0.1.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "2047c6ded9c721764247e62cd3b03c09ffc529b2ba5b10ec482ae507a4a70160"
 
+[[package]]
+name = "sync_wrapper"
+version = "1.0.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "a7065abeca94b6a8a577f9bd45aa0867a2238b74e8eb67cf10d492bc39351394"
+
 [[package]]
 name = "synstructure"
 version = "0.12.6"
@@ -8060,7 +8424,7 @@ checksum = "85b77fafb263dd9d05cbeac119526425676db3784113aa9295c88498cbf8bff1"
 dependencies = [
  "cfg-if",
  "fastrand",
- "rustix 0.38.31",
+ "rustix 0.38.33",
  "windows-sys 0.52.0",
 ]
 
@@ -8128,22 +8492,22 @@ dependencies = [
 
 [[package]]
 name = "thiserror"
-version = "1.0.57"
+version = "1.0.59"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1e45bcbe8ed29775f228095caf2cd67af7a4ccf756ebff23a306bf3e8b47b24b"
+checksum = "f0126ad08bff79f29fc3ae6a55cc72352056dfff61e3ff8bb7129476d44b23aa"
 dependencies = [
  "thiserror-impl",
 ]
 
 [[package]]
 name = "thiserror-impl"
-version = "1.0.57"
+version = "1.0.59"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a953cb265bef375dae3de6663da4d3804eee9682ea80d8e2542529b73c531c81"
+checksum = "d1cd413b5d558b4c5bf3680e324a6fa5014e7b7c067a51e69dbdf47eb7148b66"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.52",
+ "syn 2.0.60",
 ]
 
 [[package]]
@@ -8167,9 +8531,9 @@ dependencies = [
 
 [[package]]
 name = "time"
-version = "0.3.34"
+version = "0.3.36"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c8248b6521bb14bc45b4067159b9b6ad792e2d6d754d6c41fb50e29fefe38749"
+checksum = "5dfd88e563464686c916c7e46e623e520ddc6d79fa6641390f2e3fa86e83e885"
 dependencies = [
  "deranged",
  "itoa",
@@ -8188,9 +8552,9 @@ checksum = "ef927ca75afb808a4d64dd374f00a2adf8d0fcff8e7b184af886c3c87ec4a3f3"
 
 [[package]]
 name = "time-macros"
-version = "0.2.17"
+version = "0.2.18"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7ba3a3ef41e6672a2f0f001392bb5dcd3ff0a9992d618ca761a11c3121547774"
+checksum = "3f252a68540fde3a3877aeea552b832b40ab9a69e318efd078774a01ddee1ccf"
 dependencies = [
  "num-conv",
  "time-core",
@@ -8262,15 +8626,16 @@ checksum = "1f3ccbac311fea05f86f61904b462b55fb3df8837a366dfc601a0161d0532f20"
 
 [[package]]
 name = "tokio"
-version = "1.36.0"
+version = "1.37.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "61285f6515fa018fb2d1e46eb21223fff441ee8db5d0f1435e8ab4f5cdb80931"
+checksum = "1adbebffeca75fcfd058afa480fb6c0b81e165a0323f9c9d39c9697e37c46787"
 dependencies = [
  "backtrace",
  "bytes",
  "libc",
  "mio",
  "num_cpus",
+ "parking_lot 0.12.1",
  "pin-project-lite",
  "signal-hook-registry",
  "socket2 0.5.6",
@@ -8296,7 +8661,7 @@ checksum = "5b8a1e28f2deaa14e508979454cb3a223b10b938b45af148bc0986de36f1923b"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.52",
+ "syn 2.0.60",
 ]
 
 [[package]]
@@ -8341,15 +8706,26 @@ version = "0.24.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "c28327cf380ac148141087fbfb9de9d7bd4e84ab5d2c28fbc911d753de8a7081"
 dependencies = [
- "rustls",
+ "rustls 0.21.11",
+ "tokio",
+]
+
+[[package]]
+name = "tokio-rustls"
+version = "0.25.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "775e0c0f0adb3a2f22a00c4745d728b479985fc15ee7ca6a2608388c5569860f"
+dependencies = [
+ "rustls 0.22.4",
+ "rustls-pki-types",
  "tokio",
 ]
 
 [[package]]
 name = "tokio-stream"
-version = "0.1.14"
+version = "0.1.15"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "397c988d37662c7dda6d2208364a706264bf3d6138b11d436cbac0ad38832842"
+checksum = "267ac89e0bec6e691e5813911606935d77c476ff49024f98abcea3e7b15e37af"
 dependencies = [
  "futures-core",
  "pin-project-lite",
@@ -8424,7 +8800,7 @@ version = "0.19.15"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "1b5bb770da30e5cbfde35a2d7b9b8a2c4b8ef89548a7a6aeab5c9a576e3e7421"
 dependencies = [
- "indexmap 2.2.5",
+ "indexmap 2.2.6",
  "serde",
  "serde_spanned",
  "toml_datetime",
@@ -8437,7 +8813,7 @@ version = "0.20.7"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "70f427fce4d84c72b5b732388bf4a9f4531b53f74e2887e3ecb2481f68f66d81"
 dependencies = [
- "indexmap 2.2.5",
+ "indexmap 2.2.6",
  "toml_datetime",
  "winnow",
 ]
@@ -8502,7 +8878,7 @@ checksum = "34704c8d6ebcbc939824180af020566b01a7c01f80641264eba0999f6c2b6be7"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.52",
+ "syn 2.0.60",
 ]
 
 [[package]]
@@ -8590,7 +8966,7 @@ version = "0.5.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "84303a9c7cda5f085a3ed9cd241d1e95e04d88aab1d679b02f212e653537ba86"
 dependencies = [
- "darling",
+ "darling 0.13.4",
  "quote",
  "syn 1.0.109",
 ]
@@ -8744,9 +9120,9 @@ checksum = "f962df74c8c05a667b5ee8bcf162993134c104e96440b663c8daa176dc772d8c"
 
 [[package]]
 name = "universal-hash"
-version = "0.4.1"
+version = "0.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9f214e8f697e925001e66ec2c6e37a4ef93f0f78c2eed7814394e10c62025b05"
+checksum = "8326b2c654932e3e4f9196e69d08fdf7cfd718e1dc6f66b347e6024a0c961402"
 dependencies = [
  "generic-array",
  "subtle",
@@ -8764,9 +9140,9 @@ dependencies = [
 
 [[package]]
 name = "unsafe-libyaml"
-version = "0.2.10"
+version = "0.2.11"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "ab4c90930b95a82d00dc9e9ac071b4991924390d46cbd0dfe566148667605e4b"
+checksum = "673aac59facbab8a9007c7f6108d11f63b603f7cabff99fabf650fea5c32b861"
 
 [[package]]
 name = "unsigned-varint"
@@ -8826,6 +9202,12 @@ dependencies = [
  "percent-encoding",
 ]
 
+[[package]]
+name = "utf8parse"
+version = "0.2.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "711b9620af191e0cdc7468a8d14e709c3dcdb115b36f838e601583af800a370a"
+
 [[package]]
 name = "uuid"
 version = "0.8.2"
@@ -8836,14 +9218,23 @@ dependencies = [
  "serde",
 ]
 
+[[package]]
+name = "uuid"
+version = "1.8.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "a183cf7feeba97b4dd1c0d46788634f6221d87fa961b305bed08c851829efcc0"
+dependencies = [
+ "getrandom",
+]
+
 [[package]]
 name = "validator_client"
 version = "0.3.5"
 dependencies = [
  "account_utils",
  "bincode",
  "bls",
- "clap",
+ "clap 2.34.0",
  "clap_utils",
  "deposit_contract",
  "directory",
@@ -8855,7 +9246,7 @@ dependencies = [
  "filesystem",
  "futures",
  "hex",
- "hyper 1.2.0",
+ "hyper 1.3.1",
  "itertools",
  "lazy_static",
  "libsecp256k1",
@@ -8915,7 +9306,7 @@ version = "0.1.0"
 dependencies = [
  "account_utils",
  "bls",
- "clap",
+ "clap 2.34.0",
  "clap_utils",
  "environment",
  "eth2",
@@ -8964,6 +9355,25 @@ version = "1.0.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "6a02e4885ed3bc0f2de90ea6dd45ebcbb66dacffe03547fadbb0eeae2770887d"
 
+[[package]]
+name = "vrd"
+version = "0.0.4"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "a81b8b5b404f3d7afa1b8142a6bc980c20cd68556c634c3db517871aa0402521"
+dependencies = [
+ "rand",
+]
+
+[[package]]
+name = "vrd"
+version = "0.0.5"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "ee1067b8d17481f5be71b59d11c329e955ffe36348907e0a4a41b619682bb4af"
+dependencies = [
+ "rand",
+ "serde",
+]
+
 [[package]]
 name = "wait-timeout"
 version = "0.2.0"
@@ -8994,29 +9404,28 @@ dependencies = [
 
 [[package]]
 name = "warp"
-version = "0.3.6"
+version = "0.3.7"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c1e92e22e03ff1230c03a1a8ee37d2f89cd489e2e541b7550d6afad96faed169"
+checksum = "4378d202ff965b011c64817db11d5829506d3404edeadb61f190d111da3f231c"
 dependencies = [
  "bytes",
  "futures-channel",
  "futures-util",
  "headers",
- "http 0.2.11",
+ "http 0.2.12",
  "hyper 0.14.28",
  "log",
  "mime",
  "mime_guess",
  "percent-encoding",
  "pin-project",
- "rustls-pemfile",
+ "rustls-pemfile 2.1.2",
  "scoped-tls",
  "serde",
  "serde_json",
  "serde_urlencoded",
  "tokio",
- "tokio-rustls",
- "tokio-stream",
+ "tokio-rustls 0.25.0",
  "tokio-util 0.7.10",
  "tower-service",
  "tracing",
@@ -9056,34 +9465,34 @@ checksum = "b8dad83b4f25e74f184f64c43b150b91efe7647395b42289f38e50566d82855b"
 
 [[package]]
 name = "wasm-bindgen"
-version = "0.2.91"
+version = "0.2.92"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c1e124130aee3fb58c5bdd6b639a0509486b0338acaaae0c84a5124b0f588b7f"
+checksum = "4be2531df63900aeb2bca0daaaddec08491ee64ceecbee5076636a3b026795a8"
 dependencies = [
  "cfg-if",
  "wasm-bindgen-macro",
 ]
 
 [[package]]
 name = "wasm-bindgen-backend"
-version = "0.2.91"
+version = "0.2.92"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c9e7e1900c352b609c8488ad12639a311045f40a35491fb69ba8c12f758af70b"
+checksum = "614d787b966d3989fa7bb98a654e369c762374fd3213d212cfc0251257e747da"
 dependencies = [
  "bumpalo",
  "log",
  "once_cell",
  "proc-macro2",
  "quote",
- "syn 2.0.52",
+ "syn 2.0.60",
  "wasm-bindgen-shared",
 ]
 
 [[package]]
 name = "wasm-bindgen-futures"
-version = "0.4.41"
+version = "0.4.42"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "877b9c3f61ceea0e56331985743b13f3d25c406a7098d45180fb5f09bc19ed97"
+checksum = "76bc14366121efc8dbb487ab05bcc9d346b3b5ec0eaa76e46594cabbe51762c0"
 dependencies = [
  "cfg-if",
  "js-sys",
@@ -9093,32 +9502,32 @@ dependencies = [
 
 [[package]]
 name = "wasm-bindgen-macro"
-version = "0.2.91"
+version = "0.2.92"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b30af9e2d358182b5c7449424f017eba305ed32a7010509ede96cdc4696c46ed"
+checksum = "a1f8823de937b71b9460c0c34e25f3da88250760bec0ebac694b49997550d726"
 dependencies = [
  "quote",
  "wasm-bindgen-macro-support",
 ]
 
 [[package]]
 name = "wasm-bindgen-macro-support"
-version = "0.2.91"
+version = "0.2.92"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "642f325be6301eb8107a83d12a8ac6c1e1c54345a7ef1a9261962dfefda09e66"
+checksum = "e94f17b526d0a461a191c78ea52bbce64071ed5c04c9ffe424dcb38f74171bb7"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.52",
+ "syn 2.0.60",
  "wasm-bindgen-backend",
  "wasm-bindgen-shared",
 ]
 
 [[package]]
 name = "wasm-bindgen-shared"
-version = "0.2.91"
+version = "0.2.92"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "4f186bd2dcf04330886ce82d6f33dd75a7bfcf69ecf5763b89fcde53b6ac9838"
+checksum = "af190c94f2773fdb3729c55b007a722abb5384da03bc0986df4c289bf5567e96"
 
 [[package]]
 name = "wasm-streams"
@@ -9157,14 +9566,14 @@ dependencies = [
  "beacon_node",
  "bls",
  "byteorder",
- "clap",
+ "clap 2.34.0",
  "diesel",
  "diesel_migrations",
  "env_logger 0.9.3",
  "eth2",
  "hex",
  "http_api",
- "hyper 1.2.0",
+ "hyper 1.3.1",
  "log",
  "logging",
  "network",
@@ -9185,9 +9594,9 @@ dependencies = [
 
 [[package]]
 name = "web-sys"
-version = "0.3.68"
+version = "0.3.69"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "96565907687f7aceb35bc5fc03770a8a0471d82e479f25832f54a0e3f4b28446"
+checksum = "77afa9a11836342370f4817622a2f0f418b134426d91a82dfb48f532d2ec13ef"
 dependencies = [
  "js-sys",
  "wasm-bindgen",
@@ -9227,9 +9636,9 @@ checksum = "5f20c57d8d7db6d3b86154206ae5d8fba62dd39573114de97c2cb0578251f8e1"
 
 [[package]]
 name = "whoami"
-version = "1.5.0"
+version = "1.5.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0fec781d48b41f8163426ed18e8fc2864c12937df9ce54c88ede7bd47270893e"
+checksum = "a44ab49fad634e88f55bf8f9bb3abd2f27d7204172a112c7c9987e01c1c94ea9"
 dependencies = [
  "redox_syscall 0.4.1",
  "wasite",
@@ -9244,9 +9653,9 @@ checksum = "c168940144dd21fd8046987c16a46a33d5fc84eec29ef9dcddc2ac9e31526b7c"
 
 [[package]]
 name = "widestring"
-version = "1.0.2"
+version = "1.1.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "653f141f39ec16bba3c5abe400a0c60da7468261cc2cbf36805022876bc721a8"
+checksum = "7219d36b6eac893fa81e84ebe06485e7dcbb616177469b142df14f1f4deb1311"
 
 [[package]]
 name = "winapi"
@@ -9316,7 +9725,7 @@ version = "0.52.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "33ab640c8d7e35bf8ba19b884ba838ceb4fba93a4e8c65a9059d08afcfc683d9"
 dependencies = [
- "windows-targets 0.52.4",
+ "windows-targets 0.52.5",
 ]
 
 [[package]]
@@ -9343,7 +9752,7 @@ version = "0.52.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "282be5f36a8ce781fad8c8ae18fa3f9beff57ec1b52cb3de0789201425d9a33d"
 dependencies = [
- "windows-targets 0.52.4",
+ "windows-targets 0.52.5",
 ]
 
 [[package]]
@@ -9378,17 +9787,18 @@ dependencies = [
 
 [[package]]
 name = "windows-targets"
-version = "0.52.4"
+version = "0.52.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7dd37b7e5ab9018759f893a1952c9420d060016fc19a472b4bb20d1bdd694d1b"
+checksum = "6f0713a46559409d202e70e28227288446bf7841d3211583a4b53e3f6d96e7eb"
 dependencies = [
- "windows_aarch64_gnullvm 0.52.4",
- "windows_aarch64_msvc 0.52.4",
- "windows_i686_gnu 0.52.4",
- "windows_i686_msvc 0.52.4",
- "windows_x86_64_gnu 0.52.4",
- "windows_x86_64_gnullvm 0.52.4",
- "windows_x86_64_msvc 0.52.4",
+ "windows_aarch64_gnullvm 0.52.5",
+ "windows_aarch64_msvc 0.52.5",
+ "windows_i686_gnu 0.52.5",
+ "windows_i686_gnullvm",
+ "windows_i686_msvc 0.52.5",
+ "windows_x86_64_gnu 0.52.5",
+ "windows_x86_64_gnullvm 0.52.5",
+ "windows_x86_64_msvc 0.52.5",
 ]
 
 [[package]]
@@ -9405,9 +9815,9 @@ checksum = "2b38e32f0abccf9987a4e3079dfb67dcd799fb61361e53e2882c3cbaf0d905d8"
 
 [[package]]
 name = "windows_aarch64_gnullvm"
-version = "0.52.4"
+version = "0.52.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "bcf46cf4c365c6f2d1cc93ce535f2c8b244591df96ceee75d8e83deb70a9cac9"
+checksum = "7088eed71e8b8dda258ecc8bac5fb1153c5cffaf2578fc8ff5d61e23578d3263"
 
 [[package]]
 name = "windows_aarch64_msvc"
@@ -9423,9 +9833,9 @@ checksum = "dc35310971f3b2dbbf3f0690a219f40e2d9afcf64f9ab7cc1be722937c26b4bc"
 
 [[package]]
 name = "windows_aarch64_msvc"
-version = "0.52.4"
+version = "0.52.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "da9f259dd3bcf6990b55bffd094c4f7235817ba4ceebde8e6d11cd0c5633b675"
+checksum = "9985fd1504e250c615ca5f281c3f7a6da76213ebd5ccc9561496568a2752afb6"
 
 [[package]]
 name = "windows_i686_gnu"
@@ -9441,9 +9851,15 @@ checksum = "a75915e7def60c94dcef72200b9a8e58e5091744960da64ec734a6c6e9b3743e"
 
 [[package]]
 name = "windows_i686_gnu"
-version = "0.52.4"
+version = "0.52.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b474d8268f99e0995f25b9f095bc7434632601028cf86590aea5c8a5cb7801d3"
+checksum = "88ba073cf16d5372720ec942a8ccbf61626074c6d4dd2e745299726ce8b89670"
+
+[[package]]
+name = "windows_i686_gnullvm"
+version = "0.52.5"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "87f4261229030a858f36b459e748ae97545d6f1ec60e5e0d6a3d32e0dc232ee9"
 
 [[package]]
 name = "windows_i686_msvc"
@@ -9459,9 +9875,9 @@ checksum = "8f55c233f70c4b27f66c523580f78f1004e8b5a8b659e05a4eb49d4166cca406"
 
 [[package]]
 name = "windows_i686_msvc"
-version = "0.52.4"
+version = "0.52.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1515e9a29e5bed743cb4415a9ecf5dfca648ce85ee42e15873c3cd8610ff8e02"
+checksum = "db3c2bf3d13d5b658be73463284eaf12830ac9a26a90c717b7f771dfe97487bf"
 
 [[package]]
 name = "windows_x86_64_gnu"
@@ -9477,9 +9893,9 @@ checksum = "53d40abd2583d23e4718fddf1ebec84dbff8381c07cae67ff7768bbf19c6718e"
 
 [[package]]
 name = "windows_x86_64_gnu"
-version = "0.52.4"
+version = "0.52.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5eee091590e89cc02ad514ffe3ead9eb6b660aedca2183455434b93546371a03"
+checksum = "4e4246f76bdeff09eb48875a0fd3e2af6aada79d409d33011886d3e1581517d9"
 
 [[package]]
 name = "windows_x86_64_gnullvm"
@@ -9495,9 +9911,9 @@ checksum = "0b7b52767868a23d5bab768e390dc5f5c55825b6d30b86c844ff2dc7414044cc"
 
 [[package]]
 name = "windows_x86_64_gnullvm"
-version = "0.52.4"
+version = "0.52.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "77ca79f2451b49fa9e2af39f0747fe999fcda4f5e241b2898624dca97a1f2177"
+checksum = "852298e482cd67c356ddd9570386e2862b5673c85bd5f88df9ab6802b334c596"
 
 [[package]]
 name = "windows_x86_64_msvc"
@@ -9513,9 +9929,9 @@ checksum = "ed94fce61571a4006852b7389a063ab983c02eb1bb37b47f8272ce92d06d9538"
 
 [[package]]
 name = "windows_x86_64_msvc"
-version = "0.52.4"
+version = "0.52.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "32b752e52a2da0ddfbdbcc6fceadfeede4c939ed16d13e648833a61dfb611ed8"
+checksum = "bec47e5bfd1bff0eeaf6d8b485cc1074891a197ab4225d504cb7a1ab88b02bf0"
 
 [[package]]
 name = "winnow"
@@ -9601,9 +10017,9 @@ dependencies = [
 
 [[package]]
 name = "xml-rs"
-version = "0.8.19"
+version = "0.8.20"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0fcb9cbac069e033553e8bb871be2fbdffcab578eb25bd0f7c508cedc6dcd75a"
+checksum = "791978798f0597cfc70478424c2b4fdc2b7a8024aaff78497ef00f24ef674193"
 
 [[package]]
 name = "xmltree"
@@ -9615,12 +10031,23 @@ dependencies = [
 ]
 
 [[package]]
-name = "yaml-rust"
-version = "0.4.5"
+name = "xtasks"
+version = "0.0.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "56c1936c4cc7a1c9ab21a1ebb602eb942ba868cbd44a99cb7cdc5892335e1c85"
+checksum = "940db5674e301470e6cd91098b2c68a1fad751a1623575d1133f7456146e6d2f"
 dependencies = [
- "linked-hash-map",
+ "anyhow",
+ "clap 4.5.4",
+ "derive_builder",
+ "dialoguer",
+ "dtt",
+ "duct",
+ "fs_extra",
+ "glob",
+ "rlg 0.0.2",
+ "serde",
+ "serde_json",
+ "vrd 0.0.5",
 ]
 
 [[package]]
@@ -9679,7 +10106,7 @@ checksum = "9ce1b18ccd8e73a9321186f97e46f9f04b778851177567b1975109d26a08d2a6"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.52",
+ "syn 2.0.60",
 ]
 
 [[package]]
@@ -9699,7 +10126,7 @@ checksum = "ce36e65b0d2999d2aafac989fb249189a141aee1f53c612c1f37d72631959f69"
 dependencies = [
  "proc-macro2",
  "quote",
- "syn 2.0.52",
+ "syn 2.0.60",
 ]
 
 [[package]]
@@ -9743,9 +10170,9 @@ dependencies = [
 
 [[package]]
 name = "zstd-sys"
-version = "2.0.9+zstd.1.5.5"
+version = "2.0.10+zstd.1.5.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9e16efa8a874a0481a574084d34cc26fdb3b99627480f785888deb6386506656"
+checksum = "c253a4914af5bafc8fa8c86ee400827e83cf6ec01195ec1f1ed8441bf00d65aa"
 dependencies = [
  "cc",
  "pkg-config",
```

### Cargo.toml
```diff
@@ -174,15 +174,15 @@ tree_hash = "0.5"
 tree_hash_derive = "0.5"
 url = "2"
 uuid = { version = "0.8", features = ["serde", "v4"] }
-warp = { version = "0.3.6", default-features = false, features = ["tls"] }
+warp = { version = "0.3.7", default-features = false, features = ["tls"] }
 zeroize = { version = "1", features = ["zeroize_derive"] }
 zip = "0.6"
 
 # Local crates.
 account_utils = { path = "common/account_utils" }
 beacon_chain = { path = "beacon_node/beacon_chain" }
 beacon_node = { path = "beacon_node" }
-beacon_processor =  { path = "beacon_node/beacon_processor" }
+beacon_processor = { path = "beacon_node/beacon_processor" }
 bls = { path = "crypto/bls" }
 cached_tree_hash = { path = "consensus/cached_tree_hash" }
 clap_utils = { path = "common/clap_utils" }
@@ -219,7 +219,7 @@ network = { path = "beacon_node/network" }
 operation_pool = { path = "beacon_node/operation_pool" }
 pretty_reqwest_error = { path = "common/pretty_reqwest_error" }
 proto_array = { path = "consensus/proto_array" }
-safe_arith = {path = "consensus/safe_arith"}
+safe_arith = { path = "consensus/safe_arith" }
 sensitive_url = { path = "common/sensitive_url" }
 slasher = { path = "slasher" }
 slashing_protection = { path = "validator_client/slashing_protection" }
```

### consensus/int_to_bytes/Cargo.toml
```diff
@@ -8,5 +8,5 @@ edition = { workspace = true }
 bytes = { workspace = true }
 
 [dev-dependencies]
-yaml-rust = "0.4.4"
 hex = { workspace = true }
+serde_yml = "0.0.4"
```

### consensus/int_to_bytes/src/lib.rs
```diff
@@ -78,8 +78,7 @@ pub fn int_to_bytes96(int: u64) -> Vec<u8> {
 #[cfg(test)]
 mod tests {
     use super::*;
-    use std::{fs::File, io::prelude::*, path::PathBuf};
-    use yaml_rust::yaml;
+    use std::{collections::HashMap, fs::File, io::prelude::*, path::PathBuf};
 
     #[test]
     fn fixed_bytes32() {
@@ -111,14 +110,13 @@ mod tests {
 
         file.read_to_string(&mut yaml_str).unwrap();
 
-        let docs = yaml::YamlLoader::load_from_str(&yaml_str).unwrap();
-        let doc = &docs[0];
-        let test_cases = doc["test_cases"].as_vec().unwrap();
+        let docs: HashMap<String, serde_yml::Value> = serde_yml::from_str(&yaml_str).unwrap();
+        let test_cases = docs["test_cases"].as_sequence().unwrap();
 
         for test_case in test_cases {
             let byte_length = test_case["byte_length"].as_i64().unwrap() as u64;
             let int = test_case["int"].as_i64().unwrap() as u64;
-            let bytes_string = test_case["bytes"].clone().into_string().unwrap();
+            let bytes_string = test_case["bytes"].as_str().unwrap();
             let bytes = hex::decode(bytes_string.replace("0x", "")).unwrap();
 
             match byte_length {
```
