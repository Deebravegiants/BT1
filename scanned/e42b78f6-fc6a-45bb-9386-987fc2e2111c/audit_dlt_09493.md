# [?] chore: update rustls for RUSTSEC-2026-0285 (#6897)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2026-09-17
Source: https://github.com/chainflip-io/chainflip-backend/commit/86863f7599037501383b84a8d21e7c6d20ed6a2e
Type: security-commit

## Details
chore: update rustls for RUSTSEC-2026-0285 (#6897)

## Patch
### Cargo.lock
```diff
@@ -5264,7 +5264,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "a8f2f12607f92c69b12ed746fabf9ca4f5c482cba46679c1a75b874ed7c26adb"
 dependencies = [
  "futures-io",
- "rustls 0.23.43",
+ "rustls 0.23.45",
  "rustls-pki-types",
 ]
 
@@ -6071,7 +6071,7 @@ dependencies = [
  "hyper 1.8.1",
  "hyper-util",
  "log",
- "rustls 0.23.43",
+ "rustls 0.23.45",
  "rustls-native-certs",
  "rustls-pki-types",
  "tokio",
@@ -6746,7 +6746,7 @@ dependencies = [
  "http 1.4.0",
  "jsonrpsee-core",
  "pin-project",
- "rustls 0.23.43",
+ "rustls 0.23.45",
  "rustls-pki-types",
  "rustls-platform-verifier",
  "soketto",
@@ -6799,7 +6799,7 @@ dependencies = [
  "hyper-util",
  "jsonrpsee-core",
  "jsonrpsee-types",
- "rustls 0.23.43",
+ "rustls 0.23.45",
  "rustls-platform-verifier",
  "serde",
  "serde_json",
@@ -7322,7 +7322,7 @@ dependencies = [
  "quinn",
  "rand 0.8.5",
  "ring 0.17.14",
- "rustls 0.23.43",
+ "rustls 0.23.45",
  "socket2 0.5.10",
  "thiserror 1.0.69",
  "tokio",
@@ -7414,7 +7414,7 @@ dependencies = [
  "libp2p-identity",
  "rcgen",
  "ring 0.17.14",
- "rustls 0.23.43",
+ "rustls 0.23.45",
  "rustls-webpki 0.101.7",
  "thiserror 1.0.69",
  "x509-parser 0.16.0",
@@ -10919,7 +10919,7 @@ dependencies = [
  "quinn-proto",
  "quinn-udp",
  "rustc-hash 2.1.1",
- "rustls 0.23.43",
+ "rustls 0.23.45",
  "socket2 0.6.2",
  "thiserror 2.0.18",
  "tokio",
@@ -10939,7 +10939,7 @@ dependencies = [
  "rand 0.9.4",
  "ring 0.17.14",
  "rustc-hash 2.1.1",
- "rustls 0.23.43",
+ "rustls 0.23.45",
  "rustls-pki-types",
  "slab",
  "thiserror 2.0.18",
@@ -11339,7 +11339,7 @@ dependencies = [
  "percent-encoding",
  "pin-project-lite",
  "quinn",
- "rustls 0.23.43",
+ "rustls 0.23.45",
  "rustls-pki-types",
  "serde",
  "serde_json",
@@ -11589,15 +11589,15 @@ dependencies = [
 
 [[package]]
 name = "rustls"
-version = "0.23.43"
+version = "0.23.45"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0283386ce02abc0151e1761d08802dfe86c173b0b494af5cbc086574e453da06"
+checksum = "0d41d731c7d2f962d1ccc364cec258de3c0e93b38c2fb3ba97ac74513048d634"
 dependencies = [
  "log",
  "once_cell",
  "ring 0.17.14",
  "rustls-pki-types",
- "rustls-webpki 0.103.12",
+ "rustls-webpki 0.103.15",
  "subtle 2.6.1",
  "zeroize",
 ]
@@ -11644,10 +11644,10 @@ dependencies = [
  "jni",
  "log",
  "once_cell",
- "rustls 0.23.43",
+ "rustls 0.23.45",
  "rustls-native-certs",
  "rustls-platform-verifier-android",
- "rustls-webpki 0.103.12",
+ "rustls-webpki 0.103.15",
  "security-framework",
  "security-framework-sys",
  "webpki-root-certs 0.26.11",
@@ -11672,9 +11672,9 @@ dependencies = [
 
 [[package]]
 name = "rustls-webpki"
-version = "0.103.12"
+version = "0.103.15"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8279bb85272c9f10811ae6a6c547ff594d6a7f3c6c6b02ee9726d1d0dcfcdd06"
+checksum = "f3c3cf1d8b1e7d4927e2d154c3fcb02979afb9939629c62cd9048d4f07b60ac2"
 dependencies = [
  "ring 0.17.14",
  "rustls-pki-types",
@@ -12483,7 +12483,7 @@ dependencies = [
  "parity-scale-codec",
  "parking_lot 0.12.5",
  "rand 0.8.5",
- "rustls 0.23.43",
+ "rustls 0.23.45",
  "sc-client-api",
  "sc-network",
  "sc-network-types",
@@ -15796,7 +15796,7 @@ version = "0.26.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "1729aa945f29d91ba541258c8df89027d5792d85a8841fb65e8bf0f4ede4ef61"
 dependencies = [
- "rustls 0.23.43",
+ "rustls 0.23.45",
  "tokio",
 ]
 
@@ -15835,7 +15835,7 @@ checksum = "489a59b6730eda1b0171fcfda8b121f4bee2b35cba8645ca35c5f7ba3eb736c1"
 dependencies = [
  "futures-util",
  "log",
- "rustls 0.23.43",
+ "rustls 0.23.45",
  "rustls-native-certs",
  "rustls-pki-types",
  "tokio",
@@ -16241,7 +16241,7 @@ dependencies = [
  "httparse",
  "log",
  "rand 0.9.4",
- "rustls 0.23.43",
+ "rustls 0.23.45",
  "rustls-pki-types",
  "sha1",
  "thiserror 2.0.18",
```

### state-chain/runtime-tests/Cargo.lock
```diff
@@ -7270,15 +7270,15 @@ dependencies = [
 
 [[package]]
 name = "rustls"
-version = "0.23.37"
+version = "0.23.45"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "758025cb5fccfd3bc2fd74708fd4682be41d99e5dff73c377c0646c6012c73a4"
+checksum = "0d41d731c7d2f962d1ccc364cec258de3c0e93b38c2fb3ba97ac74513048d634"
 dependencies = [
  "log",
  "once_cell",
  "ring 0.17.14",
  "rustls-pki-types",
- "rustls-webpki 0.103.9",
+ "rustls-webpki 0.103.15",
  "subtle 2.6.1",
  "zeroize",
 ]
@@ -7319,7 +7319,7 @@ dependencies = [
  "rustls",
  "rustls-native-certs",
  "rustls-platform-verifier-android",
- "rustls-webpki 0.103.9",
+ "rustls-webpki 0.103.15",
  "security-framework",
  "security-framework-sys",
  "webpki-root-certs 0.26.11",
@@ -7344,9 +7344,9 @@ dependencies = [
 
 [[package]]
 name = "rustls-webpki"
-version = "0.103.9"
+version = "0.103.15"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d7df23109aa6c1567d1c575b9952556388da57401e4ace1d15f79eedad0d8f53"
+checksum = "f3c3cf1d8b1e7d4927e2d154c3fcb02979afb9939629c62cd9048d4f07b60ac2"
 dependencies = [
  "ring 0.17.14",
  "rustls-pki-types",
```
