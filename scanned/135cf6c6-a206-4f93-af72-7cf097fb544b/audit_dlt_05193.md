# [?] Update lz4-sys to fix GHSA-9q5j-jm53-v7vr (CVE-2021-3520)

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-04-08
Source: https://github.com/Conflux-Chain/conflux-rust/commit/8f6606d5c972f2e5372db368d0716acbb657244f
Type: security-commit

## Details
Update lz4-sys to fix GHSA-9q5j-jm53-v7vr (CVE-2021-3520)

Update rust-rocksdb rev to use crates.io lz4-sys 1.11 instead of
the busyjay/lz4-rs fork (1.8.3). The fork was created in 2017 to add
header copying and cargo:root output for RocksDB integration, which
upstream lz4-sys now includes natively.

The old version bundled liblz4 1.8.3 vulnerable to integer overflow
during decompression (out-of-bounds write). Fixed in liblz4 1.9.4.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

## Patch
### Cargo.lock
```diff
@@ -5785,7 +5785,7 @@ checksum = "348108ab3fba42ec82ff6e9564fc4ca0247bdccdc68dd8af9764bbc79c3c8ffb"
 [[package]]
 name = "librocksdb_sys"
 version = "0.1.0"
-source = "git+https://github.com/Conflux-Chain/rust-rocksdb.git?rev=b84f1c0f549059602c1d51d87d2c1b01e931e5fd#b84f1c0f549059602c1d51d87d2c1b01e931e5fd"
+source = "git+https://github.com/Conflux-Chain/rust-rocksdb.git?rev=d0cd089bc092ec77b65a5262d453848f57abe3c3#d0cd089bc092ec77b65a5262d453848f57abe3c3"
 dependencies = [
  "bindgen",
  "bzip2-sys",
@@ -5802,7 +5802,7 @@ dependencies = [
 [[package]]
 name = "libtitan_sys"
 version = "0.0.1"
-source = "git+https://github.com/Conflux-Chain/rust-rocksdb.git?rev=b84f1c0f549059602c1d51d87d2c1b01e931e5fd#b84f1c0f549059602c1d51d87d2c1b01e931e5fd"
+source = "git+https://github.com/Conflux-Chain/rust-rocksdb.git?rev=d0cd089bc092ec77b65a5262d453848f57abe3c3#d0cd089bc092ec77b65a5262d453848f57abe3c3"
 dependencies = [
  "bzip2-sys",
  "cc",
@@ -5967,8 +5967,9 @@ checksum = "ab44e08e5b5110188be64dc8f0865635206ad7386fe672903bef195df3cc8960"
 
 [[package]]
 name = "lz4-sys"
-version = "1.8.3"
-source = "git+https://github.com/busyjay/lz4-rs.git?branch=adjust-build#5a8afe4010c67899fc7af876a58d67fd6269bf81"
+version = "1.11.1+lz4-1.10.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "6bd8c0d6c6ed0cd30b3652886bb8711dc4bb01d637a68105a3d5158039b418e6"
 dependencies = [
  "cc",
  "libc",
@@ -8139,7 +8140,7 @@ dependencies = [
 [[package]]
 name = "rocksdb"
 version = "0.3.0"
-source = "git+https://github.com/Conflux-Chain/rust-rocksdb.git?rev=b84f1c0f549059602c1d51d87d2c1b01e931e5fd#b84f1c0f549059602c1d51d87d2c1b01e931e5fd"
+source = "git+https://github.com/Conflux-Chain/rust-rocksdb.git?rev=d0cd089bc092ec77b65a5262d453848f57abe3c3#d0cd089bc092ec77b65a5262d453848f57abe3c3"
 dependencies = [
  "libc",
  "librocksdb_sys",
```

### Cargo.toml
```diff
@@ -468,7 +468,7 @@ sqlite3-sys = "0.12"
 kvdb = "0.13"
 influx_db_client = "0.5.1"
 # conflux forked crates
-rocksdb = { git = "https://github.com/Conflux-Chain/rust-rocksdb.git", rev = "b84f1c0f549059602c1d51d87d2c1b01e931e5fd" }
+rocksdb = { git = "https://github.com/Conflux-Chain/rust-rocksdb.git", rev = "d0cd089bc092ec77b65a5262d453848f57abe3c3" }
 
 [patch.crates-io]
 # use a forked version to fix a vulnerability(introduced by failure) in vrf-rs, can be removed after the upstream is fixed
```

### deny.toml
```diff
@@ -277,8 +277,6 @@ allow-git = [
     "https://github.com/paritytech/rust-secp256k1.git",
     "https://github.com/paritytech/rust-ctrlc.git",
 
-    # librocksdb_sys -> lz4-sys
-    "https://github.com/busyjay/lz4-rs.git?branch=adjust-build",
     # librocksdb_sys -> snappy-sys
     "https://github.com/busyjay/rust-snappy.git?branch=static-link",
 
```

### tools/consensus_bench/Cargo.lock
```diff
@@ -4410,7 +4410,7 @@ checksum = "348108ab3fba42ec82ff6e9564fc4ca0247bdccdc68dd8af9764bbc79c3c8ffb"
 [[package]]
 name = "librocksdb_sys"
 version = "0.1.0"
-source = "git+https://github.com/Conflux-Chain/rust-rocksdb.git?rev=b84f1c0f549059602c1d51d87d2c1b01e931e5fd#b84f1c0f549059602c1d51d87d2c1b01e931e5fd"
+source = "git+https://github.com/Conflux-Chain/rust-rocksdb.git?rev=d0cd089bc092ec77b65a5262d453848f57abe3c3#d0cd089bc092ec77b65a5262d453848f57abe3c3"
 dependencies = [
  "bindgen",
  "bzip2-sys",
@@ -4427,7 +4427,7 @@ dependencies = [
 [[package]]
 name = "libtitan_sys"
 version = "0.0.1"
-source = "git+https://github.com/Conflux-Chain/rust-rocksdb.git?rev=b84f1c0f549059602c1d51d87d2c1b01e931e5fd#b84f1c0f549059602c1d51d87d2c1b01e931e5fd"
+source = "git+https://github.com/Conflux-Chain/rust-rocksdb.git?rev=d0cd089bc092ec77b65a5262d453848f57abe3c3#d0cd089bc092ec77b65a5262d453848f57abe3c3"
 dependencies = [
  "bzip2-sys",
  "cc",
@@ -4560,8 +4560,9 @@ checksum = "ab44e08e5b5110188be64dc8f0865635206ad7386fe672903bef195df3cc8960"
 
 [[package]]
 name = "lz4-sys"
-version = "1.8.3"
-source = "git+https://github.com/busyjay/lz4-rs.git?branch=adjust-build#5a8afe4010c67899fc7af876a58d67fd6269bf81"
+version = "1.11.1+lz4-1.10.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "6bd8c0d6c6ed0cd30b3652886bb8711dc4bb01d637a68105a3d5158039b418e6"
 dependencies = [
  "cc",
  "libc",
@@ -6220,7 +6221,7 @@ dependencies = [
 [[package]]
 name = "rocksdb"
 version = "0.3.0"
-source = "git+https://github.com/Conflux-Chain/rust-rocksdb.git?rev=b84f1c0f549059602c1d51d87d2c1b01e931e5fd#b84f1c0f549059602c1d51d87d2c1b01e931e5fd"
+source = "git+https://github.com/Conflux-Chain/rust-rocksdb.git?rev=d0cd089bc092ec77b65a5262d453848f57abe3c3#d0cd089bc092ec77b65a5262d453848f57abe3c3"
 dependencies = [
  "libc",
  "librocksdb_sys",
```

### tools/evm-spec-tester/Cargo.lock
```diff
@@ -4984,7 +4984,7 @@ checksum = "348108ab3fba42ec82ff6e9564fc4ca0247bdccdc68dd8af9764bbc79c3c8ffb"
 [[package]]
 name = "librocksdb_sys"
 version = "0.1.0"
-source = "git+https://github.com/Conflux-Chain/rust-rocksdb.git?rev=b84f1c0f549059602c1d51d87d2c1b01e931e5fd#b84f1c0f549059602c1d51d87d2c1b01e931e5fd"
+source = "git+https://github.com/Conflux-Chain/rust-rocksdb.git?rev=d0cd089bc092ec77b65a5262d453848f57abe3c3#d0cd089bc092ec77b65a5262d453848f57abe3c3"
 dependencies = [
  "bindgen",
  "bzip2-sys",
@@ -5001,7 +5001,7 @@ dependencies = [
 [[package]]
 name = "libtitan_sys"
 version = "0.0.1"
-source = "git+https://github.com/Conflux-Chain/rust-rocksdb.git?rev=b84f1c0f549059602c1d51d87d2c1b01e931e5fd#b84f1c0f549059602c1d51d87d2c1b01e931e5fd"
+source = "git+https://github.com/Conflux-Chain/rust-rocksdb.git?rev=d0cd089bc092ec77b65a5262d453848f57abe3c3#d0cd089bc092ec77b65a5262d453848f57abe3c3"
 dependencies = [
  "bzip2-sys",
  "cc",
@@ -5134,8 +5134,9 @@ checksum = "ab44e08e5b5110188be64dc8f0865635206ad7386fe672903bef195df3cc8960"
 
 [[package]]
 name = "lz4-sys"
-version = "1.8.3"
-source = "git+https://github.com/busyjay/lz4-rs.git?branch=adjust-build#5a8afe4010c67899fc7af876a58d67fd6269bf81"
+version = "1.11.1+lz4-1.10.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "6bd8c0d6c6ed0cd30b3652886bb8711dc4bb01d637a68105a3d5158039b418e6"
 dependencies = [
  "cc",
  "libc",
@@ -6845,7 +6846,7 @@ dependencies = [
 [[package]]
 name = "rocksdb"
 version = "0.3.0"
-source = "git+https://github.com/Conflux-Chain/rust-rocksdb.git?rev=b84f1c0f549059602c1d51d87d2c1b01e931e5fd#b84f1c0f549059602c1d51d87d2c1b01e931e5fd"
+source = "git+https://github.com/Conflux-Chain/rust-rocksdb.git?rev=d0cd089bc092ec77b65a5262d453848f57abe3c3#d0cd089bc092ec77b65a5262d453848f57abe3c3"
 dependencies = [
  "libc",
  "librocksdb_sys",
```
