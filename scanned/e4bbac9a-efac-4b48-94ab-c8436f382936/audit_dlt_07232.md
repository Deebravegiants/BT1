# [?] [chore] Remove RUSTSEC-2023-0086  (#21316)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2025-02-22
Source: https://github.com/MystenLabs/sui/commit/212dada704a3043c2371c1e261a1c27a92e94c9f
Type: security-commit

## Details
[chore] Remove RUSTSEC-2023-0086  (#21316)

## Description 

Removes RUSTSEC-2023-0086 by updating snowflake, lexical-util,
arrow,parquet versions. It also updates `object_store` to only have one
version in the lock file.

## Test plan 

How did you test the new or updated feature?

---

## Release notes

Check each box that your changes affect. If none of the boxes relate to
your changes, release notes aren't required.

For each box you select, include information after the relevant heading
that describes the impact of your changes that a user might notice and
any actions they must take to implement updates.

- [ ] Protocol: 
- [ ] Nodes (Validators and Full nodes): 
- [ ] gRPC:
- [ ] JSON-RPC: 
- [ ] GraphQL: 
- [ ] CLI: 
- [ ] Rust SDK:

## Patch
### Cargo.lock
```diff
@@ -536,9 +536,9 @@ checksum = "8da52d66c7071e2e3fa2a1e5c6d088fec47b593032b254f5e980de8ea54454d6"
 
 [[package]]
 name = "arrow"
-version = "52.1.0"
+version = "54.2.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6127ea5e585a12ec9f742232442828ebaf264dfa5eefdd71282376c599562b77"
+checksum = "755b6da235ac356a869393c23668c663720b8749dd6f15e52b6c214b4b964cc7"
 dependencies = [
  "arrow-arith",
  "arrow-array",
@@ -557,40 +557,39 @@ dependencies = [
 
 [[package]]
 name = "arrow-arith"
-version = "52.1.0"
+version = "54.2.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7add7f39210b7d726e2a8efc0083e7bf06e8f2d15bdb4896b564dce4410fbf5d"
+checksum = "64656a1e0b13ca766f8440752e9a93e11014eec7b67909986f83ed0ab1fe37b8"
 dependencies = [
  "arrow-array",
  "arrow-buffer",
  "arrow-data",
  "arrow-schema",
  "chrono",
- "half 2.3.1",
  "num",
 ]
 
 [[package]]
 name = "arrow-array"
-version = "52.1.0"
+version = "54.2.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "81c16ec702d3898c2f5cfdc148443c6cd7dbe5bac28399859eb0a3d38f072827"
+checksum = "57a4a6d2896083cfbdf84a71a863b22460d0708f8206a8373c52e326cc72ea1a"
 dependencies = [
  "ahash 0.8.11",
  "arrow-buffer",
  "arrow-data",
  "arrow-schema",
  "chrono",
  "half 2.3.1",
- "hashbrown 0.14.1",
+ "hashbrown 0.15.2",
  "num",
 ]
 
 [[package]]
 name = "arrow-buffer"
-version = "52.1.0"
+version = "54.2.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "cae6970bab043c4fbc10aee1660ceb5b306d0c42c8cc5f6ae564efcd9759b663"
+checksum = "cef870583ce5e4f3b123c181706f2002fb134960f9a911900f64ba4830c7a43a"
 dependencies = [
  "bytes",
  "half 2.3.1",
@@ -599,9 +598,9 @@ dependencies = [
 
 [[package]]
 name = "arrow-cast"
-version = "52.1.0"
+version = "54.2.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1c7ef44f26ef4f8edc392a048324ed5d757ad09135eff6d5509e6450d39e0398"
+checksum = "1ac7eba5a987f8b4a7d9629206ba48e19a1991762795bbe5d08497b7736017ee"
 dependencies = [
  "arrow-array",
  "arrow-buffer",
@@ -619,28 +618,25 @@ dependencies = [
 
 [[package]]
 name = "arrow-csv"
-version = "52.1.0"
+version = "54.2.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5f843490bd258c5182b66e888161bb6f198f49f3792f7c7f98198b924ae0f564"
+checksum = "90f12542b8164398fc9ec595ff783c4cf6044daa89622c5a7201be920e4c0d4c"
 dependencies = [
  "arrow-array",
- "arrow-buffer",
  "arrow-cast",
- "arrow-data",
  "arrow-schema",
  "chrono",
  "csv",
  "csv-core",
  "lazy_static",
- "lexical-core",
  "regex",
 ]
 
 [[package]]
 name = "arrow-data"
-version = "52.1.0"
+version = "54.2.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a769666ffac256dd301006faca1ca553d0ae7cffcf4cd07095f73f95eb226514"
+checksum = "b095e8a4f3c309544935d53e04c3bfe4eea4e71c3de6fe0416d1f08bb4441a83"
 dependencies = [
  "arrow-buffer",
  "arrow-schema",
@@ -650,23 +646,22 @@ dependencies = [
 
 [[package]]
 name = "arrow-ipc"
-version = "52.1.0"
+version = "54.2.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "dbf9c3fb57390a1af0b7bb3b5558c1ee1f63905f3eccf49ae7676a8d1e6e5a72"
+checksum = "65c63da4afedde2b25ef69825cd4663ca76f78f79ffe2d057695742099130ff6"
 dependencies = [
  "arrow-array",
  "arrow-buffer",
- "arrow-cast",
  "arrow-data",
  "arrow-schema",
  "flatbuffers",
 ]
 
 [[package]]
 name = "arrow-json"
-version = "52.1.0"
+version = "54.2.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "654e7f3724176b66ddfacba31af397c48e106fbe4d281c8144e7d237df5acfd7"
+checksum = "9551d9400532f23a370cabbea1dc5a53c49230397d41f96c4c8eedf306199305"
 dependencies = [
  "arrow-array",
  "arrow-buffer",
@@ -684,45 +679,41 @@ dependencies = [
 
 [[package]]
 name = "arrow-ord"
-version = "52.1.0"
+version = "54.2.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e8008370e624e8e3c68174faaf793540287106cfda8ad1da862fdc53d8e096b4"
+checksum = "6c07223476f8219d1ace8cd8d85fa18c4ebd8d945013f25ef5c72e85085ca4ee"
 dependencies = [
  "arrow-array",
  "arrow-buffer",
  "arrow-data",
  "arrow-schema",
  "arrow-select",
- "half 2.3.1",
- "num",
 ]
 
 [[package]]
 name = "arrow-row"
-version = "52.1.0"
+version = "54.2.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "ca5e3a6b7fda8d9fe03f3b18a2d946354ea7f3c8e4076dbdb502ad50d9d44824"
+checksum = "91b194b38bfd89feabc23e798238989c6648b2506ad639be42ec8eb1658d82c4"
 dependencies = [
- "ahash 0.8.11",
  "arrow-array",
  "arrow-buffer",
  "arrow-data",
  "arrow-schema",
  "half 2.3.1",
- "hashbrown 0.14.1",
 ]
 
 [[package]]
 name = "arrow-schema"
-version = "52.1.0"
+version = "54.2.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "dab1c12b40e29d9f3b699e0203c2a73ba558444c05e388a4377208f8f9c97eee"
+checksum = "0f40f6be8f78af1ab610db7d9b236e21d587b7168e368a36275d2e5670096735"
 
 [[package]]
 name = "arrow-select"
-version = "52.1.0"
+version = "54.2.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e80159088ffe8c48965cb9b1a7c968b2729f29f37363df7eca177fc3281fe7c3"
+checksum = "ac265273864a820c4a179fc67182ccc41ea9151b97024e1be956f0f2369c2539"
 dependencies = [
  "ahash 0.8.11",
  "arrow-array",
@@ -734,9 +725,9 @@ dependencies = [
 
 [[package]]
 name = "arrow-string"
-version = "52.1.0"
+version = "54.2.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0fd04a6ea7de183648edbcb7a6dd925bbd04c210895f6384c780e27a9b54afcd"
+checksum = "d44c8eed43be4ead49128370f7131f054839d3d6003e52aebf64322470b8fbd0"
 dependencies = [
  "arrow-array",
  "arrow-buffer",
@@ -2116,9 +2107,9 @@ dependencies = [
 
 [[package]]
 name = "brotli"
-version = "6.0.0"
+version = "7.0.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "74f7971dbd9326d58187408ab83117d8ac1bb9c17b085fdacd1cf2f598719b6b"
+checksum = "cc97b8f16f944bba54f0433f07e30be199b6dc2bd25937444bbad560bcea29bd"
 dependencies = [
  "alloc-no-stdlib",
  "alloc-stdlib",
@@ -3487,7 +3478,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "978747c1d849a7d2ee5e8adc0159961c48fb7e5db2f06af6723b80123bb53856"
 dependencies = [
  "cfg-if",
- "hashbrown 0.14.1",
+ "hashbrown 0.14.5",
  "lock_api",
  "once_cell",
  "parking_lot_core 0.9.9",
@@ -4974,9 +4965,9 @@ checksum = "0ce7134b9999ecaf8bcd65542e436736ef32ddca1b3e06094cb6ec5755203b80"
 
 [[package]]
 name = "flatbuffers"
-version = "24.3.25"
+version = "24.12.23"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8add37afff2d4ffa83bc748a70b4b1370984f6980768554182424ef71447c35f"
+checksum = "4f1baf0dbf96932ec9a3038d57900329c015b0bfb7b63d904f3bc27e2b02a096"
 dependencies = [
  "bitflags 1.3.2",
  "rustc_version",
@@ -5573,9 +5564,9 @@ dependencies = [
 
 [[package]]
 name = "hashbrown"
-version = "0.14.1"
+version = "0.14.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7dfda62a12f55daeae5015f81b0baea145391cb4520f86c248fc615d72640d12"
+checksum = "e5274423e17b7c9fc20b6e7e208532f9b19825d82dfd615708b70edd83df41f1"
 dependencies = [
  "ahash 0.8.11",
  "allocator-api2",
@@ -6950,9 +6941,9 @@ checksum = "884e2677b40cc8c339eaefcb701c32ef1fd2493d71118dc0ca4b6a736c93bd67"
 
 [[package]]
 name = "lexical-core"
-version = "0.8.5"
+version = "1.0.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "2cde5de06e8d4c2faabc400238f9ae1c74d5412d03a7bd067645ccbc47070e46"
+checksum = "b765c31809609075565a70b4b71402281283aeda7ecaf4818ac14a7b2ade8958"
 dependencies = [
  "lexical-parse-float",
  "lexical-parse-integer",
@@ -6963,9 +6954,9 @@ dependencies = [
 
 [[package]]
 name = "lexical-parse-float"
-version = "0.8.5"
+version = "1.0.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "683b3a5ebd0130b8fb52ba0bdc718cc56815b6a097e28ae5a6997d0ad17dc05f"
+checksum = "de6f9cb01fb0b08060209a057c048fcbab8717b4c1ecd2eac66ebfe39a65b0f2"
 dependencies = [
  "lexical-parse-integer",
  "lexical-util",
@@ -6974,28 +6965,28 @@ dependencies = [
 
 [[package]]
 name = "lexical-parse-integer"
-version = "0.8.6"
+version = "1.0.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6d0994485ed0c312f6d965766754ea177d07f9c00c9b82a5ee62ed5b47945ee9"
+checksum = "72207aae22fc0a121ba7b6d479e42cbfea549af1479c3f3a4f12c70dd66df12e"
 dependencies = [
  "lexical-util",
  "static_assertions",
 ]
 
 [[package]]
 name = "lexical-util"
-version = "0.8.5"
+version = "1.0.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5255b9ff16ff898710eb9eb63cb39248ea8a5bb036bea8085b1a767ff6c4e3fc"
+checksum = "5a82e24bf537fd24c177ffbbdc6ebcc8d54732c35b50a3f28cc3f4e4c949a0b3"
 dependencies = [
  "static_assertions",
 ]
 
 [[package]]
 name = "lexical-write-float"
-version = "0.8.5"
+version = "1.0.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "accabaa1c4581f05a3923d1b4cfd124c329352288b7b9da09e766b0668116862"
+checksum = "c5afc668a27f460fb45a81a757b6bf2f43c2d7e30cb5a2dcd3abf294c78d62bd"
 dependencies = [
  "lexical-util",
  "lexical-write-integer",
@@ -7004,9 +6995,9 @@ dependencies = [
 
 [[package]]
 name = "lexical-write-integer"
-version = "0.8.5"
+version = "1.0.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e1b6f3d1f4422866b68192d62f77bc5c700bee84f3069f2469d7bc8c77852446"
+checksum = "629ddff1a914a836fb245616a7888b62903aae58fa771e1d83943035efa0f978"
 dependencies = [
  "lexical-util",
  "static_assertions",
@@ -7197,7 +7188,7 @@ version = "0.12.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "d3262e75e648fce39813cb56ac41f3c3e3f65217ebf3844d818d1f9398cfb0dc"
 dependencies = [
- "hashbrown 0.14.1",
+ "hashbrown 0.14.5",
 ]
 
 [[package]]
@@ -8950,15 +8941,16 @@ dependencies = [
 
 [[package]]
 name = "object_store"
-version = "0.10.2"
+version = "0.11.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e6da452820c715ce78221e8202ccc599b4a52f3e1eb3eedb487b680c81a8e3f3"
+checksum = "3cfccb68961a56facde1163f9319e0d15743352344e7808a11795fb99698dcaf"
 dependencies = [
  "async-trait",
  "base64 0.22.1",
  "bytes",
  "chrono",
  "futures",
+ "httparse",
  "humantime",
  "hyper 1.5.2",
  "itertools 0.13.0",
@@ -9381,9 +9373,9 @@ dependencies = [
 
 [[package]]
 name = "parquet"
-version = "52.1.0"
+version = "54.2.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0f22ba0d95db56dde8685e3fadcb915cdaadda31ab8abbe3ff7f0ad1ef333267"
+checksum = "761c44d824fe83106e0600d2510c07bf4159a4985bf0569b513ea4288dc1b4fb"
 dependencies = [
  "ahash 0.8.11",
  "arrow-array",
@@ -9394,17 +9386,18 @@ dependencies = [
  "arrow-schema",
  "arrow-select",
  "base64 0.22.1",
- "brotli 6.0.0",
+ "brotli 7.0.0",
  "bytes",
  "chrono",
  "flate2",
  "half 2.3.1",
- "hashbrown 0.14.1",
+ "hashbrown 0.15.2",
  "lz4_flex",
  "num",
  "num-bigint 0.4.4",
  "paste",
  "seq-macro",
+ "simdutf8",
  "snap",
  "thrift",
  "twox-hash",
@@ -10413,9 +10406,9 @@ dependencies = [
 
 [[package]]
 name = "quick-xml"
-version = "0.36.1"
+version = "0.37.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "96a05e2e8efddfa51a84ca47cec303fac86c8541b686d37cac5efc0e094417bc"
+checksum = "165859e9e55f79d67b96c5d96f4e88b6f2695a1972849c15a6a3f5c59fc2c003"
 dependencies = [
  "memchr",
  "serde",
@@ -10870,9 +10863,9 @@ dependencies = [
 
 [[package]]
 name = "reqwest-middleware"
-version = "0.3.2"
+version = "0.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "39346a33ddfe6be00cbc17a34ce996818b97b230b87229f10114693becca1268"
+checksum = "d1ccd3b55e711f91a9885a2fa6fbbb2e39db1776420b062efc058c6410f7e5e3"
 dependencies = [
  "anyhow",
  "async-trait",
@@ -10885,13 +10878,12 @@ dependencies = [
 
 [[package]]
 name = "reqwest-retry"
-version = "0.5.0"
+version = "0.7.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "40f342894422862af74c50e1e9601cf0931accc9c6981e5eb413c46603b616b5"
+checksum = "29c73e4195a6bfbcb174b790d9b3407ab90646976c55de58a6515da25d851178"
 dependencies = [
  "anyhow",
  "async-trait",
- "chrono",
  "futures",
  "getrandom 0.2.15",
  "http 1.1.0",
@@ -10900,6 +10892,7 @@ dependencies = [
  "reqwest 0.12.9",
  "reqwest-middleware",
  "retry-policies",
+ "thiserror 1.0.69",
  "tokio",
  "tracing",
  "wasm-timer",
@@ -10913,12 +10906,10 @@ checksum = "4389f1d5789befaf6029ebd9f7dac4af7f7e3d61b69d4f30e2ac02b57e7712b0"
 
 [[package]]
 name = "retry-policies"
-version = "0.3.0"
+version = "0.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "493b4243e32d6eedd29f9a398896e35c6943a123b55eec97dcaee98310d25810"
+checksum = "5875471e6cab2871bc150ecb8c727db5113c9338cc3354dc5ee3425b6aa40a1c"
 dependencies = [
- "anyhow",
- "chrono",
  "rand 0.8.5",
 ]
 
@@ -12144,6 +12135,12 @@ dependencies = [
  "rand_core 0.6.4",
 ]
 
+[[package]]
+name = "simdutf8"
+version = "0.1.5"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "e3a9fe34e3e7a50316060351f37187a3f546bce95496156754b601a5fa71b76e"
+
 [[package]]
 name = "similar"
 version = "2.4.0"
@@ -12270,24 +12267,23 @@ checksum = "b7c388c1b5e93756d0c740965c41e8822f866621d41acbdf6336a6a168f8840c"
 
 [[package]]
 name = "snafu"
-version = "0.7.4"
+version = "0.8.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "cb0656e7e3ffb70f6c39b3c2a86332bb74aa3c679da781642590f3c1118c5045"
+checksum = "223891c85e2a29c3fe8fb900c1fae5e69c2e42415e3177752e8718475efa5019"
 dependencies = [
- "doc-comment",
  "snafu-derive",
 ]
 
 [[package]]
 name = "snafu-derive"
-version = "0.7.4"
+version = "0.8.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "475b3bbe5245c26f2d8a6f62d67c1f30eb9fffeccee721c45d162c3ebbdf81b2"
+checksum = "03c3c6b7927ffe7ecaa769ee0e3994da3b8cafc8f444578982c83ecb161af917"
 dependencies = [
- "heck 0.4.1",
+ "heck 0.5.0",
  "proc-macro2 1.0.87",
  "quote 1.0.37",
- "syn 1.0.107",
+ "syn 2.0.87",
 ]
 
 [[package]]
@@ -12298,9 +12294,9 @@ checksum = "5e9f0ab6ef7eb7353d9119c170a436d1bf248eea575ac42d19d12f4e34130831"
 
 [[package]]
 name = "snowflake-api"
-version = "0.9.0"
+version = "0.11.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1c7f29746a86845a74953b3728029b378c9bac2fb15c2defd54a8177cabcc452"
+checksum = "d921df7138543cd9fc35beea12beabb8f5980366f38287382ae35222f3a6d392"
 dependencies = [
  "arrow",
  "async-trait",
@@ -12317,7 +12313,7 @@ dependencies = [
  "serde",
  "serde_json",
  "snowflake-jwt",
- "thiserror 1.0.69",
+ "thiserror 2.0.9",
  "tokio",
  "url",
  "uuid 1.2.2",
@@ -16836,7 +16832,7 @@ dependencies = [
  "futures-io",
  "futures-sink",
  "futures-util",
- "hashbrown 0.14.1",
+ "hashbrown 0.14.5",
  "pin-project-lite",
  "tokio",
 ]
@@ -16851,7 +16847,7 @@ dependencies = [
  "futures-io",
  "futures-sink",
  "futures-util",
- "hashbrown 0.14.1",
+ "hashbrown 0.14.5",
  "pin-project-lite",
  "real_tokio",
  "slab",
```

### Cargo.toml
```diff
@@ -263,8 +263,8 @@ unexpected_cfgs = { level = "warn", check-cfg = [
 # Dependencies that should be kept in sync through the whole workspace
 [workspace.dependencies]
 anyhow = "1.0.71"
-arrow = "52"
-arrow-array = "52"
+arrow = "54"
+arrow-array = "54"
 arc-swap = { version = "1.5.1", features = ["serde"] }
 assert_cmd = "2.0.6"
 async-graphql = "=7.0.1"
@@ -413,11 +413,11 @@ ntest = "0.9.0"
 num-bigint = "0.4.4"
 num_cpus = "1.15.0"
 num_enum = "0.6.1"
-object_store = { version = "0.10", features = ["aws", "gcp", "azure", "http"] }
+object_store = { version = "0.11.2", features = ["aws", "gcp", "azure", "http"] }
 once_cell = "1.18.0"
 ouroboros = "0.17"
 parking_lot = { version = "0.12.3", features = ["arc_lock"] }
-parquet = "52"
+parquet = "54"
 pin-project-lite = "0.2.13"
 pkcs8 = { version = "0.9.0", features = ["std"] }
 pprof = { version = "0.14.0", features = ["cpp", "frame-pointer"] }
@@ -482,7 +482,7 @@ simple-server-timing-header = "0.1.1"
 slip10_ed25519 = "0.1.3"
 smallvec = "1.10.0"
 snap = "1.1.0"
-snowflake-api = "0.9.0"
+snowflake-api = "0.11.0"
 static_assertions = "1.1.0"
 strum = { version = "0.24", features = ["derive"] }
 strum_macros = "0.24.3"
```

### crates/sui-security-watchdog/Cargo.toml
```diff
@@ -22,6 +22,6 @@ prometheus.workspace = true
 telemetry-subscribers.workspace = true
 async-trait.workspace = true
 uuid.workspace = true
-lexical-util = "0.8.5"
+lexical-util = "1.0.6"
 reqwest = { workspace = true, features = ["json"] }
 env_logger = "0.11.3"
```

### deny.toml
```diff
@@ -30,8 +30,6 @@ ignore = [
     "RUSTSEC-2024-0320",
     # allow unmaintained proc-macro-error used in transitive dependencies
     "RUSTSEC-2024-0370",
-    # Temporarily allow until arrow family of crates updates `lexical-core` to 1.0
-    "RUSTSEC-2023-0086",
     # allow unmaintained instant crate used in transitive dependencies (backoff, cached, fastrand, parking_lot_*)
     "RUSTSEC-2024-0384",
     # allow unmaintained derivative crate used in transitive dependencies (ark-*)
```
