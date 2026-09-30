# [?] fix: RUSTSEC-2025-0055 - update tracing-subscriber (#6085)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2025-09-02
Source: https://github.com/chainflip-io/chainflip-backend/commit/a5a70a38f4082dac92dbfee3df4a361325162465
Type: security-commit

## Details
fix: RUSTSEC-2025-0055 - update tracing-subscriber (#6085)

## Patch
### Cargo.lock
```diff
@@ -1203,7 +1203,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "531a9155a481e2ee699d4f98f43c0ca4ff8ee1bfd55c31e9e98fb29d2b176fe0"
 dependencies = [
  "memchr",
- "regex-automata 0.4.9",
+ "regex-automata",
  "serde",
 ]
 
@@ -6247,7 +6247,7 @@ version = "0.20.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "507460a910eb7b32ee961886ff48539633b788a36b65692b95f225b844c82553"
 dependencies = [
- "regex-automata 0.4.9",
+ "regex-automata",
 ]
 
 [[package]]
@@ -7056,11 +7056,11 @@ checksum = "ffbee8634e0d45d258acb448e7eaab3fce7a0a467395d4d9f228e3c1f01fb2e4"
 
 [[package]]
 name = "matchers"
-version = "0.1.0"
+version = "0.2.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8263075bb86c5a1b1427b5ae862e8889656f126e9f77c484496e8b47cf5c5558"
+checksum = "d1525a2a28c7f4fa0fc98bb91ae755d1e2d1505079e05539e35bc876b5d65ae9"
 dependencies = [
- "regex-automata 0.1.10",
+ "regex-automata",
 ]
 
 [[package]]
@@ -7721,12 +7721,11 @@ checksum = "61807f77802ff30975e01f4f071c8ba10c022052f98b3294119f3e615d13e5be"
 
 [[package]]
 name = "nu-ansi-term"
-version = "0.46.0"
+version = "0.50.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "77a8165726e8236064dbb45459242600304b42a5ea24ee2948e18e023bf7ba84"
+checksum = "d4a28e057d01f97e61255210fcff094d74ed0466038633e95017f5beb68e4399"
 dependencies = [
- "overload",
- "winapi",
+ "windows-sys 0.52.0",
 ]
 
 [[package]]
@@ -8063,12 +8062,6 @@ dependencies = [
  "hashbrown 0.12.3",
 ]
 
-[[package]]
-name = "overload"
-version = "0.1.1"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b15813163c1d831bf4a13c3610c05c0d03b39feb07f7e09fa234dac9b15aaf39"
-
 [[package]]
 name = "pallet-aura"
 version = "36.0.0"
@@ -10130,19 +10123,10 @@ checksum = "b544ef1b4eac5dc2db33ea63606ae9ffcfac26c1416a2806ae0bf5f56b201191"
 dependencies = [
  "aho-corasick",
  "memchr",
- "regex-automata 0.4.9",
+ "regex-automata",
  "regex-syntax 0.8.5",
 ]
 
-[[package]]
-name = "regex-automata"
-version = "0.1.10"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6c230d73fb8d8c1b9c0b3135c5142a8acee3a0558fb8db5cf1cb65f8d7862132"
-dependencies = [
- "regex-syntax 0.6.29",
-]
-
 [[package]]
 name = "regex-automata"
 version = "0.4.9"
@@ -14961,15 +14945,15 @@ dependencies = [
 
 [[package]]
 name = "tracing-subscriber"
-version = "0.3.19"
+version = "0.3.20"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e8189decb5ac0fa7bc8b96b7cb9b2701d60d48805aca84a238004d665fcc4008"
+checksum = "2054a14f5307d601f88daf0553e1cbf472acc4f2c51afab632431cdcd72124d5"
 dependencies = [
  "matchers",
  "nu-ansi-term",
  "once_cell",
  "parking_lot 0.12.3",
- "regex",
+ "regex-automata",
  "serde",
  "serde_json",
  "sharded-slab",
```

### Cargo.toml
```diff
@@ -165,7 +165,7 @@ tokio = { version = "1.44.2" }
 tokio-stream = { version = "0.1.14" }
 toml = { version = "0.8.10" }
 tracing = { version = "0.1.37" }
-tracing-subscriber = { version = "0.3.18" }
+tracing-subscriber = { version = "0.3.20" }
 typenum = { version = "1.15" }
 url = { version = "2.4" }
 warp = { version = "0.3.6" }
```

### api/bin/chainflip-elections-tracker/Cargo.toml
```diff
@@ -8,7 +8,7 @@ license = "Apache-2.0"
 [dependencies]
 tracing = "0.1.41"
 tracing-core = "0.1.33"
-tracing-subscriber = "0.3.19"
+tracing-subscriber = { workspace = true }
 opentelemetry = "0.27.1"
 opentelemetry_sdk = { version = "0.27.1", features = ["rt-tokio", "trace"] }
 opentelemetry-otlp = { version = "0.27.0", features = ["grpc-tonic"] }
```
