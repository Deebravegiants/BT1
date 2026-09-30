# [?] [network] Update quinn-proto 0.11.3 -> 0.11.13 to fix DoS vulnerability (#18814)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-02-23
Source: https://github.com/aptos-labs/aptos-core/commit/6ffba7816cef6b8396f93428466e67b75ab265bc
Type: security-commit

## Details
[network] Update quinn-proto 0.11.3 -> 0.11.13 to fix DoS vulnerability (#18814)

Update quinn-proto to address a security vulnerability where calling
retry() on an unvalidated Incoming connection could cause a server panic
when subsequently calling refuse()/ignore() with duplicate initial packets,
or when accepting connections where the initial packet fails to decrypt or
exhausts connection IDs.

This vulnerability (present in quinn-proto < 0.11.9) allows denial of
service attacks against internet-facing servers.

The fix is a Cargo.lock-only change since quinn-proto is a transitive
dependency via gcloud-sdk -> reqwest 0.12.5 -> quinn -> quinn-proto.

Co-authored-by: Cursor Agent <cursoragent@cursor.com>

## Patch
### Cargo.lock
```diff
@@ -9981,9 +9981,11 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "26145e563e54f2cadc477553f1ec5ee650b00862f0a58bcd12cbdc5f0ea2d2f4"
 dependencies = [
  "cfg-if",
+ "js-sys",
  "libc",
  "r-efi",
  "wasi 0.14.2+wasi-0.2.4",
+ "wasm-bindgen",
 ]
 
 [[package]]
@@ -12055,6 +12057,12 @@ dependencies = [
  "hashbrown 0.15.3",
 ]
 
+[[package]]
+name = "lru-slab"
+version = "0.1.2"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "112b39cec0b298b6c1999fee3e31427f74f676e4cb9879ed1a121b43661a4154"
+
 [[package]]
 name = "lz4"
 version = "1.28.1"
@@ -15637,19 +15645,23 @@ dependencies = [
 
 [[package]]
 name = "quinn-proto"
-version = "0.11.3"
+version = "0.11.13"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "ddf517c03a109db8100448a4be38d498df8a210a99fe0e1b9eaf39e78c640efe"
+checksum = "f1906b49b0c3bc04b5fe5d86a77925ae6524a19b816ae38ce1e426255f1d8a31"
 dependencies = [
  "bytes",
- "rand 0.8.5",
+ "getrandom 0.3.3",
+ "lru-slab",
+ "rand 0.9.1",
  "ring 0.17.7",
- "rustc-hash 1.1.0",
+ "rustc-hash 2.1.1",
  "rustls 0.23.7",
+ "rustls-pki-types",
  "slab",
- "thiserror 1.0.69",
+ "thiserror 2.0.17",
  "tinyvec",
  "tracing",
+ "web-time",
 ]
 
 [[package]]
@@ -16605,6 +16617,9 @@ name = "rustls-pki-types"
 version = "1.10.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "d2bf47e6ff922db3825eb750c4e2ff784c6ff8fb9e13046ef6a1d1c5401b0b37"
+dependencies = [
+ "web-time",
+]
 
 [[package]]
 name = "rustls-webpki"
@@ -19915,6 +19930,16 @@ dependencies = [
  "wasm-bindgen",
 ]
 
+[[package]]
+name = "web-time"
+version = "1.1.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "5a6580f308b1fad9207618087a65c04e7a10bc77e02c8e84e9b00dd4b12fa0bb"
+dependencies = [
+ "js-sys",
+ "wasm-bindgen",
+]
+
 [[package]]
 name = "webpki"
 version = "0.22.4"
```
