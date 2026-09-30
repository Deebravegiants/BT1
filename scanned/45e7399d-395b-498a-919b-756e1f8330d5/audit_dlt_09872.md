# [?] fix(*): rustls RUSTSEC-2024-0399 (#4248)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2024-11-28
Source: https://github.com/iotaledger/iota/commit/b6a9a71a90b2c932e6090d86a0e8f253d0faabff
Type: security-commit

## Details
fix(*): rustls RUSTSEC-2024-0399 (#4248)

## Patch
### Cargo.lock
```diff
@@ -191,7 +191,7 @@ dependencies = [
  "rand 0.8.5",
  "rcgen",
  "ring 0.17.8",
- "rustls 0.23.13",
+ "rustls 0.23.18",
  "rustls-webpki 0.102.8",
  "serde",
  "serde_json",
@@ -1625,7 +1625,7 @@ dependencies = [
  "hyper 1.4.1",
  "hyper-util",
  "pin-project-lite",
- "rustls 0.23.13",
+ "rustls 0.23.18",
  "rustls-pemfile 2.1.3",
  "rustls-pki-types",
  "tokio",
@@ -2708,7 +2708,7 @@ dependencies = [
  "quinn-proto",
  "rand 0.8.5",
  "rstest",
- "rustls 0.23.13",
+ "rustls 0.23.18",
  "serde",
  "shared-crypto",
  "strum_macros 0.26.4",
@@ -5436,7 +5436,7 @@ dependencies = [
  "hyper 1.4.1",
  "hyper-util",
  "log",
- "rustls 0.23.13",
+ "rustls 0.23.18",
  "rustls-native-certs 0.8.0",
  "rustls-pki-types",
  "tokio",
@@ -7655,7 +7655,7 @@ dependencies = [
  "move-core-types",
  "rand 0.8.5",
  "reqwest 0.12.7",
- "rustls 0.23.13",
+ "rustls 0.23.18",
  "serde",
  "serde_json",
  "serde_with",
@@ -7903,7 +7903,7 @@ dependencies = [
  "percent-encoding",
  "prometheus",
  "reqwest 0.12.7",
- "rustls 0.23.13",
+ "rustls 0.23.18",
  "serde",
  "serde_json",
  "tap",
@@ -8023,7 +8023,7 @@ dependencies = [
  "rand 0.8.5",
  "rcgen",
  "reqwest 0.12.7",
- "rustls 0.23.13",
+ "rustls 0.23.18",
  "rustls-webpki 0.102.8",
  "tokio",
  "tokio-rustls 0.26.0",
@@ -8510,7 +8510,7 @@ dependencies = [
  "http 1.1.0",
  "jsonrpsee-core",
  "pin-project",
- "rustls 0.23.13",
+ "rustls 0.23.18",
  "rustls-pki-types",
  "rustls-platform-verifier",
  "soketto",
@@ -8563,7 +8563,7 @@ dependencies = [
  "hyper-util",
  "jsonrpsee-core",
  "jsonrpsee-types",
- "rustls 0.23.13",
+ "rustls 0.23.18",
  "rustls-platform-verifier",
  "serde",
  "serde_json",
@@ -11949,7 +11949,7 @@ dependencies = [
  "quinn-proto",
  "quinn-udp",
  "rustc-hash 2.0.0",
- "rustls 0.23.13",
+ "rustls 0.23.18",
  "socket2",
  "thiserror",
  "tokio",
@@ -11966,7 +11966,7 @@ dependencies = [
  "rand 0.8.5",
  "ring 0.17.8",
  "rustc-hash 2.0.0",
- "rustls 0.23.13",
+ "rustls 0.23.18",
  "slab",
  "thiserror",
  "tinyvec",
@@ -12397,7 +12397,7 @@ dependencies = [
  "percent-encoding",
  "pin-project-lite",
  "quinn",
- "rustls 0.23.13",
+ "rustls 0.23.18",
  "rustls-native-certs 0.7.3",
  "rustls-pemfile 2.1.3",
  "rustls-pki-types",
@@ -12865,9 +12865,9 @@ dependencies = [
 
 [[package]]
 name = "rustls"
-version = "0.23.13"
+version = "0.23.18"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f2dabaac7466917e566adb06783a81ca48944c6898a1b08b9374106dd671f4c8"
+checksum = "9c9cc1d47e243d655ace55ed38201c19ae02c148ae56412ab8750e8f0166ab7f"
 dependencies = [
  "aws-lc-rs",
  "log",
@@ -12938,9 +12938,9 @@ dependencies = [
 
 [[package]]
 name = "rustls-pki-types"
-version = "1.8.0"
+version = "1.10.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "fc0a2ce646f8655401bb81e7927b812614bd5d91dbc968696be50603510fcaf0"
+checksum = "16f1201b3c9a7ee8039bcadc17b7e605e2945b27eee7631788c1bd2b0643674b"
 
 [[package]]
 name = "rustls-platform-verifier"
@@ -12953,7 +12953,7 @@ dependencies = [
  "jni",
  "log",
  "once_cell",
- "rustls 0.23.13",
+ "rustls 0.23.18",
  "rustls-native-certs 0.7.3",
  "rustls-platform-verifier-android",
  "rustls-webpki 0.102.8",
@@ -14790,7 +14790,7 @@ version = "0.26.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "0c7bc40d0e5a97695bb96e27995cd3a08538541b0a846f65bba7a359f36700d4"
 dependencies = [
- "rustls 0.23.13",
+ "rustls 0.23.18",
  "rustls-pki-types",
  "tokio",
 ]
@@ -15554,7 +15554,7 @@ dependencies = [
  "flate2",
  "log",
  "once_cell",
- "rustls 0.23.13",
+ "rustls 0.23.18",
  "rustls-pki-types",
  "url",
  "webpki-roots 0.26.6",
```

### Cargo.toml
```diff
@@ -302,7 +302,7 @@ reqwest = { version = "0.12", default-features = false, features = ["http2", "js
 roaring = "0.10.6"
 rocksdb = { version = "0.21.0", default-features = false, features = ["snappy", "lz4", "zstd", "zlib", "multi-threaded-cf"] }
 rstest = "0.16.0"
-rustls = { version = "0.23", default-features = false, features = ["std", "tls12", "ring"] }
+rustls = { version = "0.23.18", default-features = false, features = ["std", "tls12", "ring"] }
 schemars = { version = "0.8.21", features = ["either"] }
 scopeguard = "1.1"
 serde = { version = "1.0.144", features = ["derive", "rc"] }
```

### crates/iota-storage/Cargo.toml
```diff
@@ -70,7 +70,7 @@ iota-types = { workspace = true, features = ["test-utils"] }
 [target.'cfg(msim)'.dependencies]
 # external dependencies
 axum.workspace = true
-rustls = "0.23"
+rustls = "0.23.18"
 
 # internal dependencies
 iota-simulator.workspace = true
```
