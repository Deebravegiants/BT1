# [?] revert lru version to fix use-after-free (#3107)

## Summary
Severity: Unknown
Chain: Starcoin
Component: starcoinorg/starcoin
Published: 2021-12-22
Source: https://github.com/starcoinorg/starcoin/commit/e7bfca286d7a07448e9e5b9d4b4aee830b3173c8
Type: security-commit

## Details
revert lru version to fix use-after-free (#3107)

## Patch
### Cargo.lock
```diff
@@ -4902,9 +4902,9 @@ dependencies = [
 
 [[package]]
 name = "lru"
-version = "0.7.1"
+version = "0.7.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "469898e909a1774d844793b347135a0cd344ca2f69d082013ecb8061a2229a3a"
+checksum = "6c748cfe47cb8da225c37595b3108bea1c198c84aaae8ea0ba76d01dda9fc803"
 dependencies = [
  "hashbrown 0.11.2",
 ]
@@ -5722,7 +5722,7 @@ dependencies = [
  "linked-hash-map",
  "linked_hash_set",
  "log 0.4.14",
- "lru 0.7.1",
+ "lru 0.7.0",
  "network-p2p-types",
  "once_cell",
  "parking_lot 0.11.2",
@@ -8596,7 +8596,7 @@ dependencies = [
  "bcs-ext",
  "byteorder 1.4.3",
  "itertools 0.10.3",
- "lru 0.7.1",
+ "lru 0.7.0",
  "mirai-annotations",
  "once_cell",
  "parking_lot 0.11.2",
@@ -9385,7 +9385,7 @@ dependencies = [
  "futures-timer",
  "hex",
  "log 0.4.14",
- "lru 0.7.1",
+ "lru 0.7.0",
  "network-api",
  "network-p2p",
  "network-p2p-types",
@@ -9881,7 +9881,7 @@ dependencies = [
  "anyhow",
  "bcs-ext",
  "forkable-jellyfish-merkle",
- "lru 0.7.1",
+ "lru 0.7.0",
  "parking_lot 0.11.2",
  "serde",
  "starcoin-crypto",
@@ -9903,7 +9903,7 @@ dependencies = [
  "chrono",
  "coarsetime",
  "forkable-jellyfish-merkle",
- "lru 0.7.1",
+ "lru 0.7.0",
  "num_enum",
  "once_cell",
  "parking_lot 0.11.2",
```

### commons/accumulator/Cargo.toml
```diff
@@ -17,7 +17,7 @@ logger = {path = "../../commons/logger", package="starcoin-logger"}
 starcoin-crypto = { package="starcoin-crypto", path = "../../commons/crypto"}
 bcs-ext = { package="bcs-ext", path = "../../commons/bcs_ext" }
 serde = { version = "1.0.130" }
-lru = "0.7.1"
+lru = "0.7.0"
 parking_lot = "0.11.2"
 schemars = {git = "https://github.com/starcoinorg/schemars", rev="3f8ecc27f02b27d56c716de58d7880ae7816390c"}
 
```

### network-p2p/Cargo.toml
```diff
@@ -24,7 +24,7 @@ futures-timer = "3.0"
 linked-hash-map = "0.5.4"
 linked_hash_set = "0.1.3"
 log = "0.4.14"
-lru = "0.7.1"
+lru = "0.7.0"
 parking_lot = "0.11.2"
 rand = "0.8.4"
 pin-project = "0.4.27"
```

### network/Cargo.toml
```diff
@@ -33,7 +33,7 @@ bitflags = "1.3.2"
 tempfile = "3.1.0"
 rand = "0.8.4"
 parking_lot = "0.11.2"
-lru = "0.7.1"
+lru = "0.7.0"
 
 serde = { version = "1.0.130", features = ["derive"] }
 serde_json = { version="1.0", features = ["arbitrary_precision"]}
```

### state/statedb/Cargo.toml
```diff
@@ -10,7 +10,7 @@ edition = "2018"
 anyhow = "1.0.41"
 thiserror = "1.0"
 parking_lot = "0.11.2"
-lru = "0.7.1"
+lru = "0.7.0"
 starcoin-types = {path = "../../types"}
 starcoin-vm-types = {path = "../../vm/types"}
 starcoin-state-api = {path = "../api"}
```

### storage/Cargo.toml
```diff
@@ -15,7 +15,7 @@ crypto = { package="starcoin-crypto", path = "../commons/crypto"}
 bcs-ext = { package="bcs-ext", path = "../commons/bcs_ext" }
 chrono = "0.4"
 byteorder = "1.4.3"
-lru = "0.7.1"
+lru = "0.7.0"
 parking_lot = "0.11.2"
 proptest = { version = "1.0.0", optional = true }
 proptest-derive = { version = "0.3.0", optional = true }
```
