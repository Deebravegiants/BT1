# [?] Updated 'hickory-proto' due to 'RUSTSEC-2025-0006'

## Summary
Severity: Unknown
Chain: Ethereum
Component: grandinetech/grandine
Published: 2025-02-11
Source: https://github.com/grandinetech/grandine/commit/28c00b64ea124d0d69a8544b8354713aa2c6cd56
Type: security-commit

## Details
Updated 'hickory-proto' due to 'RUSTSEC-2025-0006'

## Patch
### Cargo.lock
```diff
@@ -439,7 +439,7 @@ dependencies = [
  "futures-core",
  "futures-io",
  "futures-lite",
- "gloo-timers",
+ "gloo-timers 0.3.0",
  "kv-log-macro",
  "log",
  "memchr",
@@ -2444,6 +2444,7 @@ dependencies = [
  "std_ext",
  "strum",
  "tempfile",
+ "thiserror 1.0.69",
  "tiny-keccak",
  "tokio",
  "tokio-io-timeout",
@@ -2903,6 +2904,10 @@ name = "futures-timer"
 version = "3.0.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "f288b0a4f20f9a56b5d1da57e2227c661b7b16168e2f72365f57b63326e29b24"
+dependencies = [
+ "gloo-timers 0.2.6",
+ "send_wrapper",
+]
 
 [[package]]
 name = "futures-util"
@@ -3010,6 +3015,18 @@ version = "0.3.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "d2fabcfbdc87f4758337ca535fb41a6d701b65693ce38287d856d1674551ec9b"
 
+[[package]]
+name = "gloo-timers"
+version = "0.2.6"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "9b995a66bb87bebce9a0f4a95aed01daca4872c050bfcb21653361c03bc35e5c"
+dependencies = [
+ "futures-channel",
+ "futures-core",
+ "js-sys",
+ "wasm-bindgen",
+]
+
 [[package]]
 name = "gloo-timers"
 version = "0.3.0"
@@ -3044,7 +3061,6 @@ dependencies = [
  "either",
  "fnv",
  "futures",
- "futures-ticker",
  "futures-timer",
  "getrandom",
  "hashlink",
@@ -3360,9 +3376,9 @@ checksum = "b07f60793ff0a4d9cef0f18e63b5357e06209987153a64648c972c1e5aff336f"
 
 [[package]]
 name = "hickory-proto"
-version = "0.24.2"
+version = "0.24.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "447afdcdb8afb9d0a852af6dc65d9b285ce720ed7a59e42a8bf2e931c67bc1b5"
+checksum = "2ad3d6d98c648ed628df039541a5577bee1a7c83e9e16fe3dbedeea4cdfeb971"
 dependencies = [
  "async-trait",
  "cfg-if",
@@ -7000,6 +7016,12 @@ version = "1.0.24"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "3cb6eb87a131f756572d7fb904f6e7b68633f09cca868c5df1c4b8d1a694bbba"
 
+[[package]]
+name = "send_wrapper"
+version = "0.4.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "f638d531eccd6e23b980caf34876660d38e265409d8e99b397ab71eb3612fad0"
+
 [[package]]
 name = "serde"
 version = "1.0.216"
```
