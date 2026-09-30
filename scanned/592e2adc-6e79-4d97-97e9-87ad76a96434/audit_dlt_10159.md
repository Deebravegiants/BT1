# [?] chore(deps): use patched sentry to fix RUSTSEC-2020-0041

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2020-12-16
Source: https://github.com/nervosnetwork/ckb/commit/bfe862b905be2f3448da6a21d22116ab10e0dc55
Type: security-commit

## Details
chore(deps): use patched sentry to fix RUSTSEC-2020-0041

## Patch
### Cargo.lock
```diff
@@ -420,11 +420,11 @@ dependencies = [
  "ckb-metrics-config",
  "ckb-pow",
  "ckb-resource",
+ "ckb-sentry",
  "ckb-types",
  "clap",
  "path-clean",
  "rand 0.6.5",
- "sentry",
  "serde",
  "serde_plain",
  "tempfile",
@@ -491,6 +491,7 @@ dependencies = [
  "ckb-network-alert",
  "ckb-resource",
  "ckb-rpc",
+ "ckb-sentry",
  "ckb-shared",
  "ckb-store",
  "ckb-sync",
@@ -500,7 +501,6 @@ dependencies = [
  "clap",
  "ctrlc",
  "rayon",
- "sentry",
  "serde",
  "serde_plain",
  "tempfile",
@@ -772,12 +772,12 @@ dependencies = [
  "chrono",
  "ckb-channel",
  "ckb-logger-config",
+ "ckb-sentry",
  "ckb-util",
  "env_logger",
  "log",
  "once_cell",
  "regex",
- "sentry",
 ]
 
 [[package]]
@@ -863,6 +863,7 @@ dependencies = [
  "ckb-app-config",
  "ckb-hash",
  "ckb-logger",
+ "ckb-sentry",
  "ckb-spawn",
  "ckb-stop-handler",
  "ckb-types",
@@ -877,7 +878,6 @@ dependencies = [
  "proptest",
  "rand 0.6.5",
  "secp256k1 0.19.0",
- "sentry",
  "serde",
  "serde_json",
  "snap",
@@ -1092,6 +1092,96 @@ dependencies = [
  "tiny-keccak 1.5.0",
 ]
 
+[[package]]
+name = "ckb-sentry"
+version = "0.21.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "21490dd3d6595e6cc1309c8328220a469d6a44d7966484776a29c978f6fce0c5"
+dependencies = [
+ "ckb-sentry-backtrace",
+ "ckb-sentry-contexts",
+ "ckb-sentry-core",
+ "ckb-sentry-log",
+ "ckb-sentry-panic",
+ "httpdate",
+ "reqwest",
+]
+
+[[package]]
+name = "ckb-sentry-backtrace"
+version = "0.21.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "d79f9a7879675c60c410900aa3219e054229d13dcfac6be02e5dd2e7aa394a2a"
+dependencies = [
+ "backtrace",
+ "ckb-sentry-core",
+ "lazy_static",
+ "regex",
+]
+
+[[package]]
+name = "ckb-sentry-contexts"
+version = "0.21.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "531c0484bf408d7b7df2853c329e1dd0604260fba655831623c2370f1a3a38dd"
+dependencies = [
+ "ckb-sentry-core",
+ "hostname",
+ "lazy_static",
+ "libc",
+ "regex",
+ "rustc_version",
+ "uname",
+]
+
+[[package]]
+name = "ckb-sentry-core"
+version = "0.21.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "9f47c8cae05a9a0ab147f01c8918f09df0e5f4334e045b9efb842db56291745c"
+dependencies = [
+ "ckb-sentry-types",
+ "lazy_static",
+ "rand 0.7.3",
+ "serde",
+ "serde_json",
+]
+
+[[package]]
+name = "ckb-sentry-log"
+version = "0.21.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "930dabc43171d69f320e636fad2c3713b9746ff475ee8d0a2ad7a01e0048347a"
+dependencies = [
+ "ckb-sentry-core",
+ "log",
+]
+
+[[package]]
+name = "ckb-sentry-panic"
+version = "0.21.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "f726ac09c3201b8ddbdd5d7b4e763082e59828624a68106259d19fa62e13bcf2"
+dependencies = [
+ "ckb-sentry-backtrace",
+ "ckb-sentry-core",
+]
+
+[[package]]
+name = "ckb-sentry-types"
+version = "0.21.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "2d62c3eded5c2af5ec8851b658a1eb149db487fbfe6a25a06ecf8da920c08886"
+dependencies = [
+ "chrono",
+ "debugid",
+ "serde",
+ "serde_json",
+ "thiserror",
+ "url 2.2.0",
+ "uuid",
+]
+
 [[package]]
 name = "ckb-shared"
 version = "0.39.0-pre"
@@ -1179,6 +1269,7 @@ dependencies = [
  "ckb-logger",
  "ckb-metrics",
  "ckb-network",
+ "ckb-sentry",
  "ckb-shared",
  "ckb-store",
  "ckb-test-chain-utils",
@@ -1192,7 +1283,6 @@ dependencies = [
  "governor",
  "lru",
  "rand 0.6.5",
- "sentry",
  "tempfile",
 ]
 
@@ -4378,89 +4468,6 @@ version = "0.7.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "388a1df253eca08550bef6c72392cfe7c30914bf41df5269b68cbd6ff8f570a3"
 
-[[package]]
-name = "sentry"
-version = "0.21.0"
-source = "git+https://github.com/nervosnetwork/sentry-rust?tag=sentry-v0.21.0-patch.1#ae2253866b7cfe895e962f01e3a894c5db841fb0"
-dependencies = [
- "httpdate",
- "reqwest",
- "sentry-backtrace",
- "sentry-contexts",
- "sentry-core",
- "sentry-log",
- "sentry-panic",
-]
-
-[[package]]
-name = "sentry-backtrace"
-version = "0.21.0"
-source = "git+https://github.com/nervosnetwork/sentry-rust?tag=sentry-v0.21.0-patch.1#ae2253866b7cfe895e962f01e3a894c5db841fb0"
-dependencies = [
- "backtrace",
- "lazy_static",
- "regex",
- "sentry-core",
-]
-
-[[package]]
-name = "sentry-contexts"
-version = "0.21.0"
-source = "git+https://github.com/nervosnetwork/sentry-rust?tag=sentry-v0.21.0-patch.1#ae2253866b7cfe895e962f01e3a894c5db841fb0"
-dependencies = [
- "hostname",
- "lazy_static",
- "libc",
- "regex",
- "rustc_version",
- "sentry-core",
- "uname",
-]
-
-[[package]]
-name = "sentry-core"
-version = "0.21.0"
-source = "git+https://github.com/nervosnetwork/sentry-rust?tag=sentry-v0.21.0-patch.1#ae2253866b7cfe895e962f01e3a894c5db841fb0"
-dependencies = [
- "lazy_static",
- "rand 0.7.3",
- "sentry-types",
- "serde",
- "serde_json",
-]
-
-[[package]]
-name = "sentry-log"
-version = "0.21.0"
-source = "git+https://github.com/nervosnetwork/sentry-rust?tag=sentry-v0.21.0-patch.1#ae2253866b7cfe895e962f01e3a894c5db841fb0"
-dependencies = [
- "log",
- "sentry-core",
-]
-
-[[package]]
-name = "sentry-panic"
-version = "0.21.0"
-source = "git+https://github.com/nervosnetwork/sentry-rust?tag=sentry-v0.21.0-patch.1#ae2253866b7cfe895e962f01e3a894c5db841fb0"
-dependencies = [
- "sentry-backtrace",
- "sentry-core",
-]
-
-[[package]]
-name = "sentry-types"
-version = "0.21.0"
-source = "git+https://github.com/nervosnetwork/sentry-rust?tag=sentry-v0.21.0-patch.1#ae2253866b7cfe895e962f01e3a894c5db841fb0"
-dependencies = [
- "chrono",
- "debugid",
- "serde",
- "serde_json",
- "thiserror",
- "url 2.2.0",
- "uuid",
-]
-
 [[package]]
 name = "serde"
 version = "1.0.105"
```

### Cargo.toml
```diff
@@ -100,4 +100,3 @@ profiling = ["jemallocator/profiling", "ckb-bin/profiling"]
 metrics         = { git = "https://github.com/nervosnetwork/metrics-rs", tag = "metrics-runtime-v0.13.1-patch.1" }
 metrics-runtime = { git = "https://github.com/nervosnetwork/metrics-rs", tag = "metrics-runtime-v0.13.1-patch.1" }
 metrics-core    = { git = "https://github.com/nervosnetwork/metrics-rs", tag = "metrics-runtime-v0.13.1-patch.1" }
-sentry          = { git = "https://github.com/nervosnetwork/sentry-rust", tag = "sentry-v0.21.0-patch.1" }
```

### ckb-bin/Cargo.toml
```diff
@@ -41,10 +41,10 @@ ckb-async-runtime = { path = "../util/runtime", version = "= 0.39.0-pre" }
 base64 = "0.10.1"
 tempfile = "3.0"
 rayon = "1.0"
-sentry = { version = "0.21.0", optional = true }
+sentry = { package = "ckb-sentry", version = "0.21.0", optional = true }
 
 [features]
 deadlock_detection = ["ckb-util/deadlock_detection"]
 profiling = ["ckb-memory-tracker/profiling"]
 with_sentry = ["sentry", "ckb-network/with_sentry", "ckb-sync/with_sentry", "ckb-app-config/with_sentry", "ckb-logger-service/with_sentry"]
-with_dns_seeding = ["ckb-network/with_dns_seeding"]
\ No newline at end of file
+with_dns_seeding = ["ckb-network/with_dns_seeding"]
```

### deny.toml
```diff
@@ -5,7 +5,6 @@ yanked = "deny"
 notice = "deny"
 ignore = [
     "RUSTSEC-2020-0016", # TODO net2 has been deprecated, but still a lot of required crates are dependent on it
-    "RUSTSEC-2020-0036", # TODO failure is officially deprecated/unmaintained, but still a lot of required crates are dependent on it
     "RUSTSEC-2020-0043", # TODO ws allows remote attacker to run the process out of memory, since it is no longer actively maintained, we couldn't fix it in the short term
     "RUSTSEC-2020-0056", # We did not use the `stdweb` library, only `wasm32-unknown-unknown` would use `getrandom` and `wasm-bindgen`, `stdweb` would only be used in cargo-web
     "RUSTSEC-2020-0082", # TODO ordered_float:NotNan may contain NaN after panic in assignment operators
@@ -48,5 +47,4 @@ unknown-git = "deny"
 allow-git = [
     # TODO fix RUSTSEC-2020-0041 temporarily
     "https://github.com/nervosnetwork/metrics-rs",
-    "https://github.com/nervosnetwork/sentry-rust",
 ]
```

### network/Cargo.toml
```diff
@@ -22,7 +22,7 @@ p2p = { version="0.3.3", package="tentacle", features = ["molc"] }
 faketime = "0.2.0"
 lazy_static = { version = "1.3.0", optional = true }
 bs58 = { version = "0.3.0", optional = true }
-sentry = { version = "0.21.0", optional = true }
+sentry = { package = "ckb-sentry", version = "0.21.0", optional = true }
 faster-hex = { version = "0.4", optional = true }
 ckb-hash = {path = "../util/hash", version = "= 0.39.0-pre"}
 secp256k1 = {version = "0.19", features = ["recovery"], optional = true }
```

### sync/Cargo.toml
```diff
@@ -26,7 +26,7 @@ ckb-chain-spec = { path = "../spec", version = "= 0.39.0-pre" }
 ckb-channel = { path = "../util/channel", version = "= 0.39.0-pre" }
 ckb-traits = { path = "../traits", version = "= 0.39.0-pre" }
 lru = "0.6.0"
-sentry = { version = "0.21.0", optional = true }
+sentry = { package = "ckb-sentry", version = "0.21.0", optional = true }
 futures = "0.3"
 ckb-error = {path = "../error", version = "= 0.39.0-pre"}
 ckb-tx-pool = { path = "../tx-pool", version = "= 0.39.0-pre" }
```

### util/app-config/Cargo.toml
```diff
@@ -27,7 +27,7 @@ ckb-fee-estimator = { path = "../fee-estimator", version = "= 0.39.0-pre" }
 secio = { version="0.4.2", features = ["molc"], package="tentacle-secio" }
 multiaddr = { version="0.2.0", package="tentacle-multiaddr" }
 rand = "0.6"
-sentry = { version = "0.21.0", optional = true }
+sentry = { package = "ckb-sentry", version = "0.21.0", optional = true }
 
 [features]
 with_sentry = ["sentry"]
```

### util/logger-service/Cargo.toml
```diff
@@ -19,7 +19,7 @@ once_cell = "1.3.1"
 regex = "1.1.6"
 chrono = "0.4"
 backtrace = "0.3"
-sentry = { version = "0.21.0", optional = true, features = ["log"] }
+sentry = { package = "ckb-sentry", version = "0.21.0", optional = true, features = ["log"] }
 
 [features]
 with_sentry = ["sentry"]
```
