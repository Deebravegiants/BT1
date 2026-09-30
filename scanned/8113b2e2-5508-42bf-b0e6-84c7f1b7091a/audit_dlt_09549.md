# [?] Merge pull request #3437 from peilun-conflux/fix/rustsec-2026-0097-rand

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-04-13
Source: https://github.com/Conflux-Chain/conflux-rust/commit/833f694f82ead3634230613de34fff3ad7905331
Type: security-commit

## Details
Merge pull request #3437 from peilun-conflux/fix/rustsec-2026-0097-rand

Update rand to 0.9.3 to fix RUSTSEC-2026-0097

## Patch
### Cargo.lock
```diff
@@ -73,7 +73,7 @@ dependencies = [
  "getrandom 0.2.15",
  "once_cell",
  "version_check",
- "zerocopy 0.7.32",
+ "zerocopy",
 ]
 
 [[package]]
@@ -256,7 +256,7 @@ dependencies = [
  "keccak-asm",
  "paste",
  "proptest",
- "rand 0.9.0",
+ "rand 0.9.3",
  "rapidhash",
  "ruint",
  "rustc-hash 2.1.1",
@@ -1277,7 +1277,7 @@ dependencies = [
  "metrics",
  "parking_lot 0.12.1",
  "primitives",
- "rand 0.9.0",
+ "rand 0.9.3",
  "txgen",
 ]
 
@@ -1575,7 +1575,7 @@ dependencies = [
  "network",
  "parking_lot 0.12.1",
  "primitives",
- "rand 0.9.0",
+ "rand 0.9.3",
  "toml 0.8.19",
  "txgen",
 ]
@@ -1743,7 +1743,7 @@ dependencies = [
  "malloc_size_of",
  "malloc_size_of_derive",
  "primitives",
- "rand 0.9.0",
+ "rand 0.9.3",
  "rand_xorshift 0.4.0",
  "treap-map",
  "typenum",
@@ -1794,7 +1794,7 @@ dependencies = [
  "jsonrpsee-core",
  "jsonrpsee-types",
  "log",
- "rand 0.9.0",
+ "rand 0.9.3",
  "serde",
  "strum 0.26.3",
  "thiserror 2.0.18",
@@ -1892,7 +1892,7 @@ dependencies = [
  "once_cell",
  "parity-version",
  "primitives",
- "rand 0.7.3",
+ "rand 0.9.3",
  "rustc-hex",
  "serde",
  "serde_derive",
@@ -2084,7 +2084,7 @@ dependencies = [
  "memoffset 0.9.1",
  "parking_lot 0.12.1",
  "primitives",
- "rand 0.9.0",
+ "rand 0.9.3",
  "rand_chacha 0.9.0",
  "random-crash",
  "rlp 0.4.6",
@@ -2262,7 +2262,7 @@ dependencies = [
  "proptest",
  "proptest-derive",
  "rand 0.8.5",
- "rand 0.9.0",
+ "rand 0.9.3",
  "rand_xorshift 0.4.0",
  "rangetools",
  "rayon",
@@ -2348,7 +2348,7 @@ dependencies = [
  "malloc_size_of_derive",
  "parking_lot 0.12.1",
  "primitives",
- "rand 0.9.0",
+ "rand 0.9.3",
  "rlp 0.4.6",
  "rlp-derive",
  "smart-default",
@@ -2393,7 +2393,7 @@ dependencies = [
  "matches",
  "parity-wordlist",
  "parking_lot 0.12.1",
- "rand 0.9.0",
+ "rand 0.9.3",
  "rustc-hex",
  "serde",
  "serde_derive",
@@ -2610,7 +2610,7 @@ dependencies = [
  "parking_lot 0.12.1",
  "primitives",
  "rand 0.8.5",
- "rand 0.9.0",
+ "rand 0.9.3",
  "random-crash",
  "rlp 0.4.6",
  "rpassword",
@@ -4548,7 +4548,7 @@ version = "0.6.0"
 dependencies = [
  "atom",
  "malloc_size_of",
- "rand 0.9.0",
+ "rand 0.9.3",
  "rayon",
 ]
 
@@ -5481,7 +5481,7 @@ dependencies = [
  "jsonrpsee-types",
  "parking_lot 0.12.1",
  "pin-project",
- "rand 0.9.0",
+ "rand 0.9.3",
  "rustc-hash 2.1.1",
  "serde",
  "serde_json",
@@ -5814,7 +5814,7 @@ version = "0.1.0"
 dependencies = [
  "malloc_size_of",
  "parking_lot 0.12.1",
- "rand 0.9.0",
+ "rand 0.9.3",
 ]
 
 [[package]]
@@ -5868,7 +5868,7 @@ dependencies = [
  "db",
  "kvdb",
  "parking_lot 0.12.1",
- "rand 0.9.0",
+ "rand 0.9.3",
  "rlp 0.4.6",
  "rlp-derive",
 ]
@@ -5897,7 +5897,7 @@ dependencies = [
  "log-mdc",
  "mock_instant",
  "parking_lot 0.12.1",
- "rand 0.9.0",
+ "rand 0.9.3",
  "serde",
  "serde-value",
  "serde_json",
@@ -6083,7 +6083,7 @@ dependencies = [
  "lazy_static",
  "log",
  "parking_lot 0.12.1",
- "rand 0.9.0",
+ "rand 0.9.3",
  "reqwest 0.12.24",
  "serde",
  "timer",
@@ -6218,7 +6218,7 @@ dependencies = [
  "hyper 1.8.1",
  "hyper-util",
  "log",
- "rand 0.9.0",
+ "rand 0.9.3",
  "regex",
  "serde_json",
  "serde_urlencoded",
@@ -6307,7 +6307,7 @@ dependencies = [
  "parity-path",
  "parking_lot 0.12.1",
  "priority-send-queue",
- "rand 0.9.0",
+ "rand 0.9.3",
  "rlp 0.4.6",
  "rlp-derive",
  "serde",
@@ -7276,7 +7276,7 @@ dependencies = [
  "log",
  "malloc_size_of",
  "once_cell",
- "rand 0.9.0",
+ "rand 0.9.3",
  "rlp 0.4.6",
  "rlp-derive",
  "serde",
@@ -7545,14 +7545,13 @@ dependencies = [
 
 [[package]]
 name = "rand"
-version = "0.9.0"
+version = "0.9.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "3779b94aeb87e8bd4e834cee3650289ee9e0d5677f976ecdb6d219e5f4f6cd94"
+checksum = "7ec095654a25171c2124e9e3393a930bddbffdc939556c914957a4c3e0a87166"
 dependencies = [
  "rand_chacha 0.9.0",
  "rand_core 0.9.3",
  "serde",
- "zerocopy 0.8.24",
 ]
 
 [[package]]
@@ -7647,7 +7646,7 @@ dependencies = [
  "lazy_static",
  "log",
  "parking_lot 0.12.1",
- "rand 0.9.0",
+ "rand 0.9.3",
 ]
 
 [[package]]
@@ -8157,7 +8156,7 @@ dependencies = [
  "primitive-types 0.12.2",
  "proptest",
  "rand 0.8.5",
- "rand 0.9.0",
+ "rand 0.9.3",
  "rlp 0.5.2",
  "ruint-macro",
  "serde_core",
@@ -8504,7 +8503,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "2c3c81b43dc2d8877c216a3fccf76677ee1ebccd429566d3e67447290d0c42b2"
 dependencies = [
  "bitcoin_hashes",
- "rand 0.9.0",
+ "rand 0.9.3",
  "secp256k1-sys 0.11.0",
 ]
 
@@ -9900,7 +9899,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "319c70195101a93f56db4c74733e272d720768e13471f400c78406a326b172b0"
 dependencies = [
  "cc",
- "windows-targets 0.48.5",
+ "windows-targets 0.52.6",
 ]
 
 [[package]]
@@ -9918,7 +9917,7 @@ dependencies = [
  "criterion",
  "malloc_size_of",
  "primitives",
- "rand 0.9.0",
+ "rand 0.9.3",
  "rand_chacha 0.9.0",
  "rand_xorshift 0.4.0",
 ]
@@ -9943,7 +9942,7 @@ dependencies = [
  "metrics",
  "parking_lot 0.12.1",
  "primitives",
- "rand 0.9.0",
+ "rand 0.9.3",
  "rlp 0.4.6",
  "rustc-hex",
  "secret-store",
@@ -10971,16 +10970,7 @@ version = "0.7.32"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "74d4d3961e53fa4c9a25a8637fc2bfaf2595b3d3ae34875568a5cf64787716be"
 dependencies = [
- "zerocopy-derive 0.7.32",
-]
-
-[[package]]
-name = "zerocopy"
-version = "0.8.24"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "2586fea28e186957ef732a5f8b3be2da217d65c5969d4b1e17f973ebbe876879"
-dependencies = [
- "zerocopy-derive 0.8.24",
+ "zerocopy-derive",
 ]
 
 [[package]]
@@ -10994,17 +10984,6 @@ dependencies = [
  "syn 2.0.114",
 ]
 
-[[package]]
-name = "zerocopy-derive"
-version = "0.8.24"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a996a8f63c5c4448cd959ac1bab0aaa3306ccfd060472f85943ee0750f0169be"
-dependencies = [
- "proc-macro2",
- "quote",
- "syn 2.0.114",
-]
-
 [[package]]
 name = "zerofrom"
 version = "0.1.5"
```

### Cargo.toml
```diff
@@ -353,7 +353,8 @@ ripemd = "0.1.3"
 clap = "4"
 
 # rand & rng
-rand = "0.9"
+# 0.9.3 is the patched version for RUSTSEC-2026-0097.
+rand = "0.9.3"
 rand_xorshift = "0.4"
 rand_chacha = "0.9"
 
```

### crates/client/src/rpc/helpers/subscribers.rs
```diff
@@ -20,9 +20,7 @@
 
 //! A map of subscribers.
 
-use cfx_rpc_cfx_types::random;
 pub use cfx_rpc_cfx_types::SubId as Id;
-use cfx_types::H64;
 use jsonrpc_pubsub::{
     typed::{Sink, Subscriber},
     SubscriptionId,
@@ -31,24 +29,19 @@ use log::{debug, trace};
 use std::{collections::HashMap, ops};
 
 pub struct Subscribers<T> {
-    rand: random::Rng,
     subscriptions: HashMap<Id, T>,
 }
 
 impl<T> Default for Subscribers<T> {
     fn default() -> Self {
         Subscribers {
-            rand: random::new(),
             subscriptions: HashMap::new(),
         }
     }
 }
 
 impl<T> Subscribers<T> {
-    pub fn next_id(&mut self) -> Id {
-        let data = H64::random_using(&mut self.rand);
-        Id::new(data)
-    }
+    pub fn next_id(&mut self) -> Id { Id::next() }
 
     /// Insert new subscription and return assigned id.
     #[allow(dead_code)]
```

### crates/rpc/rpc-cfx-impl/src/helpers/subscribers.rs
```diff
@@ -20,10 +20,8 @@
 
 //! A map of subscribers.
 
-use cfx_rpc_cfx_types::random;
 pub use cfx_rpc_cfx_types::SubId as Id;
 use cfx_rpc_utils::error::jsonrpsee_error_helpers::internal_error_with_data;
-use cfx_types::H64;
 use futures::StreamExt;
 use jsonrpsee::{
     server::SubscriptionMessage, types::ErrorObject, SubscriptionSink,
@@ -34,24 +32,19 @@ use std::{collections::HashMap, ops};
 use tokio_stream::Stream;
 
 pub struct Subscribers<T> {
-    rand: random::Rng,
     subscriptions: HashMap<Id, T>,
 }
 
 impl<T> Default for Subscribers<T> {
     fn default() -> Self {
         Subscribers {
-            rand: random::new(),
             subscriptions: HashMap::new(),
         }
     }
 }
 
 impl<T> Subscribers<T> {
-    pub fn next_id(&mut self) -> Id {
-        let data = H64::random_using(&mut self.rand);
-        Id::new(data)
-    }
+    pub fn next_id(&mut self) -> Id { Id::next() }
 
     /// Insert new subscription and return assigned id.
     #[allow(dead_code)]
```

### crates/rpc/rpc-cfx-types/Cargo.toml
```diff
@@ -27,7 +27,7 @@ cfx-util-macros = { workspace = true }
 log = { workspace = true }
 cfx-parity-trace-types = { workspace = true }
 parity-version = { workspace = true }
-rand_07 = { workspace = true }
+rand = { workspace = true }
 diem-crypto = { workspace = true }
 diem-types = { workspace = true }
 rustc-hex = { workspace = true }
```

### crates/rpc/rpc-cfx-types/src/lib.rs
```diff
@@ -68,4 +68,4 @@ pub use vote_params_info::VoteParamsInfo;
 pub use cfx_rpc_primitives::Bytes;
 pub use primitives::BlockHashOrEpochNumber;
 
-pub use subscriber_id::{random, SubId};
+pub use subscriber_id::SubId;
```

### crates/rpc/rpc-cfx-types/src/subscriber_id.rs
```diff
@@ -18,14 +18,9 @@ impl str::FromStr for SubId {
 impl SubId {
     pub fn new(data: H64) -> Self { SubId(data) }
 
+    /// Generate a new random subscription id.
+    pub fn next() -> Self { SubId(H64(rand::random::<[u8; 8]>())) }
+
     // TODO: replace `format!` see [#10412](https://github.com/paritytech/parity-ethereum/issues/10412)
     pub fn as_string(&self) -> String { format!("{:?}", self.0) }
 }
-
-pub mod random {
-    use rand_07;
-
-    pub type Rng = rand_07::rngs::OsRng;
-
-    pub fn new() -> Rng { rand_07::rngs::OsRng }
-}
```

### deny.toml
```diff
@@ -82,6 +82,18 @@ ignore = [
     "RUSTSEC-2020-0016",
     # instant unmaintained; pulled by parking_lot 0.11 via jsonrpc + prometheus 0.12.
     "RUSTSEC-2024-0384",
+    # rand 0.7/0.8 unsound `ThreadRng` reseed-in-custom-logger
+    # (RUSTSEC-2026-0097). The 0.9.x code path is patched here by bumping
+    # workspace rand to 0.9.3. rand 0.7.3 and 0.8.5 still appear in
+    # Cargo.lock via external transitive deps that cannot be upgraded
+    # without upstream work (fixed-hash, jsonrpc-pubsub, parity-secp256k1,
+    # parity-ws for 0.7.x; ark-std, alloy-rpc-types, proptest, revm,
+    # substrate-bn for 0.8.x) and first-party pos/diem-crypto plus cfx_key
+    # bound to the unmaintained parity-secp256k1 fork. The exploit requires
+    # a custom log::Log impl that calls rand::thread_rng() inside its log
+    # method and triggers a reseed there, which this repo does not do.
+    # Follow-ups will migrate pos/diem-crypto and replace parity-secp256k1.
+    { id = "RUSTSEC-2026-0097", reason = "rand 0.9 patched; 0.7/0.8 forced by transitive deps and upstream pins; vulnerable code path not reachable here." },
 ]
 # If this is true, then cargo deny will use the git executable to fetch advisory database.
 # If this is false, then it uses a built-in git library.
```

### tools/consensus_bench/Cargo.lock
```diff
@@ -71,7 +71,7 @@ dependencies = [
  "cfg-if 1.0.0",
  "once_cell",
  "version_check",
- "zerocopy 0.7.32",
+ "zerocopy",
 ]
 
 [[package]]
@@ -236,7 +236,7 @@ dependencies = [
  "keccak-asm",
  "paste",
  "proptest",
- "rand 0.9.0",
+ "rand 0.9.3",
  "ruint",
  "rustc-hash 2.1.1",
  "serde",
@@ -1486,7 +1486,7 @@ dependencies = [
  "malloc_size_of",
  "malloc_size_of_derive",
  "primitives",
- "rand 0.9.0",
+ "rand 0.9.3",
  "rand_xorshift 0.4.0",
  "treap-map",
  "typenum",
@@ -1545,7 +1545,7 @@ dependencies = [
  "once_cell",
  "parity-version",
  "primitives",
- "rand 0.7.3",
+ "rand 0.9.3",
  "rustc-hex",
  "serde",
  "serde_derive",
@@ -1652,7 +1652,7 @@ dependencies = [
  "memoffset",
  "parking_lot 0.12.3",
  "primitives",
- "rand 0.9.0",
+ "rand 0.9.3",
  "rand_chacha 0.9.0",
  "random-crash",
  "rlp 0.4.6",
@@ -1812,7 +1812,7 @@ dependencies = [
  "primitives",
  "priority-send-queue",
  "rand 0.8.5",
- "rand 0.9.0",
+ "rand 0.9.3",
  "rand_xorshift 0.4.0",
  "rangetools",
  "rayon",
@@ -1940,7 +1940,7 @@ dependencies = [
  "log",
  "parity-wordlist",
  "parking_lot 0.12.3",
- "rand 0.9.0",
+ "rand 0.9.3",
  "rustc-hex",
  "serde",
  "serde_derive",
@@ -4440,7 +4440,7 @@ version = "0.1.0"
 dependencies = [
  "malloc_size_of",
  "parking_lot 0.12.3",
- "rand 0.9.0",
+ "rand 0.9.3",
 ]
 
 [[package]]
@@ -4504,7 +4504,7 @@ dependencies = [
  "log-mdc",
  "mock_instant",
  "parking_lot 0.12.3",
- "rand 0.9.0",
+ "rand 0.9.3",
  "serde",
  "serde-value",
  "serde_json",
@@ -4623,7 +4623,7 @@ dependencies = [
  "lazy_static",
  "log",
  "parking_lot 0.12.3",
- "rand 0.9.0",
+ "rand 0.9.3",
  "serde",
  "timer",
  "tokio",
@@ -4765,7 +4765,7 @@ dependencies = [
  "parity-path",
  "parking_lot 0.12.3",
  "priority-send-queue",
- "rand 0.9.0",
+ "rand 0.9.3",
  "rlp 0.4.6",
  "rlp-derive",
  "serde",
@@ -5555,7 +5555,7 @@ dependencies = [
  "log",
  "malloc_size_of",
  "once_cell",
- "rand 0.9.0",
+ "rand 0.9.3",
  "rlp 0.4.6",
  "rlp-derive",
  "serde",
@@ -5711,14 +5711,13 @@ dependencies = [
 
 [[package]]
 name = "rand"
-version = "0.9.0"
+version = "0.9.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "3779b94aeb87e8bd4e834cee3650289ee9e0d5677f976ecdb6d219e5f4f6cd94"
+checksum = "7ec095654a25171c2124e9e3393a930bddbffdc939556c914957a4c3e0a87166"
 dependencies = [
  "rand_chacha 0.9.0",
  "rand_core 0.9.3",
  "serde",
- "zerocopy 0.8.24",
 ]
 
 [[package]]
@@ -5813,7 +5812,7 @@ dependencies = [
  "lazy_static",
  "log",
  "parking_lot 0.12.3",
- "rand 0.9.0",
+ "rand 0.9.3",
 ]
 
 [[package]]
@@ -6223,7 +6222,7 @@ dependencies = [
  "primitive-types 0.12.2",
  "proptest",
  "rand 0.8.5",
- "rand 0.9.0",
+ "rand 0.9.3",
  "rlp 0.5.2",
  "ruint-macro",
  "serde_core",
@@ -6462,7 +6461,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "2c3c81b43dc2d8877c216a3fccf76677ee1ebccd429566d3e67447290d0c42b2"
 dependencies = [
  "bitcoin_hashes",
- "rand 0.9.0",
+ "rand 0.9.3",
  "secp256k1-sys 0.11.0",
 ]
 
@@ -7533,7 +7532,7 @@ version = "0.1.0"
 dependencies = [
  "malloc_size_of",
  "primitives",
- "rand 0.9.0",
+ "rand 0.9.3",
  "rand_xorshift 0.4.0",
 ]
 
@@ -8304,16 +8303,7 @@ version = "0.7.32"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "74d4d3961e53fa4c9a25a8637fc2bfaf2595b3d3ae34875568a5cf64787716be"
 dependencies = [
- "zerocopy-derive 0.7.32",
-]
-
-[[package]]
-name = "zerocopy"
-version = "0.8.24"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "2586fea28e186957ef732a5f8b3be2da217d65c5969d4b1e17f973ebbe876879"
-dependencies = [
- "zerocopy-derive 0.8.24",
+ "zerocopy-derive",
 ]
 
 [[package]]
@@ -8327,17 +8317,6 @@ dependencies = [
  "syn 2.0.111",
 ]
 
-[[package]]
-name = "zerocopy-derive"
-version = "0.8.24"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a996a8f63c5c4448cd959ac1bab0aaa3306ccfd060472f85943ee0750f0169be"
-dependencies = [
- "proc-macro2",
- "quote",
- "syn 2.0.111",
-]
-
 [[package]]
 name = "zerofrom"
 version = "0.1.5"
```

### tools/evm-spec-tester/Cargo.lock
```diff
@@ -71,7 +71,7 @@ dependencies = [
  "cfg-if 1.0.0",
  "once_cell",
  "version_check",
- "zerocopy 0.7.32",
+ "zerocopy",
 ]
 
 [[package]]
@@ -245,7 +245,7 @@ dependencies = [
  "keccak-asm",
  "paste",
  "proptest",
- "rand 0.9.0",
+ "rand 0.9.3",
  "ruint",
  "rustc-hash 2.1.1",
  "serde",
@@ -1145,7 +1145,7 @@ dependencies = [
  "metrics",
  "parking_lot 0.12.1",
  "primitives",
- "rand 0.9.0",
+ "rand 0.9.3",
  "txgen",
 ]
 
@@ -1414,7 +1414,7 @@ dependencies = [
  "network",
  "parking_lot 0.12.1",
  "primitives",
- "rand 0.9.0",
+ "rand 0.9.3",
  "toml 0.8.19",
  "txgen",
 ]
@@ -1559,7 +1559,7 @@ dependencies = [
  "malloc_size_of",
  "malloc_size_of_derive",
  "primitives",
- "rand 0.9.0",
+ "rand 0.9.3",
  "rand_xorshift 0.4.0",
  "treap-map",
  "typenum",
@@ -1610,7 +1610,7 @@ dependencies = [
  "jsonrpsee-core",
  "jsonrpsee-types",
  "log",
- "rand 0.9.0",
+ "rand 0.9.3",
  "serde",
  "strum 0.26.3",
  "thiserror 2.0.18",
@@ -1708,7 +1708,7 @@ dependencies = [
  "once_cell",
  "parity-version",
  "primitives",
- "rand 0.7.3",
+ "rand 0.9.3",
  "rustc-hex",
  "serde",
  "serde_derive",
@@ -1900,7 +1900,7 @@ dependencies = [
  "memoffset",
  "parking_lot 0.12.1",
  "primitives",
- "rand 0.9.0",
+ "rand 0.9.3",
  "rand_chacha 0.9.0",
  "random-crash",
  "rlp 0.4.6",
@@ -2073,7 +2073,7 @@ dependencies = [
  "primitives",
  "priority-send-queue",
  "rand 0.8.5",
- "rand 0.9.0",
+ "rand 0.9.3",
  "rand_xorshift 0.4.0",
  "rangetools",
  "rayon",
@@ -2201,7 +2201,7 @@ dependencies = [
  "log",
  "parity-wordlist",
  "parking_lot 0.12.1",
- "rand 0.9.0",
+ "rand 0.9.3",
  "rustc-hex",
  "serde",
  "serde_derive",
@@ -4715,7 +4715,7 @@ dependencies = [
  "jsonrpsee-types",
  "parking_lot 0.12.1",
  "pin-project",
- "rand 0.9.0",
+ "rand 0.9.3",
  "rustc-hash 2.1.1",
  "serde",
  "serde_json",
@@ -5014,7 +5014,7 @@ version = "0.1.0"
 dependencies = [
  "malloc_size_of",
  "parking_lot 0.12.1",
- "rand 0.9.0",
+ "rand 0.9.3",
 ]
 
 [[package]]
@@ -5078,7 +5078,7 @@ dependencies = [
  "log-mdc",
  "mock_instant",
  "parking_lot 0.12.1",
- "rand 0.9.0",
+ "rand 0.9.3",
  "serde",
  "serde-value",
  "serde_json",
@@ -5206,7 +5206,7 @@ dependencies = [
  "lazy_static",
  "log",
  "parking_lot 0.12.1",
- "rand 0.9.0",
+ "rand 0.9.3",
  "serde",
  "timer",
  "tokio",
@@ -5359,7 +5359,7 @@ dependencies = [
  "parity-path",
  "parking_lot 0.12.1",
  "priority-send-queue",
- "rand 0.9.0",
+ "rand 0.9.3",
  "rlp 0.4.6",
  "rlp-derive",
  "serde",
@@ -6169,7 +6169,7 @@ dependencies = [
  "log",
  "malloc_size_of",
  "once_cell",
- "rand 0.9.0",
+ "rand 0.9.3",
  "rlp 0.4.6",
  "rlp-derive",
  "serde",
@@ -6325,14 +6325,13 @@ dependencies = [
 
 [[package]]
 name = "rand"
-version = "0.9.0"
+version = "0.9.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "3779b94aeb87e8bd4e834cee3650289ee9e0d5677f976ecdb6d219e5f4f6cd94"
+checksum = "7ec095654a25171c2124e9e3393a930bddbffdc939556c914957a4c3e0a87166"
 dependencies = [
  "rand_chacha 0.9.0",
  "rand_core 0.9.3",
  "serde",
- "zerocopy 0.8.24",
 ]
 
 [[package]]
@@ -6427,7 +6426,7 @@ dependencies = [
  "lazy_static",
  "log",
  "parking_lot 0.12.1",
- "rand 0.9.0",
+ "rand 0.9.3",
 ]
 
 [[package]]
@@ -6854,7 +6853,7 @@ dependencies = [
  "primitive-types 0.12.2",
  "proptest",
  "rand 0.8.5",
- "rand 0.9.0",
+ "rand 0.9.3",
  "rlp 0.5.2",
  "ruint-macro",
  "serde_core",
@@ -7176,7 +7175,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "2c3c81b43dc2d8877c216a3fccf76677ee1ebccd429566d3e67447290d0c42b2"
 dependencies = [
  "bitcoin_hashes",
- "rand 0.9.0",
+ "rand 0.9.3",
  "secp256k1-sys 0.11.0",
 ]
 
@@ -8395,7 +8394,7 @@ version = "0.1.0"
 dependencies = [
  "malloc_size_of",
  "primitives",
- "rand 0.9.0",
+ "rand 0.9.3",
  "rand_xorshift 0.4.0",
 ]
 
@@ -8419,7 +8418,7 @@ dependencies = [
  "metrics",
  "parking_lot 0.12.1",
  "primitives",
- "rand 0.9.0",
+ "rand 0.9.3",
  "rlp 0.4.6",
  "rustc-hex",
  "secret-store",
@@ -9223,16 +9222,7 @@ version = "0.7.32"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "74d4d3961e53fa4c9a25a8637fc2bfaf2595b3d3ae34875568a5cf64787716be"
 dependencies = [
- "zerocopy-derive 0.7.32",
-]
-
-[[package]]
-name = "zerocopy"
-version = "0.8.24"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "2586fea28e186957ef732a5f8b3be2da217d65c5969d4b1e17f973ebbe876879"
-dependencies = [
- "zerocopy-derive 0.8.24",
+ "zerocopy-derive",
 ]
 
 [[package]]
@@ -9246,17 +9236,6 @@ dependencies = [
  "syn 2.0.111",
 ]
 
-[[package]]
-name = "zerocopy-derive"
-version = "0.8.24"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a996a8f63c5c4448cd959ac1bab0aaa3306ccfd060472f85943ee0750f0169be"
-dependencies = [
- "proc-macro2",
- "quote",
- "syn 2.0.111",
-]
-
 [[package]]
 name = "zerofrom"
 version = "0.1.5"
```
