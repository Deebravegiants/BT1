# [?] bump color-eyre version to avoid a panic when printing spantraces (#1438)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2020-12-02
Source: https://github.com/ZcashFoundation/zebra/commit/d7bef1c15573a3d32199af58951c19905811e355
Type: security-commit

## Details
bump color-eyre version to avoid a panic when printing spantraces (#1438)

## Patch
### Cargo.lock
```diff
@@ -478,9 +478,9 @@ dependencies = [
 
 [[package]]
 name = "color-eyre"
-version = "0.5.8"
+version = "0.5.9"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8fb57305b07ffcc1a4d08808f1f2200647c8e3d91a4c83d2810ae20c997274e0"
+checksum = "4cd93ec975c58d2e669fcfd09bcbb38a9ea4a182dd612e0855a3503b825e393b"
 dependencies = [
  "backtrace",
  "color-spantrace",
@@ -494,11 +494,12 @@ dependencies = [
 
 [[package]]
 name = "color-spantrace"
-version = "0.1.4"
+version = "0.1.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6a99aa4aa18448eef4c7d3f86d2720d2d8cad5c860fe9ff9b279293efdc8f5be"
+checksum = "b6eee477a4a8a72f4addd4de416eb56d54bc307b284d6601bafdee1f4ea462d1"
 dependencies = [
- "ansi_term 0.11.0",
+ "once_cell",
+ "owo-colors",
  "tracing-core",
  "tracing-error",
 ]
```

### tower-batch/Cargo.toml
```diff
@@ -21,4 +21,4 @@ tokio = { version = "0.3", features = ["full"]}
 tracing = "0.1.22"
 zebra-test = { path = "../zebra-test/" }
 tower-fallback = { path = "../tower-fallback/" }
-color-eyre = "0.5"
+color-eyre = "0.5.9"
```

### zebra-chain/Cargo.toml
```diff
@@ -46,7 +46,7 @@ bitflags = "1.2.1"
 
 [dev-dependencies]
 bincode = "1"
-color-eyre = "0.5"
+color-eyre = "0.5.9"
 spandoc = "0.2"
 tracing = "0.1.22"
 proptest = "0.10"
```

### zebra-consensus/Cargo.toml
```diff
@@ -7,7 +7,7 @@ edition = "2018"
 
 [dependencies]
 chrono = "0.4.19"
-color-eyre = "0.5"
+color-eyre = "0.5.9"
 displaydoc = "0.1.7"
 jubjub = "0.5.1"
 once_cell = "1.5"
```

### zebra-state/Cargo.toml
```diff
@@ -10,7 +10,7 @@ edition = "2018"
 [dependencies]
 zebra-chain = { path = "../zebra-chain" }
 
-color-eyre = "0.5"
+color-eyre = "0.5.9"
 dirs = "3.0.1"
 hex = "0.4.2"
 lazy_static = "1.4.0"
```

### zebra-test/Cargo.toml
```diff
@@ -12,7 +12,7 @@ hex = "0.4.2"
 lazy_static = "1.4.0"
 tower = { version = "0.4", features = ["util"] }
 futures = "0.3.7"
-color-eyre = "0.5.8"
+color-eyre = "0.5.9"
 tracing = "0.1.22"
 tracing-subscriber = "0.2.15"
 tracing-error = "0.1.2"
```

### zebra-utils/Cargo.toml
```diff
@@ -9,7 +9,7 @@ publish = false
 
 [dependencies]
 structopt = "0.3.21"
-color-eyre = "0.5.8"
+color-eyre = "0.5.9"
 hex = "0.4"
 serde_json = "1.0"
 tracing-error = { version = "0.1.2", features = ["traced-error"] }
```

### zebrad/Cargo.toml
```diff
@@ -25,7 +25,7 @@ tokio = { version = "0.3", features = ["time", "rt-multi-thread", "stream", "mac
 tower = { version = "0.4", features = ["hedge", "limit"] }
 pin-project = "0.4.23"
 
-color-eyre = { version = "0.5.8", features = ["issue-url"] }
+color-eyre = { version = "0.5.9", features = ["issue-url"] }
 thiserror = "1"
 
 tracing = "0.1"
```
