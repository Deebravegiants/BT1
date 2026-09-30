# [?] chore: Update tracing-subscriber to fix `RUSTSEC-2025-0055` (#9712)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-01-13
Source: https://github.com/iotaledger/iota/commit/c33b939d06e7a4094bdc46df1e0558658e3b225e
Type: security-commit

## Details
chore: Update tracing-subscriber to fix `RUSTSEC-2025-0055` (#9712)

## Description

Updates `tracing-subscriber` to avoid
https://rustsec.org/advisories/RUSTSEC-2025-0055

Closes #8448

## Patch
### Cargo.lock
```diff
@@ -7,10 +7,6 @@ name = "Inflector"
 version = "0.11.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "fe438c63458706e03479442743baae6c88256498e6431708f6dfc520a26515d3"
-dependencies = [
- "lazy_static",
- "regex",
-]
 
 [[package]]
 name = "addchain"
@@ -830,15 +826,9 @@ dependencies = [
  "memchr",
  "num",
  "regex",
- "regex-syntax 0.8.6",
+ "regex-syntax",
 ]
 
-[[package]]
-name = "ascii_utils"
-version = "0.9.3"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "71938f30533e4d95a6d17aa530939da3842c2ab6f4f84b9dae68447e4129f74a"
-
 [[package]]
 name = "asn1-rs"
 version = "0.7.1"
@@ -851,7 +841,7 @@ dependencies = [
  "nom",
  "num-traits",
  "rusticata-macros",
- "thiserror 2.0.12",
+ "thiserror 2.0.17",
  "time",
 ]
 
@@ -912,27 +902,26 @@ dependencies = [
 
 [[package]]
 name = "async-graphql"
-version = "7.0.17"
+version = "7.1.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "036618f842229ba0b89652ffe425f96c7c16a49f7e3cb23b56fca7f61fd74980"
+checksum = "31b75c5a43a58890d6dcc02d03952456570671332bb0a5a947b1f09c699912a5"
 dependencies = [
  "async-graphql-derive",
  "async-graphql-parser",
  "async-graphql-value",
- "async-stream",
  "async-trait",
+ "asynk-strim",
  "base64 0.22.1",
  "bytes",
  "chrono",
- "fast_chemail",
  "fnv",
  "futures-channel",
  "futures-timer",
  "futures-util",
  "handlebars",
  "http 1.3.1",
  "indexmap 2.11.0",
- "lru",
+ "lru 0.16.3",
  "mime",
  "multer",
  "num-traits",
@@ -943,17 +932,16 @@ dependencies = [
  "serde_json",
  "serde_urlencoded",
  "static_assertions_next",
- "tempfile",
- "thiserror 1.0.64",
+ "thiserror 2.0.17",
  "tracing",
  "tracing-futures",
 ]
 
 [[package]]
 name = "async-graphql-axum"
-version = "7.0.17"
+version = "7.1.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8725874ecfbf399e071150b8619c4071d7b2b7a2f117e173dddef53c6bdb6bb1"
+checksum = "599e663e170f69baa0b9f18f52cdfd701e01ade0ac1baef2c4bc488cb68e35c1"
 dependencies = [
  "async-graphql",
  "axum 0.8.4",
@@ -968,26 +956,26 @@ dependencies = [
 
 [[package]]
 name = "async-graphql-derive"
-version = "7.0.17"
+version = "7.1.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "fd45deb3dbe5da5cdb8d6a670a7736d735ba65b455328440f236dfb113727a3d"
+checksum = "0c266ec9a094bbf2d088e016f71aa8d3be7f18c7343b2f0fe6d0e6c1e78977ea"
 dependencies = [
  "Inflector",
  "async-graphql-parser",
- "darling 0.20.10",
+ "darling 0.23.0",
  "proc-macro-crate 3.2.0",
  "proc-macro2",
  "quote",
- "strum 0.26.3",
+ "strum 0.27.2",
  "syn 2.0.100",
- "thiserror 1.0.64",
+ "thiserror 2.0.17",
 ]
 
 [[package]]
 name = "async-graphql-parser"
-version = "7.0.17"
+version = "7.1.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "60b7607e59424a35dadbc085b0d513aa54ec28160ee640cf79ec3b634eba66d3"
+checksum = "67e2188d3f1299087aa02cfb281f12414905ce63f425dbcfe7b589773468d771"
 dependencies = [
  "async-graphql-value",
  "pest",
@@ -997,9 +985,9 @@ dependencies = [
 
 [[package]]
 name = "async-graphql-value"
-version = "7.0.17"
+version = "7.1.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "34ecdaff7c9cffa3614a9f9999bf9ee4c3078fe3ce4d6a6e161736b56febf2de"
+checksum = "527a4c6022fc4dac57b4f03f12395e9a391512e85ba98230b93315f8f45f27fc"
 dependencies = [
  "bytes",
  "indexmap 2.11.0",
@@ -1063,6 +1051,16 @@ version = "0.2.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "2ce4f10ea3abcd6617873bae9f91d1c5332b4a778bd9ce34d0cd517474c1de82"
 
+[[package]]
+name = "asynk-strim"
+version = "0.1.5"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "52697735bdaac441a29391a9e97102c74c6ef0f9b60a40cf109b1b404e29d2f6"
+dependencies = [
+ "futures-core",
+ "pin-project-lite",
+]
+
 [[package]]
 name = "atoi"
 version = "2.0.0"
@@ -2162,7 +2160,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "40723b8fb387abc38f4f4a37c09073622e41dd12327033091ef8950659e6dc0c"
 dependencies = [
  "memchr",
- "regex-automata 0.4.11",
+ "regex-automata",
  "serde",
 ]
 
@@ -2661,7 +2659,7 @@ dependencies = [
  "iota-sdk-types",
  "iota-tls",
  "itertools 0.13.0",
- "lru",
+ "lru 0.12.4",
  "nom",
  "parking_lot 0.12.3",
  "prometheus",
@@ -3255,6 +3253,16 @@ dependencies = [
  "darling_macro 0.21.3",
 ]
 
+[[package]]
+name = "darling"
+version = "0.23.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "25ae13da2f202d56bd7f91c25fba009e7717a1e4a1cc98a76d844b65ae912e9d"
+dependencies = [
+ "darling_core 0.23.0",
+ "darling_macro 0.23.0",
+]
+
 [[package]]
 name = "darling_core"
 version = "0.14.4"
@@ -3297,6 +3305,19 @@ dependencies = [
  "syn 2.0.100",
 ]
 
+[[package]]
+name = "darling_core"
+version = "0.23.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "9865a50f7c335f53564bb694ef660825eb8610e0a53d3e11bf1b0d3df31e03b0"
+dependencies = [
+ "ident_case",
+ "proc-macro2",
+ "quote",
+ "strsim 0.11.1",
+ "syn 2.0.100",
+]
+
 [[package]]
 name = "darling_macro"
 version = "0.14.4"
@@ -3330,6 +3351,17 @@ dependencies = [
  "syn 2.0.100",
 ]
 
+[[package]]
+name = "darling_macro"
+version = "0.23.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "ac3984ec7bd6cfa798e62b4a642426a5be0e68f9401cfc2a01e3fa9ea2fcdb8d"
+dependencies = [
+ "darling_core 0.23.0",
+ "quote",
+ "syn 2.0.100",
+]
+
 [[package]]
 name = "dary_heap"
 version = "0.3.6"
@@ -3484,6 +3516,37 @@ dependencies = [
  "syn 2.0.100",
 ]
 
+[[package]]
+name = "derive_builder"
+version = "0.20.2"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "507dfb09ea8b7fa618fcf76e953f4f5e192547945816d5358edffe39f6f94947"
+dependencies = [
+ "derive_builder_macro",
+]
+
+[[package]]
+name = "derive_builder_core"
+version = "0.20.2"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "2d5bcf7b024d6835cfb3d473887cd966994907effbe9227e8c8219824d06c4e8"
+dependencies = [
+ "darling 0.20.10",
+ "proc-macro2",
+ "quote",
+ "syn 2.0.100",
+]
+
+[[package]]
+name = "derive_builder_macro"
+version = "0.20.2"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "ab63b0e2bf4d5928aff72e83a7dace85d7bba5fe12dcc3c5a572d78caffd3f3c"
+dependencies = [
+ "derive_builder_core",
+ "syn 2.0.100",
+]
+
 [[package]]
 name = "derive_more"
 version = "0.99.18"
@@ -3586,7 +3649,7 @@ version = "0.3.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "e616e59155c92257e84970156f506287853355f58cd4a6eb167385722c32b790"
 dependencies = [
- "nu-ansi-term",
+ "nu-ansi-term 0.46.0",
 ]
 
 [[package]]
@@ -4006,15 +4069,6 @@ version = "0.2.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "4443176a9f2c162692bd3d352d745ef9413eec5782a80d8fd6f8a1ac692a07f7"
 
-[[package]]
-name = "fast_chemail"
-version = "0.9.6"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "495a39d30d624c2caabe6312bfead73e7717692b44e0b32df168c275a2e8e9e4"
-dependencies = [
- "ascii_utils",
-]
-
 [[package]]
 name = "fastcrypto"
 version = "0.1.8"
@@ -4290,6 +4344,12 @@ version = "1.0.7"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "3f9eec918d3f24069decb9af1554cad7c880e2da24a9afd88aca000531ab82c1"
 
+[[package]]
+name = "foldhash"
+version = "0.2.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "77ce24cb58228fbb8aa041425bb1050850ac19177686ea6e0f41a70416f56fdb"
+
 [[package]]
 name = "form_urlencoded"
 version = "1.2.1"
@@ -4726,16 +4786,18 @@ dependencies = [
 
 [[package]]
 name = "handlebars"
-version = "5.1.2"
+version = "6.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d08485b96a0e6393e9e4d1b8d48cf74ad6c063cd905eb33f42c1ce3f0377539b"
+checksum = "9b3f9296c208515b87bd915a2f5d1163d4b3f863ba83337d7713cf478055948e"
 dependencies = [
+ "derive_builder",
  "log",
+ "num-order",
  "pest",
  "pest_derive",
  "serde",
  "serde_json",
- "thiserror 1.0.64",
+ "thiserror 2.0.17",
 ]
 
 [[package]]
@@ -4770,6 +4832,17 @@ version = "0.15.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "5971ac85611da7067dbfcabef3c70ebb5606018acd9e2a3903a0da507521e0d5"
 
+[[package]]
+name = "hashbrown"
+version = "0.16.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "841d1cc9bed7f9236f321df977030373f4a4163ae1a7dbfe1a51a2c1a51d9100"
+dependencies = [
+ "allocator-api2",
+ "equivalent",
+ "foldhash",
+]
+
 [[package]]
 name = "hdrhistogram"
 version = "7.5.4"
@@ -5805,7 +5878,7 @@ dependencies = [
  "prost 0.13.3",
  "prost-types 0.13.3",
  "serde",
- "thiserror 2.0.12",
+ "thiserror 2.0.17",
  "tonic 0.13.1",
  "tonic-build 0.13.1",
 ]
@@ -5976,7 +6049,7 @@ dependencies = [
  "iota-transaction-checks",
  "iota-types",
  "itertools 0.13.0",
- "lru",
+ "lru 0.12.4",
  "mockall",
  "moka",
  "more-asserts",
@@ -7354,7 +7427,7 @@ dependencies = [
  "insta",
  "iota-move-build",
  "iota-types",
- "lru",
+ "lru 0.12.4",
  "move-binary-format",
  "move-command-line-common",
  "move-compiler",
@@ -7464,7 +7537,7 @@ dependencies = [
  "iota-transaction-checks",
  "iota-types",
  "jsonrpsee",
- "lru",
+ "lru 0.12.4",
  "move-binary-format",
  "move-bytecode-utils",
  "move-core-types",
@@ -7710,7 +7783,7 @@ dependencies = [
  "serde_repr",
  "serde_with",
  "strum 0.27.2",
- "thiserror 2.0.12",
+ "thiserror 2.0.17",
  "winnow 0.7.11",
 ]
 
@@ -7725,7 +7798,7 @@ dependencies = [
  "iota-framework",
  "iota-move-build",
  "iota-types",
- "lru",
+ "lru 0.12.4",
  "move-package",
  "msim",
  "rand 0.8.5",
@@ -7893,7 +7966,7 @@ dependencies = [
  "iota-test-transaction-builder",
  "iota-types",
  "itertools 0.13.0",
- "lru",
+ "lru 0.12.4",
  "moka",
  "num_enum",
  "object_store 0.10.2",
@@ -8203,7 +8276,7 @@ dependencies = [
  "iota-sdk 1.1.5",
  "iota-sdk-types",
  "itertools 0.13.0",
- "lru",
+ "lru 0.12.4",
  "move-binary-format",
  "move-bytecode-utils",
  "move-core-types",
@@ -8689,7 +8762,7 @@ version = "0.20.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "507460a910eb7b32ee961886ff48539633b788a36b65692b95f225b844c82553"
 dependencies = [
- "regex-automata 0.4.11",
+ "regex-automata",
 ]
 
 [[package]]
@@ -8995,7 +9068,7 @@ dependencies = [
  "lazy_static",
  "proc-macro2",
  "quote",
- "regex-syntax 0.8.6",
+ "regex-syntax",
  "syn 2.0.100",
 ]
 
@@ -9017,6 +9090,15 @@ dependencies = [
  "hashbrown 0.14.5",
 ]
 
+[[package]]
+name = "lru"
+version = "0.16.3"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "a1dc47f592c06f33f8e3aea9591776ec7c9f9e4124778ff8a3c3b87159f7e593"
+dependencies = [
+ "hashbrown 0.16.1",
+]
+
 [[package]]
 name = "lsp-server"
 version = "0.7.7"
@@ -9063,11 +9145,11 @@ dependencies = [
 
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
@@ -10213,6 +10295,15 @@ dependencies = [
  "winapi",
 ]
 
+[[package]]
+name = "nu-ansi-term"
+version = "0.50.3"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "7957b9740744892f114936ab4a57b3f487491bbeafaf8083688b16841a4240e5"
+dependencies = [
+ "windows-sys 0.61.2",
+]
+
 [[package]]
 name = "num"
 version = "0.4.3"
@@ -10313,6 +10404,21 @@ dependencies = [
  "num-traits",
 ]
 
+[[package]]
+name = "num-modular"
+version = "0.6.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "17bb261bf36fa7d83f4c294f834e91256769097b3cb505d44831e0a179ac647f"
+
+[[package]]
+name = "num-order"
+version = "1.2.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "537b596b97c40fcf8056d153049eb22f481c17ebce72a513ec9286e4986d1bb6"
+dependencies = [
+ "num-modular 0.6.1",
+]
+
 [[package]]
 name = "num-prime"
 version = "0.4.4"
@@ -10321,10 +10427,10 @@ checksum = "e238432a7881ec7164503ccc516c014bf009be7984cde1ba56837862543bdec3"
 dependencies = [
  "bitvec 1.0.1",
  "either",
- "lru",
+ "lru 0.12.4",
  "num-bigint 0.4.6",
  "num-integer",
- "num-modular",
+ "num-modular 0.5.1",
  "num-traits",
  "rand 0.8.5",
 ]
@@ -11621,7 +11727,7 @@ dependencies = [
  "memchr",
  "parking_lot 0.12.3",
  "protobuf",
- "thiserror 2.0.12",
+ "thiserror 2.0.17",
 ]
 
 [[package]]
@@ -11672,7 +11778,7 @@ dependencies = [
  "rand 0.8.5",
  "rand_chacha 0.3.1",
  "rand_xorshift",
- "regex-syntax 0.8.6",
+ "regex-syntax",
  "rusty-fork",
  "tempfile",
  "unarray",
@@ -12139,7 +12245,7 @@ dependencies = [
  "indoc",
  "instability",
  "itertools 0.13.0",
- "lru",
+ "lru 0.12.4",
  "paste",
  "strum 0.26.3",
  "unicode-segmentation",
@@ -12296,17 +12402,8 @@ checksum = "8b5288124840bee7b386bc413c487869b360b2b4ec421ea56425128692f2a82c"
 dependencies = [
  "aho-corasick",
  "memchr",
- "regex-automata 0.4.11",
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
@@ -12317,7 +12414,7 @@ checksum = "833eb9ce86d40ef33cb1306d8accf7bc8ec2bfea4355cbdebb3df68b40925cad"
 dependencies = [
  "aho-corasick",
  "memchr",
- "regex-syntax 0.8.6",
+ "regex-syntax",
 ]
 
 [[package]]
@@ -12326,12 +12423,6 @@ version = "0.1.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "53a49587ad06b26609c52e423de037e7f57f20d53535d66e08c695f347df952a"
 
-[[package]]
-name = "regex-syntax"
-version = "0.6.29"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f162c6dd7b008981e4d40210aca20b4bd0f9b60ca9271061b07f78537722f2e1"
-
 [[package]]
 name = "regex-syntax"
 version = "0.8.6"
@@ -13308,15 +13399,16 @@ dependencies = [
 
 [[package]]
 name = "serde_json"
-version = "1.0.128"
+version = "1.0.149"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6ff5456707a1de34e7e37f2a6fd3d3f808c318259cbd01ab6377795054b483d8"
+checksum = "83fc039473c5595ace860d8c4fafa220ff474b3fc6bfdb4293327f1a37e94d86"
 dependencies = [
  "indexmap 2.11.0",
  "itoa",
  "memchr",
- "ryu",
  "serde",
+ "serde_core",
+ "zmij",
 ]
 
 [[package]]
@@ -13777,7 +13869,7 @@ dependencies = [
  "serde",
  "serde_json",
  "snowflake-jwt",
- "thiserror 2.0.12",
+ "thiserror 2.0.17",
  "tokio",
  "url",
  "uuid",
@@ -14639,11 +14731,11 @@ dependencies = [
 
 [[package]]
 name = "thiserror"
-version = "2.0.12"
+version = "2.0.17"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "567b8a2dae586314f7be2a752ec7474332959c6460e02bde30d702a66d488708"
+checksum = "f63587ca0f12b72a0600bcba1d40081f830876000bb46dd2337a3051618f4fc8"
 dependencies = [
- "thiserror-impl 2.0.12",
+ "thiserror-impl 2.0.17",
 ]
 
 [[package]]
@@ -14659,9 +14751,9 @@ dependencies = [
 
 [[package]]
 name = "thiserror-impl"
-version = "2.0.12"
+version = "2.0.17"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7f7cf42b4507d8ea322120659672cf1b9dbb93f8f2d4ecfd6e51350ff5b17a1d"
+checksum = "3ff15c8ecd7de3849db632e14d18d2571fa09dfc5ed93479bc4485c7a517c913"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -15340,9 +15432,9 @@ checksum = "8df9b6e13f2d32c91b9bd719c00d1958837bc7dec474d94952798cc8e69eeec3"
 
 [[package]]
 name = "tracing"
-version = "0.1.40"
+version = "0.1.44"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c3523ab5a71916ccf420eebdf5521fcef02141234bbc0b8a49f2fdc4544364ef"
+checksum = "63e71662fa4b2a2c3a26f570f037eb95bb1f85397f3cd8076caed2f026a6d100"
 dependencies = [
  "log",
  "pin-project-lite",
@@ -15364,9 +15456,9 @@ dependencies = [
 
 [[package]]
 name = "tracing-attributes"
-version = "0.1.27"
+version = "0.1.31"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "34704c8d6ebcbc939824180af020566b01a7c01f80641264eba0999f6c2b6be7"
+checksum = "7490cfa5ec963746568740651ac6781f701c9c5ea257c58e057f3ba8cf69e8da"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -15375,9 +15467,9 @@ dependencies = [
 
 [[package]]
 name = "tracing-core"
-version = "0.1.32"
+version = "0.1.36"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c06d3da6113f116aaee68e4d601191614c9053067f9ab7f6edbcb161237daa54"
+checksum = "db97caf9d906fbde555dd62fa95ddba9eecfd14cb388e4f491a66d74cd5fb79a"
 dependencies = [
  "once_cell",
  "valuable",
@@ -15436,24 +15528,24 @@ dependencies = [
 
 [[package]]
 name = "tracing-serde"
-version = "0.1.3"
+version = "0.2.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "bc6b213177105856957181934e4920de57730fc69bf42c37ee5bb664d406d9e1"
+checksum = "704b1aeb7be0d0a84fc9828cae51dab5970fee5088f83d1dd7ee6f6246fc6ff1"
 dependencies = [
  "serde",
  "tracing-core",
 ]
 
 [[package]]
 name = "tracing-subscriber"
-version = "0.3.18"
+version = "0.3.22"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "ad0f048c97dbd9faa9b7df56362b8ebcaa52adb06b498c050d2f4e32f90a7a8b"
+checksum = "2f30143827ddab0d256fd843b7a66d164e9f271cfa0dde49142c5ca0ca291f1e"
 dependencies = [
  "matchers",
- "nu-ansi-term",
+ "nu-ansi-term 0.50.3",
  "once_cell",
- "regex",
+ "regex-automata",
  "serde",
  "serde_json",
  "sharded-slab",
@@ -15534,7 +15626,7 @@ dependencies = [
  "log",
  "rand 0.9.2",
  "sha1",
- "thiserror 2.0.12",
+ "thiserror 2.0.17",
  "utf-8",
 ]
 
@@ -16696,7 +16788,7 @@ dependencies = [
  "nom",
  "oid-registry",
  "rusticata-macros",
- "thiserror 2.0.12",
+ "thiserror 2.0.17",
  "time",
 ]
 
@@ -16894,6 +16986,12 @@ dependencies = [
  "zopfli",
 ]
 
+[[package]]
+name = "zmij"
+version = "1.0.13"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "ac93432f5b761b22864c774aac244fa5c0fd877678a4c37ebf6cf42208f9c9ec"
+
 [[package]]
 name = "zopfli"
 version = "0.8.1"
```

### Cargo.toml
```diff
@@ -233,7 +233,7 @@ anemo-build = { git = "https://github.com/mystenlabs/anemo.git", rev = "c4e7e4cb
 anemo-tower = { git = "https://github.com/mystenlabs/anemo.git", rev = "c4e7e4cb4b624d7738c2016d7b7885c6774ff9c2" }
 anyhow = "1.0.71"
 arc-swap = { version = "1.5.1", features = ["serde"] }
-async-graphql = "7.0.17"
+async-graphql = { version = "7.1.0", default-features = false }
 async-recursion = "1.0.4"
 async-stream = "0.3.6"
 async-trait = "0.1.61"
@@ -341,7 +341,7 @@ schemars = { version = "0.8.21", features = ["either"] }
 scopeguard = "1.1"
 serde = { version = "1.0.144", features = ["derive", "rc"] }
 serde-reflection = "0.5"
-serde_json = { version = "1.0.95", features = ["preserve_order"] }
+serde_json = { version = "1.0.149", features = ["preserve_order"] }
 serde_spanned = "0.6.8"
 serde_with = "3.8"
 serde_yaml = "0.8.26"
@@ -376,8 +376,8 @@ tonic-prost-build = "0.14"
 tonic-rustls = "0.3.0"
 tower = { version = "0.4.12", features = ["full", "util", "timeout", "load-shed", "limit"] }
 tower-http = { version = "0.5", features = ["cors", "full", "trace", "set-header", "propagate-header"] }
-tracing = "0.1.37"
-tracing-subscriber = { version = "0.3.15", default-features = false, features = ["std", "smallvec", "fmt", "ansi", "time", "json", "registry", "env-filter"] }
+tracing = "0.1.44"
+tracing-subscriber = { version = "0.3.22", default-features = false, features = ["std", "smallvec", "fmt", "ansi", "time", "json", "registry", "env-filter"] }
 unescape = "0.1.0"
 url = "2.3.1"
 uuid = { version = "1.1.2", features = ["v4", "fast-rng"] }
```

### crates/iota-core/src/execution_cache/passthrough_cache.rs
```diff
@@ -258,8 +258,8 @@ impl TransactionCacheRead for PassthroughCache {
 
 impl ExecutionCacheWrite for PassthroughCache {
     #[instrument(level = "debug", skip_all)]
-    fn try_write_transaction_outputs<'a>(
-        &'a self,
+    fn try_write_transaction_outputs(
+        &self,
         epoch_id: EpochId,
         tx_outputs: Arc<TransactionOutputs>,
     ) -> IotaResult {
```

### crates/iota-genesis-builder/Cargo.toml
```diff
@@ -35,7 +35,7 @@ serde_yaml.workspace = true
 tempfile.workspace = true
 tokio.workspace = true
 tracing.workspace = true
-tracing-subscriber = "0.3"
+tracing-subscriber.workspace = true
 
 # internal dependencies
 iota-adapter-latest = { path = "../../iota-execution/latest/iota-adapter/" }
```

### crates/iota-graphql-e2e-tests/tests/call/checkpoint_connection_pagination.snap
```diff
@@ -12,10 +12,6 @@ task 2, lines 34-46:
 Response: {
   "data": {
     "checkpoints": {
-      "pageInfo": {
-        "hasPreviousPage": true,
-        "hasNextPage": true
-      },
       "edges": [
         {
           "cursor": "eyJjIjoxMiwicyI6N30",
@@ -41,7 +37,11 @@ Response: {
             "sequenceNumber": 10
           }
         }
-      ]
+      ],
+      "pageInfo": {
+        "hasNextPage": true,
+        "hasPreviousPage": true
+      }
     }
   }
 }
@@ -51,18 +51,18 @@ task 3, lines 48-60:
 Response: {
   "data": {
     "checkpoints": {
-      "pageInfo": {
-        "hasPreviousPage": true,
-        "hasNextPage": true
-      },
       "edges": [
         {
           "cursor": "eyJjIjoxMiwicyI6N30",
           "node": {
             "sequenceNumber": 7
           }
         }
-      ]
+      ],
+      "pageInfo": {
+        "hasNextPage": true,
+        "hasPreviousPage": true
+      }
     }
   }
 }
@@ -72,10 +72,6 @@ task 4, lines 62-74:
 Response: {
   "data": {
     "checkpoints": {
-      "pageInfo": {
-        "hasPreviousPage": false,
-        "hasNextPage": true
-      },
       "edges": [
         {
           "cursor": "eyJjIjoxMiwicyI6MH0",
@@ -101,7 +97,11 @@ Response: {
             "sequenceNumber": 3
           }
         }
-      ]
+      ],
+      "pageInfo": {
+        "hasNextPage": true,
+        "hasPreviousPage": false
+      }
     }
   }
 }
@@ -111,10 +111,6 @@ task 5, lines 76-88:
 Response: {
   "data": {
     "checkpoints": {
-      "pageInfo": {
-        "hasPreviousPage": true,
-        "hasNextPage": true
-      },
       "edges": [
         {
           "cursor": "eyJjIjoxMiwicyI6NH0",
@@ -128,7 +124,11 @@ Response: {
             "sequenceNumber": 5
           }
         }
-      ]
+      ],
+      "pageInfo": {
+        "hasNextPage": true,
+        "hasPreviousPage": true
+      }
     }
   }
 }
@@ -138,10 +138,6 @@ task 6, lines 90-102:
 Response: {
   "data": {
     "checkpoints": {
-      "pageInfo": {
-        "hasPreviousPage": false,
-        "hasNextPage": true
-      },
       "edges": [
         {
           "cursor": "eyJjIjoxMiwicyI6MH0",
@@ -161,7 +157,11 @@ Response: {
             "sequenceNumber": 2
           }
         }
-      ]
+      ],
+      "pageInfo": {
+        "hasNextPage": true,
+        "hasPreviousPage": false
+      }
     }
   }
 }
@@ -171,10 +171,6 @@ task 7, lines 104-116:
 Response: {
   "data": {
     "checkpoints": {
-      "pageInfo": {
-        "hasPreviousPage": true,
-        "hasNextPage": false
-      },
       "edges": [
         {
           "cursor": "eyJjIjoxMiwicyI6OX0",
@@ -200,7 +196,11 @@ Response: {
             "sequenceNumber": 12
           }
         }
-      ]
+      ],
+      "pageInfo": {
+        "hasNextPage": false,
+        "hasPreviousPage": true
+      }
     }
   }
 }
@@ -210,10 +210,6 @@ task 8, lines 118-130:
 Response: {
   "data": {
     "checkpoints": {
-      "pageInfo": {
-        "hasPreviousPage": false,
-        "hasNextPage": true
-      },
       "edges": [
         {
           "cursor": "eyJjIjoxMiwicyI6MH0",
@@ -239,7 +235,11 @@ Response: {
             "sequenceNumber": 3
           }
         }
-      ]
+      ],
+      "pageInfo": {
+        "hasNextPage": true,
+        "hasPreviousPage": false
+      }
     }
   }
 }
@@ -249,10 +249,6 @@ task 9, lines 132-144:
 Response: {
   "data": {
     "checkpoints": {
-      "pageInfo": {
-        "hasPreviousPage": true,
-        "hasNextPage": false
-      },
       "edges": [
         {
           "cursor": "eyJjIjoxMiwicyI6NX0",
@@ -302,7 +298,11 @@ Response: {
             "sequenceNumber": 12
           }
         }
-      ]
+      ],
+      "pageInfo": {
+        "hasNextPage": false,
+        "hasPreviousPage": true
+      }
     }
   }
 }
@@ -312,10 +312,6 @@ task 10, lines 146-158:
 Response: {
   "data": {
     "checkpoints": {
-      "pageInfo": {
-        "hasPreviousPage": true,
-        "hasNextPage": true
-      },
       "edges": [
         {
           "cursor": "eyJjIjoxMiwicyI6Mn0",
@@ -341,7 +337,11 @@ Response: {
             "sequenceNumber": 5
           }
         }
-      ]
+      ],
+      "pageInfo": {
+        "hasNextPage": true,
+        "hasPreviousPage": true
+      }
     }
   }
 }
@@ -351,10 +351,6 @@ task 11, lines 160-172:
 Response: {
   "data": {
     "checkpoints": {
-      "pageInfo": {
-        "hasPreviousPage": true,
-        "hasNextPage": true
-      },
       "edges": [
         {
           "cursor": "eyJjIjoxMiwicyI6NH0",
@@ -368,7 +364,11 @@ Response: {
             "sequenceNumber": 5
           }
         }
-      ]
+      ],
+      "pageInfo": {
+        "hasNextPage": true,
+        "hasPreviousPage": true
+      }
     }
   }
 }
@@ -378,10 +378,6 @@ task 12, lines 174-186:
 Response: {
   "data": {
     "checkpoints": {
-      "pageInfo": {
-        "hasPreviousPage": true,
-        "hasNextPage": false
-      },
       "edges": [
         {
           "cursor": "eyJjIjoxMiwicyI6MTB9",
@@ -401,7 +397,11 @@ Response: {
             "sequenceNumber": 12
           }
         }
-      ]
+      ],
+      "pageInfo": {
+        "hasNextPage": false,
+        "hasPreviousPage": true
+      }
     }
   }
 }
@@ -411,10 +411,6 @@ task 13, lines 188-200:
 Response: {
   "data": {
     "checkpoints": {
-      "pageInfo": {
-        "hasPreviousPage": false,
-        "hasNextPage": false
-      },
       "edges": [
         {
           "cursor": "eyJjIjoxMiwicyI6MH0",
@@ -494,7 +490,11 @@ Response: {
             "sequenceNumber": 12
           }
         }
-      ]
+      ],
+      "pageInfo": {
+        "hasNextPage": false,
+        "hasPreviousPage": false
+      }
     }
   }
 }
@@ -504,10 +504,6 @@ task 14, lines 202-214:
 Response: {
   "data": {
     "checkpoints": {
-      "pageInfo": {
-        "hasPreviousPage": false,
-        "hasNextPage": true
-      },
       "edges": [
         {
           "cursor": "eyJjIjoxMiwicyI6MH0",
@@ -533,7 +529,11 @@ Response: {
             "sequenceNumber": 3
           }
         }
-      ]
+      ],
+      "pageInfo": {
+        "hasNextPage": true,
+        "hasPreviousPage": false
+      }
     }
   }
 }
@@ -543,10 +543,6 @@ task 15, lines 216-228:
 Response: {
   "data": {
     "checkpoints": {
-      "pageInfo": {
-        "hasPreviousPage": true,
-        "hasNextPage": false
-      },
       "edges": [
         {
           "cursor": "eyJjIjoxMiwicyI6OX0",
@@ -572,7 +568,11 @@ Response: {
             "sequenceNumber": 12
           }
         }
-      ]
+      ],
+      "pageInfo": {
+        "hasNextPage": false,
+        "hasPreviousPage": true
+      }
     }
   }
 }
```

### crates/iota-graphql-e2e-tests/tests/call/coin_metadata.snap
```diff
@@ -22,11 +22,11 @@ Response: {
   "data": {
     "coinMetadata": {
       "decimals": 2,
-      "name": "",
-      "symbol": "FAKE",
       "description": "",
       "iconUrl": null,
-      "supply": "0"
+      "name": "",
+      "supply": "0",
+      "symbol": "FAKE"
     }
   }
 }
@@ -50,11 +50,11 @@ Response: {
   "data": {
     "coinMetadata": {
       "decimals": 2,
-      "name": "",
-      "symbol": "FAKE",
       "description": "",
       "iconUrl": null,
-      "supply": "100"
+      "name": "",
+      "supply": "100",
+      "symbol": "FAKE"
     }
   }
 }
```

### crates/iota-graphql-e2e-tests/tests/call/dynamic_fields.snap
```diff
@@ -43,55 +43,55 @@ Response: {
         "nodes": [
           {
             "name": {
-              "type": {
-                "repr": "u64"
-              },
+              "bcs": "AAAAAAAAAAA=",
               "data": {
                 "Number": "0"
               },
-              "bcs": "AAAAAAAAAAA="
+              "type": {
+                "repr": "u64"
+              }
             },
             "value": {
               "__typename": "MoveObject"
             }
           },
           {
             "name": {
-              "type": {
-                "repr": "u64"
-              },
+              "bcs": "AAAAAAAAAAA=",
               "data": {
                 "Number": "0"
               },
-              "bcs": "AAAAAAAAAAA="
+              "type": {
+                "repr": "u64"
+              }
             },
             "value": {
               "__typename": "MoveValue"
             }
           },
           {
             "name": {
-              "type": {
-                "repr": "vector<u8>"
-              },
+              "bcs": "AA==",
               "data": {
                 "Vector": []
               },
-              "bcs": "AA=="
+              "type": {
+                "repr": "vector<u8>"
+              }
             },
             "value": {
               "__typename": "MoveValue"
             }
           },
           {
             "name": {
-              "type": {
-                "repr": "bool"
-              },
+              "bcs": "AA==",
               "data": {
                 "Bool": false
               },
-              "bcs": "AA=="
+              "type": {
+                "repr": "bool"
+              }
             },
             "value": {
               "__typename": "MoveValue"
@@ -123,55 +123,55 @@ Response: {
         "nodes": [
           {
             "name": {
-              "type": {
-                "repr": "u64"
-              },
+              "bcs": "AAAAAAAAAAA=",
               "data": {
                 "Number": "0"
               },
-              "bcs": "AAAAAAAAAAA="
+              "type": {
+                "repr": "u64"
+              }
             },
             "value": {
               "__typename": "MoveObject"
             }
           },
           {
             "name": {
-              "type": {
-                "repr": "u64"
-              },
+              "bcs": "AAAAAAAAAAA=",
               "data": {
                 "Number": "0"
               },
-              "bcs": "AAAAAAAAAAA="
+              "type": {
+                "repr": "u64"
+              }
             },
             "value": {
               "__typename": "MoveValue"
             }
           },
           {
             "name": {
-              "type": {
-                "repr": "vector<u8>"
-              },
+              "bcs": "AA==",
               "data": {
                 "Vector": []
               },
-              "bcs": "AA=="
+              "type": {
+                "repr": "vector<u8>"
+              }
             },
             "value": {
               "__typename": "MoveValue"
             }
           },
           {
             "name": {
-              "type": {
-                "repr": "bool"
-              },
+              "bcs": "AA==",
               "data": {
                 "Bool": false
               },
-              "bcs": "AA=="
+              "type": {
+                "repr": "bool"
+              }
             },
             "value": {
               "__typename": "MoveValue"
@@ -192,70 +192,70 @@ Response: {
         "nodes": [
           {
             "name": {
-              "type": {
-                "repr": "u64"
-              },
+              "bcs": "AAAAAAAAAAA=",
               "data": {
                 "Number": "0"
               },
-              "bcs": "AAAAAAAAAAA="
+              "type": {
+                "repr": "u64"
+              }
             },
             "value": {
               "__typename": "MoveObject"
             }
           },
           {
             "name": {
-              "type": {
-                "repr": "u64"
-              },
+              "bcs": "AAAAAAAAAAA=",
               "data": {
                 "Number": "0"
               },
-              "bcs": "AAAAAAAAAAA="
+              "type": {
+                "repr": "u64"
+              }
             },
             "value": {
+              "__typename": "MoveValue",
               "bcs": "AAAAAAAAAAA=",
               "data": {
                 "Number": "0"
-              },
-              "__typename": "MoveValue"
+              }
             }
           },
           {
             "name": {
-              "type": {
-                "repr": "vector<u8>"
-              },
+              "bcs": "AA==",
               "data": {
                 "Vector": []
               },
-              "bcs": "AA=="
+              "type": {
+                "repr": "vector<u8>"
+              }
             },
             "value": {
+              "__typename": "MoveValue",
               "bcs": "AQAAAAAAAAA=",
               "data": {
                 "Number": "1"
-              },
-              "__typename": "MoveValue"
+              }
             }
           },
           {
             "name": {
-              "type": {
-                "repr": "bool"
-              },
+              "bcs": "AA==",
               "data": {
                 "Bool": false
               },
-              "bcs": "AA=="
+              "type": {
+                "repr": "bool"
+              }
             },
             "value": {
+              "__typename": "MoveValue",
               "bcs": "AgAAAAAAAAA=",
               "data": {
                 "Number": "2"
-              },
-              "__typename": "MoveValue"
+              }
             }
           }
         ]
@@ -271,13 +271,13 @@ Response: {
     "owner": {
       "dynamicField": {
         "name": {
-          "type": {
-            "repr": "u64"
-          },
+          "bcs": "AAAAAAAAAAA=",
           "data": {
             "Number": "0"
           },
-          "bcs": "AAAAAAAAAAA="
+          "type": {
+            "repr": "u64"
+          }
         },
         "value": {
           "__typename": "MoveValue",
```

### crates/iota-graphql-e2e-tests/tests/call/simple.snap
```diff
@@ -178,6 +178,15 @@ Response: {
         "edges": []
       }
     },
+    "object": {
+      "owner": {
+        "__typename": "AddressOwner",
+        "owner": {
+          "address": "0x0000000000000000000000000000000000000000000000000000000000000042"
+        }
+      },
+      "version": 3
+    },
     "second": {
       "objects": {
         "edges": [
@@ -306,15 +315,6 @@ Response: {
           }
         ]
       }
-    },
-    "object": {
-      "version": 3,
-      "owner": {
-        "__typename": "AddressOwner",
-        "owner": {
-          "address": "0x0000000000000000000000000000000000000000000000000000000000000042"
-        }
-      }
     }
   }
 }
@@ -323,6 +323,9 @@ task 20, lines 152-168:
 //# run-graphql
 Response: {
   "data": {
+    "address": {
+      "address": "0x28f02a953f3553f51a9365593c7d4bd0643d2085f004b18c6ca9de51682b2c80"
+    },
     "epoch": {
       "validatorSet": {
         "activeValidators": {
@@ -335,9 +338,6 @@ Response: {
           ]
         }
       }
-    },
-    "address": {
-      "address": "0x28f02a953f3553f51a9365593c7d4bd0643d2085f004b18c6ca9de51682b2c80"
     }
   }
 }
```

### crates/iota-graphql-e2e-tests/tests/consistency/balances.snap
```diff
@@ -69,26 +69,26 @@ Response: {
       "nodes": [
         {
           "sender": {
-            "fakeCoinBalance": {
-              "totalBalance": "700"
-            },
             "allBalances": {
               "nodes": [
                 {
+                  "coinObjectCount": 1,
                   "coinType": {
                     "repr": "0x0000000000000000000000000000000000000000000000000000000000000002::iota::IOTA"
                   },
-                  "coinObjectCount": 1,
                   "totalBalance": "299999982382000"
                 },
                 {
+                  "coinObjectCount": 3,
                   "coinType": {
                     "repr": "0x97a73654d6f792c4f911e41da7099fa0ba3c9fd820112a3772c282cca96e98ab::fake::FAKE"
                   },
-                  "coinObjectCount": 3,
                   "totalBalance": "700"
                 }
               ]
+            },
+            "fakeCoinBalance": {
+              "totalBalance": "700"
             }
           }
         }
@@ -105,26 +105,26 @@ Response: {
       "nodes": [
         {
           "sender": {
-            "fakeCoinBalance": {
-              "totalBalance": "600"
-            },
             "allBalances": {
               "nodes": [
                 {
+                  "coinObjectCount": 1,
                   "coinType": {
                     "repr": "0x0000000000000000000000000000000000000000000000000000000000000002::iota::IOTA"
                   },
-                  "coinObjectCount": 1,
                   "totalBalance": "299999981382000"
                 },
                 {
+                  "coinObjectCount": 2,
                   "coinType": {
                     "repr": "0x97a73654d6f792c4f911e41da7099fa0ba3c9fd820112a3772c282cca96e98ab::fake::FAKE"
                   },
-                  "coinObjectCount": 2,
                   "totalBalance": "600"
                 }
               ]
+            },
+            "fakeCoinBalance": {
+              "totalBalance": "600"
             }
           }
         }
@@ -141,26 +141,26 @@ Response: {
       "nodes": [
         {
           "sender": {
-            "fakeCoinBalance": {
-              "totalBalance": "400"
-            },
             "allBalances": {
               "nodes": [
                 {
+                  "coinObjectCount": 1,
                   "coinType": {
                     "repr": "0x0000000000000000000000000000000000000000000000000000000000000002::iota::IOTA"
                   },
-                  "coinObjectCount": 1,
                   "totalBalance": "299999980382000"
                 },
                 {
+                  "coinObjectCount": 1,
                   "coinType": {
                     "repr": "0x97a73654d6f792c4f911e41da7099fa0ba3c9fd820112a3772c282cca96e98ab::fake::FAKE"
                   },
-                  "coinObjectCount": 1,
                   "totalBalance": "400"
                 }
               ]
+            },
+            "fakeCoinBalance": {
+              "totalBalance": "400"
             }
           }
         }
@@ -181,26 +181,26 @@ Response: {
       "nodes": [
         {
           "sender": {
-            "fakeCoinBalance": {
-              "totalBalance": "700"
-            },
             "allBalances": {
               "nodes": [
                 {
+                  "coinObjectCount": 1,
                   "coinType": {
                     "repr": "0x0000000000000000000000000000000000000000000000000000000000000002::iota::IOTA"
                   },
-                  "coinObjectCount": 1,
                   "totalBalance": "299999982382000"
                 },
                 {
+                  "coinObjectCount": 3,
                   "coinType": {
                     "repr": "0x97a73654d6f792c4f911e41da7099fa0ba3c9fd820112a3772c282cca96e98ab::fake::FAKE"
                   },
-                  "coinObjectCount": 3,
                   "totalBalance": "700"
                 }
               ]
+            },
+            "fakeCoinBalance": {
+              "totalBalance": "700"
             }
           }
         }
@@ -217,26 +217,26 @@ Response: {
       "nodes": [
         {
           "sender": {
-            "fakeCoinBalance": {
-              "totalBalance": "600"
-            },
             "allBalances": {
               "nodes": [
                 {
+                  "coinObjectCount": 1,
                   "coinType": {
                     "repr": "0x0000000000000000000000000000000000000000000000000000000000000002::iota::IOTA"
                   },
-                  "coinObjectCount": 1,
                   "totalBalance": "299999981382000"
                 },
                 {
+                  "coinObjectCount": 2,
                   "coinType": {
                     "repr": "0x97a73654d6f792c4f911e41da7099fa0ba3c9fd820112a3772c282cca96e98ab::fake::FAKE"
                   },
-                  "coinObjectCount": 2,
                   "totalBalance": "600"
                 }
               ]
+            },
+            "fakeCoinBalance": {
+              "totalBalance": "600"
             }
           }
         }
@@ -253,26 +253,26 @@ Response: {
       "nodes": [
         {
           "sender": {
-            "fakeCoinBalance": {
-              "totalBalance": "400"
-            },
             "allBalances": {
               "nodes": [
                 {
+                  "coinObjectCount": 1,
                   "coinType": {
                     "repr": "0x0000000000000000000000000000000000000000000000000000000000000002::iota::IOTA"
                   },
-                  "coinObjectCount": 1,
                   "totalBalance": "299999980382000"
                 },
                 {
+                  "coinObjectCount": 1,
                   "coinType": {
                     "repr": "0x97a73654d6f792c4f911e41da7099fa0ba3c9fd820112a3772c282cca96e98ab::fake::FAKE"
                   },
-                  "coinObjectCount": 1,
                   "totalBalance": "400"
                 }
               ]
+            },
+            "fakeCoinBalance": {
+              "totalBalance": "400"
             }
           }
         }
@@ -304,7 +304,9 @@ Response: {
     "transactionBlocks": {
       "nodes": [
         {
-          "sender": null
+          "sender": {
+            "fakeCoinBalance": null
+          }
         }
       ]
     }
@@ -340,26 +342,26 @@ Response: {
       "nodes": [
         {
           "sender": {
-            "fakeCoinBalance": {
-              "totalBalance": "600"
-            },
             "allBalances": {
               "nodes": [
                 {
+                  "coinObjectCount": 1,
                   "coinType": {
                     "repr": "0x0000000000000000000000000000000000000000000000000000000000000002::iota::IOTA"
                   },
-                  "coinObjectCount": 1,
                   "totalBalance": "299999981382000"
                 },
                 {
+                  "coinObjectCount": 2,
                   "coinType": {
                     "repr": "0x97a73654d6f792c4f911e41da7099fa0ba3c9fd820112a3772c282cca96e98ab::fake::FAKE"
                   },
-                  "coinObjectCount": 2,
                   "totalBalance": "600"
                 }
               ]
+            },
+            "fakeCoinBalance": {
+              "totalBalance": "600"
             }
           }
         }
@@ -376,26 +378,26 @@ Response: {
       "nodes": [
         {
           "sender": {
-            "fakeCoinBalance": {
-              "totalBalance": "400"
-            },
             "allBalances": {
               "nodes": [
                 {
+                  "coinObjectCount": 1,
                   "coinType": {
                     "repr": "0x0000000000000000000000000000000000000000000000000000000000000002::iota::IOTA"
                   },
-                  "coinObjectCount": 1,
                   "totalBalance": "299999980382000"
                 },
                 {
+                  "coinObjectCount": 1,
                   "coinType": {
                     "repr": "0x97a73654d6f792c4f911e41da7099fa0ba3c9fd820112a3772c282cca96e98ab::fake::FAKE"
                   },
-                  "coinObjectCount": 1,
                   "totalBalance": "400"
                 }
               ]
+            },
+            "fakeCoinBalance": {
+              "totalBalance": "400"
             }
           }
         }
@@ -435,7 +437,9 @@ Response: {
     "transactionBlocks": {
       "nodes": [
         {
-          "sender": null
+          "sender": {
+            "fakeCoinBalance": null
+          }
         }
       ]
     }
@@ -478,7 +482,9 @@ Response: {
     "transactionBlocks": {
       "nodes": [
         {
-          "sender": null
+          "sender": {
+            "fakeCoinBalance": null
+          }
         }
       ]
     }
@@ -521,7 +527,9 @@ Response: {
     "transactionBlocks": {
       "nodes": [
         {
-          "sender": null
+          "sender": {
+            "fakeCoinBalance": null
+          }
         }
       ]
     }
```

### crates/iota-graphql-e2e-tests/tests/consistency/checkpoints/transaction_blocks.snap
```diff
@@ -258,9 +258,7 @@ Response: {
     "checkpoints": {
       "nodes": [
         {
-          "sequenceNumber": 0,
           "epoch": {
-            "epochId": 0,
             "checkpoints": {
               "nodes": [
                 {
@@ -276,13 +274,13 @@ Response: {
                   "sequenceNumber": 3
                 }
               ]
-            }
-          }
+            },
+            "epochId": 0
+          },
+          "sequenceNumber": 0
         },
         {
-          "sequenceNumber": 1,
           "epoch": {
-            "epochId": 0,
             "checkpoints": {
               "nodes": [
                 {
@@ -298,13 +296,13 @@ Response: {
                   "sequenceNumber": 3
                 }
               ]
-            }
-          }
+            },
+            "epochId": 0
+          },
+          "sequenceNumber": 1
         },
         {
-          "sequenceNumber": 2,
           "epoch": {
-            "epochId": 0,
             "checkpoints": {
               "nodes": [
                 {
@@ -320,13 +318,13 @@ Response: {
                   "sequenceNumber": 3
                 }
               ]
-            }
-          }
+            },
+            "epochId": 0
+          },
+          "sequenceNumber": 2
         },
         {
-          "sequenceNumber": 3,
           "epoch": {
-            "epochId": 0,
             "checkpoints": {
               "nodes": [
                 {
@@ -342,8 +340,10 @@ Response: {
                   "sequenceNumber": 3
                 }
               ]
-            }
-          }
+            },
+            "epochId": 0
+          },
+          "sequenceNumber": 3
         }
       ]
     }
```

### crates/iota-graphql-e2e-tests/tests/consistency/coins.snap
```diff
@@ -32,47 +32,47 @@ Response: {
     "coins": {
       "nodes": [
         {
-          "owner": {
-            "owner": {
-              "address": "0x8cca4e1ce0ba5904cea61df9242da2f7d29e3ef328fb7ec07c086b3bf47ca61a"
-            }
-          },
           "contents": {
             "json": {
-              "id": "0x8465562a80b8701abde792175fbfc4ff032b68eb6e160c17931459549ea204ab",
               "balance": {
                 "value": "300"
-              }
+              },
+              "id": "0x8465562a80b8701abde792175fbfc4ff032b68eb6e160c17931459549ea204ab"
             }
-          }
-        },
-        {
+          },
           "owner": {
             "owner": {
               "address": "0x8cca4e1ce0ba5904cea61df9242da2f7d29e3ef328fb7ec07c086b3bf47ca61a"
             }
-          },
+          }
+        },
+        {
           "contents": {
             "json": {
-              "id": "0xa461d4dde3d736c3cf3b8faa49973802987ccb143c5f9f7df0437a4ebba9f5ff",
               "balance": {
                 "value": "100"
-              }
+              },
+              "id": "0xa461d4dde3d736c3cf3b8faa49973802987ccb143c5f9f7df0437a4ebba9f5ff"
             }
-          }
-        },
-        {
+          },
           "owner": {
             "owner": {
               "address": "0x8cca4e1ce0ba5904cea61df9242da2f7d29e3ef328fb7ec07c086b3bf47ca61a"
             }
-          },
+          }
+        },
+        {
           "contents": {
             "json": {
-              "id": "0xc32a65f3c1b1b5376f5e1515a17f558968dd2d5316e58a29877cc7e49610bea1",
               "balance": {
                 "value": "200"
-              }
+              },
+              "id": "0xc32a65f3c1b1b5376f5e1515a17f558968dd2d5316e58a29877cc7e49610bea1"
+            }
+          },
+          "owner": {
+            "owner": {
+              "address": "0x8cca4e1ce0ba5904cea61df9242da2f7d29e3ef328fb7ec07c086b3bf47ca61a"
             }
           }
         }
@@ -112,47 +112,47 @@ Response: {
     "coins": {
       "nodes": [
         {
-          "owner": {
-            "owner": {
-              "address": "0x8cca4e1ce0ba5904cea61df9242da2f7d29e3ef328fb7ec07c086b3bf47ca61a"
-            }
-          },
           "contents": {
             "json": {
-              "id": "0x8465562a80b8701abde792175fbfc4ff032b68eb6e160c17931459549ea204ab",
               "balance": {
                 "value": "300"
-              }
+              },
+              "id": "0x8465562a80b8701abde792175fbfc4ff032b68eb6e160c17931459549ea204ab"
             }
-          }
-        },
-        {
+          },
           "owner": {
             "owner": {
               "address": "0x8cca4e1ce0ba5904cea61df9242da2f7d29e3ef328fb7ec07c086b3bf47ca61a"
             }
-          },
+          }
+        },
+        {
           "contents": {
             "json": {
-              "id": "0xa461d4dde3d736c3cf3b8faa49973802987ccb143c5f9f7df0437a4ebba9f5ff",
               "balance": {
                 "value": "100"
-              }
+              },
+              "id": "0xa461d4dde3d736c3cf3b8faa49973802987ccb143c5f9f7df0437a4ebba9f5ff"
             }
-          }
-        },
-        {
+          },
           "owner": {
             "owner": {
               "address": "0x8cca4e1ce0ba5904cea61df9242da2f7d29e3ef328fb7ec07c086b3bf47ca61a"
             }
-          },
+          }
+        },
+        {
           "contents": {
             "json": {
-              "id": "0xc32a65f3c1b1b5376f5e1515a17f558968dd2d5316e58a29877cc7e49610bea1",
               "balance": {
                 "value": "200"
-              }
+              },
+              "id": "0xc32a65f3c1b1b5376f5e1515a17f558968dd2d5316e58a29877cc7e49610bea1"
+            }
+          },
+          "owner": {
+            "owner": {
+              "address": "0x8cca4e1ce0ba5904cea61df9242da2f7d29e3ef328fb7ec07c086b3bf47ca61a"
             }
           }
         }
@@ -192,47 +192,47 @@ Response: {
     "coins": {
       "nodes": [
         {
-          "owner": {
-            "owner": {
-              "address": "0x8cca4e1ce0ba5904cea61df9242da2f7d29e3ef328fb7ec07c086b3bf47ca61a"
-            }
-          },
           "contents": {
             "json": {
-              "id": "0x8465562a80b8701abde792175fbfc4ff032b68eb6e160c17931459549ea204ab",
               "balance": {
                 "value": "300"
-              }
+              },
+              "id": "0x8465562a80b8701abde792175fbfc4ff032b68eb6e160c17931459549ea204ab"
             }
-          }
-        },
-        {
+          },
           "owner": {
             "owner": {
-              "address": "0x28f02a953f3553f51a9365593c7d4bd0643d2085f004b18c6ca9de51682b2c80"
+              "address": "0x8cca4e1ce0ba5904cea61df9242da2f7d29e3ef328fb7ec07c086b3bf47ca61a"
             }
-          },
+          }
+        },
+        {
           "contents": {
             "json": {
-              "id": "0xa461d4dde3d736c3cf3b8faa49973802987ccb143c5f9f7df0437a4ebba9f5ff",
               "balance": {
                 "value": "100"
-              }
+              },
+              "id": "0xa461d4dde3d736c3cf3b8faa49973802987ccb143c5f9f7df0437a4ebba9f5ff"
             }
-          }
-        },
-        {
+          },
           "owner": {
             "owner": {
               "address": "0x28f02a953f3553f51a9365593c7d4bd0643d2085f004b18c6ca9de51682b2c80"
             }
-          },
+          }
+        },
+        {
           "contents": {
             "json": {
-              "id": "0xc32a65f3c1b1b5376f5e1515a17f558968dd2d5316e58a29877cc7e49610bea1",
               "balance": {
                 "value": "200"
-              }
+              },
+              "id": "0xc32a65f3c1b1b5376f5e1515a17f558968dd2d5316e58a29877cc7e49610bea1"
+            }
+          },
+          "owner": {
+            "owner": {
+              "address": "0x28f02a953f3553f51a9365593c7d4bd0643d2085f004b18c6ca9de51682b2c80"
             }
           }
         }
@@ -256,34 +256,34 @@ Response: {
     "coins": {
       "nodes": [
         {
-          "owner": {
-            "owner": {
-              "address": "0x8cca4e1ce0ba5904cea61df9242da2f7d29e3ef328fb7ec07c086b3bf47ca61a"
-            }
-          },
           "address": "0xa461d4dde3d736c3cf3b8faa49973802987ccb143c5f9f7df0437a4ebba9f5ff",
           "contents": {
             "json": {
-              "id": "0xa461d4dde3d736c3cf3b8faa49973802987ccb143c5f9f7df0437a4ebba9f5ff",
               "balance": {
                 "value": "100"
-              }
+              },
+              "id": "0xa461d4dde3d736c3cf3b8faa49973802987ccb143c5f9f7df0437a4ebba9f5ff"
             }
-          }
-        },
-        {
+          },
           "owner": {
             "owner": {
               "address": "0x8cca4e1ce0ba5904cea61df9242da2f7d29e3ef328fb7ec07c086b3bf47ca61a"
             }
-          },
+          }
+        },
+        {
           "address": "0xc32a65f3c1b1b5376f5e1515a17f558968dd2d5316e58a29877cc7e49610bea1",
           "contents": {
             "json": {
-              "id": "0xc32a65f3c1b1b5376f5e1515a17f558968dd2d5316e58a29877cc7e49610bea1",
               "balance": {
                 "value": "200"
-              }
+              },
+              "id": "0xc32a65f3c1b1b5376f5e1515a17f558968dd2d5316e58a29877cc7e49610bea1"
+            }
+          },
+          "owner": {
+            "owner": {
+              "address": "0x8cca4e1ce0ba5904cea61df9242da2f7d29e3ef328fb7ec07c086b3bf47ca61a"
             }
           }
         }
@@ -295,7 +295,16 @@ Response: {
 task 13, lines 166-192:
 //# run-graphql --cursors bcs(@{obj_1_1},1)
 Response: {
-  "data": null,
+  "data": {
+    "availableRange": {
+      "first": {
+        "sequenceNumber": 2
+      },
+      "last": {
+        "sequenceNumber": 3
+      }
+    }
+  },
   "errors": [
     {
       "message": "Requested data is outside the available range",
@@ -318,7 +327,16 @@ Response: {
 task 14, lines 194-220:
 //# run-graphql --cursors bcs(@{obj_1_1},0)
 Response: {
-  "data": null,
+  "data": {
+    "availableRange": {
+      "first": {
+        "sequenceNumber": 2
+      },
+      "last": {
+        "sequenceNumber": 3
+      }
+    }
+  },
   "errors": [
     {
       "message": "Requested data is outside the available range",
```

### crates/iota-graphql-e2e-tests/tests/consistency/dynamic_fields/deleted_df.snap
```diff
@@ -88,45 +88,7 @@ task 11, lines 76-139:
 //# run-graphql
 Response: {
   "data": {
-    "latest": {
-      "version": 6,
-      "dynamicFields": {
-        "edges": [
-          {
-            "cursor": "IBdJyFZgAd3FF4kUA2ChBc3/KHCheQ4d6azocaJ074V0AQAAAAAAAAA=",
-            "node": {
-              "name": {
-                "bcs": "A2RmNA=="
-              },
-              "value": {
-                "json": "df4"
-              }
-            }
-          },
-          {
-            "cursor": "IHxoRI3Ce6B/guuh3eNs1qH336WmuI7nYdX85L26PEuAAQAAAAAAAAA=",
-            "node": {
-              "name": {
-                "bcs": "A2RmNQ=="
-              },
-              "value": {
-                "json": "df5"
-              }
-            }
-          },
-          {
-            "cursor": "IMqQupB6O4axj4yBPPakqB9dSiVLWP/F7L4oaURajy0AAQAAAAAAAAA=",
-            "node": {
-              "name": {
-                "bcs": "A2RmNg=="
-              },
-              "value": {
-                "json": "df6"
-              }
-            }
-          }
-        ]
-      },
+    "df123_removed": {
       "df1": null,
       "df5": {
         "name": {
@@ -135,10 +97,7 @@ Response: {
         "value": {
           "json": "df5"
         }
-      }
-    },
-    "df123_removed": {
-      "version": 5,
+      },
       "dynamicFields": {
         "edges": [
           {
@@ -176,18 +135,25 @@ Response: {
           }
         ]
       },
-      "df1": null,
+      "version": 5
+    },
+    "df456_added": {
+      "df1": {
+        "name": {
+          "bcs": "A2RmMQ=="
+        },
+        "value": {
+          "json": "df1"
+        }
+      },
       "df5": {
         "name": {
           "bcs": "A2RmNQ=="
         },
         "value": {
           "json": "df5"
         }
-      }
-    },
-    "df456_added": {
-      "version": 4,
+      },
       "dynamicFields": {
         "edges": [
           {
@@ -258,31 +224,18 @@ Response: {
           }
         ]
       },
-      "df1": {
-        "name": {
-          "bcs": "A2RmMQ=="
-        },
-        "value": {
-          "json": "df1"
-        }
-      },
+      "version": 4
+    },
+    "latest": {
+      "df1": null,
       "df5": {
         "name": {
           "bcs": "A2RmNQ=="
         },
         "value": {
           "json": "df5"
         }
-      }
-    }
-  }
-}
-
-task 12, lines 141-179:
-//# run-graphql
-Response: {
-  "data": {
-    "latest_owner": {
+      },
       "dynamicFields": {
         "edges": [
           {
@@ -320,6 +273,16 @@ Response: {
           }
         ]
       },
+      "version": 6
+    }
+  }
+}
+
+task 12, lines 141-179:
+//# run-graphql
+Response: {
+  "data": {
+    "latest_owner": {
       "df1": null,
       "df5": {
         "name": {
@@ -328,6 +291,43 @@ Response: {
         "value": {
           "json": "df5"
         }
+      },
+      "dynamicFields": {
+        "edges": [
+          {
+            "cursor": "IBdJyFZgAd3FF4kUA2ChBc3/KHCheQ4d6azocaJ074V0AQAAAAAAAAA=",
+            "node": {
+              "name": {
+                "bcs": "A2RmNA=="
+              },
+              "value": {
+                "json": "df4"
+              }
+            }
+          },
+          {
+            "cursor": "IHxoRI3Ce6B/guuh3eNs1qH336WmuI7nYdX85L26PEuAAQAAAAAAAAA=",
+            "node": {
+              "name": {
+                "bcs": "A2RmNQ=="
+              },
+              "value": {
+                "json": "df5"
+              }
+            }
+          },
+          {
+            "cursor": "IMqQupB6O4axj4yBPPakqB9dSiVLWP/F7L4oaURajy0AAQAAAAAAAAA=",
+            "node": {
+              "name": {
+                "bcs": "A2RmNg=="
+              },
+              "value": {
+                "json": "df6"
+              }
+            }
+          }
+        ]
       }
     }
   }
```
