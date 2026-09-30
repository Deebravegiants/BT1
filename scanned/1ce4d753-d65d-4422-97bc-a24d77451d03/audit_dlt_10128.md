# [?] Merge pull request #4429 from eval-exec/exec/revert-4437.ignore-RUSTSEC-2024-0336

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2024-04-22
Source: https://github.com/nervosnetwork/ckb/commit/ba9c1f7dc1bcd9bc3b148c13b2f6ccc7192ce8d5
Type: security-commit

## Details
Merge pull request #4429 from eval-exec/exec/revert-4437.ignore-RUSTSEC-2024-0336

Revert #4427, ignore `RUSTSEC-2024-0336`

## Patch
### .github/workflows/ci_unit_tests_windows.yaml
```diff
@@ -62,8 +62,6 @@ jobs:
         scoop install git
         scoop bucket add extras
         scoop install llvm
-    - name: Install nextest dependency
-      run: scoop install jq
     - name: Install nextest-rs/nextest
       uses: taiki-e/install-action@nextest
     - run: |
```

### Cargo.lock
```diff
@@ -4593,11 +4593,25 @@ dependencies = [
  "libc",
  "once_cell",
  "spin 0.5.2",
- "untrusted",
+ "untrusted 0.7.1",
  "web-sys",
  "winapi",
 ]
 
+[[package]]
+name = "ring"
+version = "0.17.7"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "688c63d65483050968b2a8937f7995f443e27041a0f7700aa59b0822aedebb74"
+dependencies = [
+ "cc",
+ "getrandom 0.2.12",
+ "libc",
+ "spin 0.9.8",
+ "untrusted 0.9.0",
+ "windows-sys 0.48.0",
+]
+
 [[package]]
 name = "rust-ini"
 version = "0.19.0"
@@ -4642,6 +4656,27 @@ dependencies = [
  "windows-sys 0.52.0",
 ]
 
+[[package]]
+name = "rustls"
+version = "0.20.9"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "1b80e3dec595989ea8510028f30c408a4630db12c9cbb8de34203b89d6577e99"
+dependencies = [
+ "log",
+ "ring 0.16.20",
+ "sct",
+ "webpki",
+]
+
+[[package]]
+name = "rustls-pemfile"
+version = "1.0.4"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "1c74cae0a4cf6ccbbf5f359f08efdf8ee7e1dc532573bf0db71968cb56b1448c"
+dependencies = [
+ "base64 0.21.7",
+]
+
 [[package]]
 name = "rustversion"
 version = "1.0.14"
@@ -4710,6 +4745,16 @@ dependencies = [
  "syn 1.0.109",
 ]
 
+[[package]]
+name = "sct"
+version = "0.7.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "da046153aa2352493d6cb7da4b6e5c0c057d8a1d0a9aa8560baffdd945acd414"
+dependencies = [
+ "ring 0.17.7",
+ "untrusted 0.9.0",
+]
+
 [[package]]
 name = "secp256k1"
 version = "0.24.3"
@@ -5158,6 +5203,8 @@ dependencies = [
  "paste",
  "percent-encoding",
  "rand 0.8.5",
+ "rustls",
+ "rustls-pemfile",
  "serde",
  "serde_json",
  "sha1",
@@ -5169,6 +5216,7 @@ dependencies = [
  "thiserror",
  "tokio-stream",
  "url",
+ "webpki-roots",
  "whoami",
 ]
 
@@ -5197,10 +5245,9 @@ version = "0.6.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "804d3f245f894e61b1e6263c84b23ca675d96753b5abfd5cc8597d86806e8024"
 dependencies = [
- "native-tls",
  "once_cell",
  "tokio",
- "tokio-native-tls",
+ "tokio-rustls",
 ]
 
 [[package]]
@@ -5350,7 +5397,7 @@ dependencies = [
  "rand 0.7.3",
  "rand 0.8.5",
  "rand_core 0.5.1",
- "ring",
+ "ring 0.16.20",
  "secp256k1",
  "sha2",
  "tokio",
@@ -5593,6 +5640,17 @@ dependencies = [
  "tokio",
 ]
 
+[[package]]
+name = "tokio-rustls"
+version = "0.23.4"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "c43ee83903113e03984cb9e5cebe6c04a5116269e900e3ddba8f068a62adda59"
+dependencies = [
+ "rustls",
+ "tokio",
+ "webpki",
+]
+
 [[package]]
 name = "tokio-stream"
 version = "0.1.14"
@@ -5996,6 +6054,12 @@ version = "0.7.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "a156c684c91ea7d62626509bce3cb4e1d9ed5c4d978f7b4352658f96a4c26b4a"
 
+[[package]]
+name = "untrusted"
+version = "0.9.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "8ecb6da28b8a351d773b68d5825ac39017e680750f980f3a1a85cd8dd28a47c1"
+
 [[package]]
 name = "url"
 version = "2.5.0"
@@ -6170,6 +6234,25 @@ dependencies = [
  "wasm-bindgen",
 ]
 
+[[package]]
+name = "webpki"
+version = "0.22.4"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "ed63aea5ce73d0ff405984102c42de94fc55a6b75765d621c65262469b3c9b53"
+dependencies = [
+ "ring 0.17.7",
+ "untrusted 0.9.0",
+]
+
+[[package]]
+name = "webpki-roots"
+version = "0.22.6"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "b6c71e40d7d2c34a5106301fb632274ca37242cd0c9d3e64dbece371a40a2d87"
+dependencies = [
+ "webpki",
+]
+
 [[package]]
 name = "which"
 version = "4.4.2"
```

### deny.toml
```diff
@@ -7,7 +7,10 @@ ignore = [
     # The CVE can be kept under control for its triggering.
     # See https://github.com/launchbadge/sqlx/pull/2455#issuecomment-1507657825 for more information.
     # Meanwhile, awaiting SQLx's new version (> 0.7.3) for full support of any DB driver.
-    "RUSTSEC-2022-0090"
+    "RUSTSEC-2022-0090",
+    # ckb-rich-indexer need sqlx's runtime-tokio-rustls feature,
+    # ignore https://rustsec.org/advisories/RUSTSEC-2024-0336
+    "RUSTSEC-2024-0336"
 ]
 
 [licenses]
```

### util/rich-indexer/Cargo.toml
```diff
@@ -23,7 +23,7 @@ log = "0.4"
 num-bigint = "0.4"
 once_cell = "1.8.0"
 sql-builder = "3.1"
-sqlx = { version = "0.6", features = ["runtime-tokio-native-tls", "any", "sqlite", "postgres"] }
+sqlx = { version = "0.6", features = ["runtime-tokio-rustls", "any", "sqlite", "postgres"] }
 
 [dev-dependencies]
 hex = "0.4"
```
