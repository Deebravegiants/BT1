# [?] [security] Upgrade rustls 0.21.10 to 0.21.12 to fix complete_io infinite loop DoS (#18815)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-02-23
Source: https://github.com/aptos-labs/aptos-core/commit/2cd764e7e0f366d0a1c22b9d0ceaa83683248e90
Type: security-commit

## Details
[security] Upgrade rustls 0.21.10 to 0.21.12 to fix complete_io infinite loop DoS (#18815)

Addresses CVE-2024-32650: rustls::ConnectionCommon::complete_io could fall
into an infinite loop when a client sends close_notify immediately after
client_hello. This causes 100% CPU usage on the affected thread, enabling
a denial-of-service attack against blocking rustls servers.

The fix upgrades rustls from 0.21.10 to 0.21.12 which contains the patch
for this vulnerability. This affects the following transitive dependencies:
- hyper-rustls 0.24.2
- reqwest (0.11.x)
- tokio-rustls 0.24.1
- tokio-tungstenite
- tungstenite

Note: rustls 0.20.9 (used by kube 0.65.0) remains unpatched as the 0.20.x
line is EOL with no security fix available. However, kube uses rustls via
tokio-rustls which does not call complete_io, so the vulnerable code path
is not reachable. rustls 0.22.4 and 0.23.7 are already patched.

Co-authored-by: Cursor Agent <cursoragent@cursor.com>

## Patch
### Cargo.lock
```diff
@@ -10819,7 +10819,7 @@ dependencies = [
  "http 0.2.11",
  "hyper 0.14.28",
  "log",
- "rustls 0.21.10",
+ "rustls 0.21.12",
  "rustls-native-certs 0.6.3",
  "tokio",
  "tokio-rustls 0.24.1",
@@ -16087,7 +16087,7 @@ dependencies = [
  "once_cell",
  "percent-encoding",
  "pin-project-lite",
- "rustls 0.21.10",
+ "rustls 0.21.12",
  "rustls-pemfile 1.0.4",
  "serde",
  "serde_json",
@@ -16507,9 +16507,9 @@ dependencies = [
 
 [[package]]
 name = "rustls"
-version = "0.21.10"
+version = "0.21.12"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f9d5a6813c0759e4609cd494e8e725babae6a2ca7b62a5536a13daaec6fcb7ba"
+checksum = "3f56a14d1f48b391359b22f731fd4bd7e43c97f3c50eee276f3aa09c94784d3e"
 dependencies = [
  "log",
  "ring 0.17.7",
@@ -18647,7 +18647,7 @@ version = "0.24.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "c28327cf380ac148141087fbfb9de9d7bd4e84ab5d2c28fbc911d753de8a7081"
 dependencies = [
- "rustls 0.21.10",
+ "rustls 0.21.12",
  "tokio",
 ]
 
@@ -18715,7 +18715,7 @@ checksum = "212d5dcb2a1ce06d81107c3d0ffa3121fe974b73f068c8282cb1c32328113b6c"
 dependencies = [
  "futures-util",
  "log",
- "rustls 0.21.10",
+ "rustls 0.21.12",
  "tokio",
  "tokio-rustls 0.24.1",
  "tungstenite",
@@ -19231,7 +19231,7 @@ dependencies = [
  "httparse",
  "log",
  "rand 0.8.5",
- "rustls 0.21.10",
+ "rustls 0.21.12",
  "sha1",
  "thiserror 1.0.69",
  "url",
```
