# [?] fix: RUSTSEC-2025-0052 - remove async-std dependency (#6072)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2025-08-27
Source: https://github.com/chainflip-io/chainflip-backend/commit/8a278f8d452d8b3884a655e9eed3112eb4fe546d
Type: security-commit

## Details
fix: RUSTSEC-2025-0052 - remove async-std dependency (#6072)

## Patch
### Cargo.lock
```diff
@@ -535,21 +535,6 @@ dependencies = [
  "futures-lite",
 ]
 
-[[package]]
-name = "async-global-executor"
-version = "2.4.1"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "05b1b633a2115cd122d73b955eadd9916c18c8f510ec9cd1686404c60ad1c29c"
-dependencies = [
- "async-channel 2.3.1",
- "async-executor",
- "async-io",
- "async-lock",
- "blocking",
- "futures-lite",
- "once_cell",
-]
-
 [[package]]
 name = "async-io"
 version = "2.4.0"
@@ -628,33 +613,6 @@ dependencies = [
  "windows-sys 0.59.0",
 ]
 
-[[package]]
-name = "async-std"
-version = "1.13.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c634475f29802fde2b8f0b505b1bd00dfe4df7d4a000f0b36f7671197d5c3615"
-dependencies = [
- "async-channel 1.9.0",
- "async-global-executor",
- "async-io",
- "async-lock",
- "async-process",
- "crossbeam-utils",
- "futures-channel",
- "futures-core",
- "futures-io",
- "futures-lite",
- "gloo-timers 0.3.0",
- "kv-log-macro",
- "log",
- "memchr",
- "once_cell",
- "pin-project-lite",
- "pin-utils",
- "slab",
- "wasm-bindgen-futures",
-]
-
 [[package]]
 name = "async-stream"
 version = "0.3.6"
@@ -4632,7 +4590,7 @@ version = "3.0.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "f288b0a4f20f9a56b5d1da57e2227c661b7b16168e2f72365f57b63326e29b24"
 dependencies = [
- "gloo-timers 0.2.6",
+ "gloo-timers",
  "send_wrapper 0.4.0",
 ]
 
@@ -4848,18 +4806,6 @@ dependencies = [
  "wasm-bindgen",
 ]
 
-[[package]]
-name = "gloo-timers"
-version = "0.3.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "bbb143cf96099802033e0d4f4963b19fd2e0b728bcf076cd9cf7f6634f092994"
-dependencies = [
- "futures-channel",
- "futures-core",
- "js-sys",
- "wasm-bindgen",
-]
-
 [[package]]
 name = "gloo-utils"
 version = "0.2.0"
@@ -6241,15 +6187,6 @@ version = "1.0.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "c33070833c9ee02266356de0c43f723152bd38bd96ddf52c82b3af10c9138b28"
 
-[[package]]
-name = "kv-log-macro"
-version = "1.0.7"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0de8b303297635ad57c9f5059fd9cee7a47f8e8daa09df0fcd07dd39fb22977f"
-dependencies = [
- "log",
-]
-
 [[package]]
 name = "kvdb"
 version = "0.13.0"
@@ -7007,9 +6944,6 @@ name = "log"
 version = "0.4.25"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "04cbf5b083de1c7e0222a7a51dbfdba1cbe1c6ab0b15e29fff3f6c077fd9cd9f"
-dependencies = [
- "value-bag",
-]
 
 [[package]]
 name = "lru"
@@ -8098,7 +8032,6 @@ version = "0.27.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "231e9d6ceef9b0b2546ddf52335785ce41252bc7474ee8ba05bfad277be13ab8"
 dependencies = [
- "async-std",
  "async-trait",
  "futures-channel",
  "futures-executor",
@@ -15440,12 +15373,6 @@ version = "0.1.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "ba73ea9cf16a25df0c8caa16c51acb937d5712a8429db78a3ee29d5dcacd3a65"
 
-[[package]]
-name = "value-bag"
-version = "1.10.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "3ef4c4aa54d5d05a279399bfa921ec387b7aba77caf7a682ae8d86785b8fdad2"
-
 [[package]]
 name = "vcpkg"
 version = "0.2.15"
```

### api/bin/chainflip-elections-tracker/Cargo.toml
```diff
@@ -10,11 +10,7 @@ tracing = "0.1.41"
 tracing-core = "0.1.33"
 tracing-subscriber = "0.3.19"
 opentelemetry = "0.27.1"
-opentelemetry_sdk = { version = "0.27.1", features = [
-	"async-std",
-	"rt-tokio",
-	"trace",
-] }
+opentelemetry_sdk = { version = "0.27.1", features = ["rt-tokio", "trace"] }
 opentelemetry-otlp = { version = "0.27.0", features = ["grpc-tonic"] }
 
 # workspaced deps
```
