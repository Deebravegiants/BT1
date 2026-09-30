# [?] remove failure from depencies to solve security issue

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2025-06-12
Source: https://github.com/Conflux-Chain/conflux-rust/commit/d312752d48b568e5d64258394cd463d1d2dbc9dd
Type: security-commit

## Details
remove failure from depencies to solve security issue

update deny git whitelist

update

## Patch
### Cargo.lock
```diff
@@ -3400,28 +3400,6 @@ dependencies = [
  "rand 0.8.5",
 ]
 
-[[package]]
-name = "failure"
-version = "0.1.8"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d32e9bd16cc02eae7db7ef620b392808b89f6a5e16bb3497d159c6b92a0f4f86"
-dependencies = [
- "backtrace",
- "failure_derive",
-]
-
-[[package]]
-name = "failure_derive"
-version = "0.1.8"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "aa4da3c766cd7a0db8242e326e9e4e081edd567072893ed320008189715366a4"
-dependencies = [
- "proc-macro2",
- "quote",
- "syn 1.0.109",
- "synstructure 0.12.6",
-]
-
 [[package]]
 name = "fake-simd"
 version = "0.1.2"
@@ -9199,13 +9177,12 @@ checksum = "49874b5167b65d7193b8aba1567f5c7d93d001cafc34600cee003eda787e483f"
 
 [[package]]
 name = "vrf"
-version = "0.2.4"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "eff9943db5840ba292776c3778fedf9b97e11166d8222eceb2cb330f1ea08945"
+version = "0.2.5"
+source = "git+https://github.com/andrcmdr/vrf-rs.git?rev=f7bdb21f7f5d1858a3bb0183f194440f9a4199b3#f7bdb21f7f5d1858a3bb0183f194440f9a4199b3"
 dependencies = [
- "failure",
  "hmac-sha256",
  "openssl",
+ "thiserror 2.0.11",
 ]
 
 [[package]]
```

### Cargo.toml
```diff
@@ -335,6 +335,7 @@ blst = "0.3"
 #secp256k1 = "0.30.0"
 #rustls = "0.21"
 hashbrown = "0.7.1"
+vrf = "0.2"
 
 clap = "4"
 
@@ -454,4 +455,6 @@ influx_db_client = "0.5.1"
 rocksdb = { git = "https://github.com/Conflux-Chain/rust-rocksdb.git", rev = "7dbd66f507db1d0cfdf5334ad56ca0b24a768740" }
 
 [patch.crates-io]
+# use a forked version to fix a vulnerability(introduced by failure) in vrf-rs, can be removed after the upstream is fixed
+vrf = { git = "https://github.com/andrcmdr/vrf-rs.git", rev = "f7bdb21f7f5d1858a3bb0183f194440f9a4199b3" }
 sqlite3-sys = { git = "https://github.com/Conflux-Chain/sqlite3-sys.git", rev = "1de8e5998f7c2d919336660b8ef4e8f52ac43844" }
```

### crates/pos/crypto/crypto/Cargo.toml
```diff
@@ -35,7 +35,7 @@ diem-crypto-derive = { workspace = true }
 bcs = "0.1.2"
 cfx-types = { workspace = true }
 bls-signatures = { workspace = true }
-vrf = "0.2.2"
+vrf = { workspace = true }
 lazy_static = { workspace = true }
 parking_lot = { workspace = true }
 openssl = "0.10"
```

### deny.toml
```diff
@@ -275,7 +275,7 @@ allow-git = [
     # diem-logger -> pipe-logger-lib
     "https://github.com/aleksuss/pipe-logger-lib.git",
 
-
+    "https://github.com/andrcmdr/vrf-rs.git",
 ]
 
 [sources.allow-org]
```
