# [?] chore: Upgrade rustls to fix security vulnerability (#3331)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2024-11-25
Source: https://github.com/matter-labs/zksync-era/commit/193c855fc593f53b63d3eab9784ee2dae255205c
Type: security-commit

## Details
chore: Upgrade rustls to fix security vulnerability (#3331)

## What ❔
Upgrade rustls

## Why ❔
```
error[vulnerability]: rustls network-reachable panic in `Acceptor::accept`
    ┌─ /github/workspace/Cargo.lock:601:1
    │
601 │ rustls 0.23.16 registry+https://github.com/rust-lang/crates.io-index
    │ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ security vulnerability detected
    │
    ├ ID: RUSTSEC-[20](https://github.com/matter-labs/zksync-era/actions/runs/12011183823/job/33479628638?pr=3199#step:4:21)24-0399
    ├ Advisory: https://rustsec.org/advisories/RUSTSEC-2024-0399
    ├ A bug introduced in rustls 0.23.13 leads to a panic if the received
      TLS ClientHello is fragmented.  Only servers that use
      `rustls::server::Acceptor::accept()` are affected.
      
      Servers that use `tokio-rustls`'s `LazyConfigAcceptor` API are affected.
      
      Servers that use `tokio-rustls`'s `TlsAcceptor` API are not affected.
      
      Servers that use `rustls-ffi`'s `rustls_acceptor_accept` API are affected.
    ├ Announcement: https://github.com/rustls/rustls/issues/[22](https://github.com/matter-labs/zksync-era/actions/runs/12011183823/job/33479628638?pr=3199#step:4:23)27
    ├ Solution: Upgrade to >=0.[23](https://github.com/matter-labs/zksync-era/actions/runs/12011183823/job/33479628638?pr=3199#step:4:24).18 (try `cargo update -p rustls`)
```

## Patch
### Cargo.lock
```diff
@@ -1040,7 +1040,7 @@ dependencies = [
  "bitflags 2.6.0",
  "cexpr",
  "clang-sys",
- "itertools 0.12.1",
+ "itertools 0.10.5",
  "lazy_static",
  "lazycell",
  "log",
@@ -4156,7 +4156,7 @@ dependencies = [
  "hyper 1.5.0",
  "hyper-util",
  "log",
- "rustls 0.23.16",
+ "rustls 0.23.18",
  "rustls-native-certs 0.8.0",
  "rustls-pki-types",
  "tokio",
@@ -4568,7 +4568,7 @@ dependencies = [
  "http 1.1.0",
  "jsonrpsee-core 0.23.2",
  "pin-project",
- "rustls 0.23.16",
+ "rustls 0.23.18",
  "rustls-pki-types",
  "rustls-platform-verifier",
  "soketto 0.8.0",
@@ -4667,7 +4667,7 @@ dependencies = [
  "hyper-util",
  "jsonrpsee-core 0.23.2",
  "jsonrpsee-types 0.23.2",
- "rustls 0.23.16",
+ "rustls 0.23.18",
  "rustls-platform-verifier",
  "serde",
  "serde_json",
@@ -4920,7 +4920,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "4979f22fdb869068da03c9f7528f8297c6fd2606bc3a4affe42e6a823fdb8da4"
 dependencies = [
  "cfg-if",
- "windows-targets 0.52.6",
+ "windows-targets 0.48.5",
 ]
 
 [[package]]
@@ -6588,7 +6588,7 @@ checksum = "22505a5c94da8e3b7c2996394d1c933236c4d743e81a410bcca4e6989fc066a4"
 dependencies = [
  "bytes",
  "heck 0.5.0",
- "itertools 0.12.1",
+ "itertools 0.10.5",
  "log",
  "multimap",
  "once_cell",
@@ -6608,7 +6608,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "81bddcdb20abf9501610992b6759a4c888aef7d1a7247ef75e2404275ac24af1"
 dependencies = [
  "anyhow",
- "itertools 0.12.1",
+ "itertools 0.10.5",
  "proc-macro2 1.0.89",
  "quote 1.0.37",
  "syn 2.0.85",
@@ -6798,7 +6798,7 @@ dependencies = [
  "quinn-proto",
  "quinn-udp",
  "rustc-hash 2.0.0",
- "rustls 0.23.16",
+ "rustls 0.23.18",
  "socket2",
  "thiserror",
  "tokio",
@@ -6815,7 +6815,7 @@ dependencies = [
  "rand 0.8.5",
  "ring",
  "rustc-hash 2.0.0",
- "rustls 0.23.16",
+ "rustls 0.23.18",
  "slab",
  "thiserror",
  "tinyvec",
@@ -7118,7 +7118,7 @@ dependencies = [
  "percent-encoding",
  "pin-project-lite",
  "quinn",
- "rustls 0.23.16",
+ "rustls 0.23.18",
  "rustls-native-certs 0.8.0",
  "rustls-pemfile 2.2.0",
  "rustls-pki-types",
@@ -7434,9 +7434,9 @@ dependencies = [
 
 [[package]]
 name = "rustls"
-version = "0.23.16"
+version = "0.23.18"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "eee87ff5d9b36712a58574e12e9f0ea80f915a5b0ac518d322b24a465617925e"
+checksum = "9c9cc1d47e243d655ace55ed38201c19ae02c148ae56412ab8750e8f0166ab7f"
 dependencies = [
  "aws-lc-rs",
  "log",
@@ -7521,7 +7521,7 @@ dependencies = [
  "jni",
  "log",
  "once_cell",
- "rustls 0.23.16",
+ "rustls 0.23.18",
  "rustls-native-certs 0.7.3",
  "rustls-platform-verifier-android",
  "rustls-webpki 0.102.8",
@@ -9620,7 +9620,7 @@ version = "0.26.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "0c7bc40d0e5a97695bb96e27995cd3a08538541b0a846f65bba7a359f36700d4"
 dependencies = [
- "rustls 0.23.16",
+ "rustls 0.23.18",
  "rustls-pki-types",
  "tokio",
 ]
@@ -11494,7 +11494,7 @@ dependencies = [
  "octocrab",
  "regex",
  "reqwest 0.12.9",
- "rustls 0.23.16",
+ "rustls 0.23.18",
  "semver 1.0.23",
  "serde",
  "serde_json",
@@ -12965,7 +12965,7 @@ dependencies = [
  "pin-project-lite",
  "rand 0.8.5",
  "rlp",
- "rustls 0.23.16",
+ "rustls 0.23.18",
  "serde",
  "serde_json",
  "test-casing",
```

### deny.toml
```diff
@@ -12,7 +12,6 @@ ignore = [
     "RUSTSEC-2020-0168", # mach dependency being unmaintained, dependency in consensus, we should consider moving to mach2 fork
     "RUSTSEC-2024-0370", # `cs_derive` needs to be updated to not rely on `proc-macro-error`
     # all below caused by StructOpt which we still use and we should move to clap v4 instead
-    "RUSTSEC-2024-0375",
     "RUSTSEC-2021-0145",
     "RUSTSEC-2021-0139",
     "RUSTSEC-2024-0388", # `derivative` is unmaintained, crypto dependenicies (boojum, circuit_encodings and others) rely on it
```
