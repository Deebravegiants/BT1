# [?] Fix keygen usb panic (debug only) (#31194)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana
Published: 2023-04-14
Source: https://github.com/solana-labs/solana/commit/2147f0d0568510bff1f37b99df708189cecfb731
Type: security-commit

## Details
Fix keygen usb panic (debug only) (#31194)

* Bump clap v3

* Use fallible method to check for confirm_key

## Patch
### Cargo.lock
```diff
@@ -1042,26 +1042,26 @@ dependencies = [
 
 [[package]]
 name = "clap"
-version = "3.1.8"
+version = "3.2.23"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "71c47df61d9e16dc010b55dba1952a57d8c215dbb533fd13cdd13369aac73b1c"
+checksum = "71655c45cb9845d3270c9d6df84ebe72b4dad3c2ba3f7023ad47c144e4e473a5"
 dependencies = [
  "atty",
  "bitflags",
  "clap_derive",
+ "clap_lex",
  "indexmap",
- "lazy_static",
- "os_str_bytes",
+ "once_cell",
  "strsim 0.10.0",
  "termcolor",
- "textwrap 0.15.0",
+ "textwrap 0.16.0",
 ]
 
 [[package]]
 name = "clap_derive"
-version = "3.1.7"
+version = "3.2.18"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a3aab4734e083b809aaf5794e14e756d1c798d2c69c7f7de7a09a2f5214993c1"
+checksum = "ea0c8bce528c4be4da13ea6fead8965e95b6073585a2f05204bd8f4119f82a65"
 dependencies = [
  "heck 0.4.0",
  "proc-macro-error",
@@ -1070,6 +1070,15 @@ dependencies = [
  "syn 1.0.107",
 ]
 
+[[package]]
+name = "clap_lex"
+version = "0.2.4"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "2850f2f5a82cbf437dd5af4d49848fbdfc27c157c3d010345776f952765261c5"
+dependencies = [
+ "os_str_bytes",
+]
+
 [[package]]
 name = "combine"
 version = "3.8.1"
@@ -3354,9 +3363,6 @@ name = "os_str_bytes"
 version = "6.0.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "8e22443d1643a904602595ba1cd8f7d896afe56d26712531c5ff73a15b2fbf64"
-dependencies = [
- "memchr",
-]
 
 [[package]]
 name = "ouroboros"
@@ -4135,7 +4141,7 @@ dependencies = [
 name = "rbpf-cli"
 version = "1.16.0"
 dependencies = [
- "clap 3.1.8",
+ "clap 3.2.23",
  "serde",
  "serde_json",
  "solana-bpf-loader-program",
@@ -4998,7 +5004,7 @@ dependencies = [
 name = "solana-banking-bench"
 version = "1.16.0"
 dependencies = [
- "clap 3.1.8",
+ "clap 3.2.23",
  "crossbeam-channel",
  "log",
  "rand 0.7.3",
@@ -5066,7 +5072,7 @@ dependencies = [
 name = "solana-bench-streamer"
 version = "1.16.0"
 dependencies = [
- "clap 3.1.8",
+ "clap 3.2.23",
  "crossbeam-channel",
  "solana-net-utils",
  "solana-streamer",
@@ -5183,7 +5189,7 @@ name = "solana-cargo-build-bpf"
 version = "1.16.0"
 dependencies = [
  "cargo_metadata",
- "clap 3.1.8",
+ "clap 3.2.23",
  "log",
  "solana-logger 1.16.0",
  "solana-sdk 1.16.0",
@@ -5196,7 +5202,7 @@ dependencies = [
  "assert_cmd",
  "bzip2",
  "cargo_metadata",
- "clap 3.1.8",
+ "clap 3.2.23",
  "log",
  "predicates",
  "regex",
@@ -5214,15 +5220,15 @@ name = "solana-cargo-test-bpf"
 version = "1.16.0"
 dependencies = [
  "cargo_metadata",
- "clap 3.1.8",
+ "clap 3.2.23",
 ]
 
 [[package]]
 name = "solana-cargo-test-sbf"
 version = "1.16.0"
 dependencies = [
  "cargo_metadata",
- "clap 3.1.8",
+ "clap 3.2.23",
  "log",
  "solana-logger 1.16.0",
 ]
@@ -5249,7 +5255,7 @@ name = "solana-clap-v3-utils"
 version = "1.16.0"
 dependencies = [
  "chrono",
- "clap 3.1.8",
+ "clap 3.2.23",
  "rpassword",
  "solana-perf",
  "solana-remote-wallet",
@@ -5536,7 +5542,7 @@ name = "solana-dos"
 version = "1.16.0"
 dependencies = [
  "bincode",
- "clap 3.1.8",
+ "clap 3.2.23",
  "crossbeam-channel",
  "itertools",
  "log",
@@ -5875,7 +5881,7 @@ name = "solana-keygen"
 version = "1.16.0"
 dependencies = [
  "bs58",
- "clap 3.1.8",
+ "clap 3.2.23",
  "dirs-next",
  "num_cpus",
  "solana-clap-v3-utils",
@@ -6044,7 +6050,7 @@ name = "solana-log-analyzer"
 version = "1.16.0"
 dependencies = [
  "byte-unit",
- "clap 3.1.8",
+ "clap 3.2.23",
  "serde",
  "serde_json",
  "solana-logger 1.16.0",
@@ -6125,7 +6131,7 @@ dependencies = [
 name = "solana-net-shaper"
 version = "1.16.0"
 dependencies = [
- "clap 3.1.8",
+ "clap 3.2.23",
  "rand 0.7.3",
  "serde",
  "serde_json",
@@ -6137,7 +6143,7 @@ name = "solana-net-utils"
 version = "1.16.0"
 dependencies = [
  "bincode",
- "clap 3.1.8",
+ "clap 3.2.23",
  "crossbeam-channel",
  "log",
  "nix",
@@ -6217,7 +6223,7 @@ dependencies = [
 name = "solana-poh-bench"
 version = "1.16.0"
 dependencies = [
- "clap 3.1.8",
+ "clap 3.2.23",
  "log",
  "rand 0.7.3",
  "rayon",
@@ -7731,9 +7737,9 @@ dependencies = [
 
 [[package]]
 name = "textwrap"
-version = "0.15.0"
+version = "0.16.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b1141d4d61095b28419e22cb0bbf02755f5e54e0526f97f1e3d1d160e60885fb"
+checksum = "222a222a5bfe1bba4a77b45ec488a741b3cb8872e5e499451fd7d0129c9c7c3d"
 
 [[package]]
 name = "thiserror"
```

### clap-v3-utils/Cargo.toml
```diff
@@ -11,7 +11,7 @@ edition = { workspace = true }
 
 [dependencies]
 chrono = { workspace = true, features = ["default"] }
-clap = { version = "3.1.5", features = ["cargo"] }
+clap = { version = "3.2.23", features = ["cargo"] }
 rpassword = { workspace = true }
 solana-perf = { workspace = true }
 solana-remote-wallet = { workspace = true }
```

### clap-v3-utils/src/keypair.rs
```diff
@@ -788,11 +788,12 @@ pub fn signer_from_path_with_config(
                 *wallet_manager = maybe_wallet_manager()?;
             }
             if let Some(wallet_manager) = wallet_manager {
+                let confirm_key = matches.try_contains_id("confirm_key").unwrap_or(false);
                 Ok(Box::new(generate_remote_keypair(
                     locator,
                     derivation_path.unwrap_or_default(),
                     wallet_manager,
-                    matches.is_present("confirm_key"),
+                    confirm_key,
                     keypair_name,
                 )?))
             } else {
@@ -915,11 +916,12 @@ pub fn resolve_signer_from_path(
                 *wallet_manager = maybe_wallet_manager()?;
             }
             if let Some(wallet_manager) = wallet_manager {
+                let confirm_key = matches.try_contains_id("confirm_key").unwrap_or(false);
                 let path = generate_remote_keypair(
                     locator,
                     derivation_path.unwrap_or_default(),
                     wallet_manager,
-                    matches.is_present("confirm_key"),
+                    confirm_key,
                     keypair_name,
                 )
                 .map(|keypair| keypair.path)?;
```
