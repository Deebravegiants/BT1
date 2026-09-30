# [?] fix(audit): bump time to 0.3.47 to fix RUSTSEC-2026-0009 (#15684)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-05-07
Source: https://github.com/near/nearcore/commit/d88271ea4fcc1eeb93646388318abcf0a73bb840
Type: security-commit

## Details
fix(audit): bump time to 0.3.47 to fix RUSTSEC-2026-0009 (#15684)

Bump `time` from 0.3.9 to 0.3.47 to address
[RUSTSEC-2026-0009](https://rustsec.org/advisories/RUSTSEC-2026-0009) —
a stack exhaustion DoS in RFC 2822 parsing. Drop the corresponding
ignore from `.cargo/audit.toml`.

This was previously blocked because `time >= 0.3.47` requires Rust 1.88;
the toolchain bump to 1.93 (#15681) unblocks it.

Supersedes #15009, which only updated the workspace `Cargo.toml`
constraint and didn't refresh the main `Cargo.lock`.

Closes #15026.

## Patch
### .cargo/audit.toml
```diff
@@ -31,10 +31,6 @@ ignore = [
     # TODO(#14768): Remove this and updated necessary crates to get rid of rustls-pemfile
     "RUSTSEC-2025-0134",
 
-    # time has a DoS vulnerability (stack exhaustion), fixed in 0.3.47+ which requires Rust 1.88
-    # TODO(#15026): Remove this when rust-toolchain.toml is updated to >= 1.88
-    "RUSTSEC-2026-0009",
-
     # libsecp256k1 is unmaintained, but every version of aurora-engine-transactions pulls it in
     # (via aurora-engine-precompiles in 1.1, or aurora-engine-sdk in 1.2+). In the main workspace
     # it's only a dev-dependency (test-loop-tests, integration-tests). It is also a transitive
```

### Cargo.lock
```diff
@@ -1817,12 +1817,12 @@ dependencies = [
 
 [[package]]
 name = "deranged"
-version = "0.3.11"
+version = "0.5.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b42b6fa04a440b495c8b04d0e71b707c585f83cb9cb28cf8cd0d976c315e31b4"
+checksum = "7cd812cc2bc1d69d4764bd80df88b4317eaef9e773c75226407d9bc0876b211c"
 dependencies = [
  "powerfmt",
- "serde",
+ "serde_core",
 ]
 
 [[package]]
@@ -5829,9 +5829,9 @@ dependencies = [
 
 [[package]]
 name = "num-conv"
-version = "0.1.0"
+version = "0.2.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "51d515d32fb182ee37cda2ccdcb92950d6a3c2893aa280e540671c2cd0f3b1d9"
+checksum = "c6673768db2d862beb9b39a78fdcb1a69439615d5794a1be50caa9bc92c81967"
 
 [[package]]
 name = "num-integer"
@@ -6692,7 +6692,7 @@ dependencies = [
  "quinn-udp",
  "rustc-hash 2.0.0",
  "rustls",
- "socket2 0.5.8",
+ "socket2 0.6.0",
  "thiserror 2.0.16",
  "tokio",
  "tracing",
@@ -6730,7 +6730,7 @@ dependencies = [
  "cfg_aliases",
  "libc",
  "once_cell",
- "socket2 0.5.8",
+ "socket2 0.6.0",
  "tracing",
  "windows-sys 0.60.2",
 ]
@@ -7552,7 +7552,7 @@ dependencies = [
  "security-framework 3.7.0",
  "security-framework-sys",
  "webpki-root-certs",
- "windows-sys 0.52.0",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
@@ -7789,18 +7789,28 @@ dependencies = [
 
 [[package]]
 name = "serde"
-version = "1.0.219"
+version = "1.0.228"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5f0e2c6ed6606019b4e29e69dbaba95b11854410e5347d525002456dbbb786b6"
+checksum = "9a8e94ea7f378bd32cbbd37198a4a91436180c5bb472411e48b5ec2e2124ae9e"
+dependencies = [
+ "serde_core",
+ "serde_derive",
+]
+
+[[package]]
+name = "serde_core"
+version = "1.0.228"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "41d385c7d4ca58e59fc732af25c3983b67ac852c1a25000afe1175de458b67ad"
 dependencies = [
  "serde_derive",
 ]
 
 [[package]]
 name = "serde_derive"
-version = "1.0.219"
+version = "1.0.228"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5b0276cf7f2c73365f7157c8123c21cd9a50fbbd844757af28ca1f5925fc2a00"
+checksum = "d540f220d3187173da220f885ab66608367b6574e925011a9353e4badda91d79"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -8597,30 +8607,30 @@ dependencies = [
 
 [[package]]
 name = "time"
-version = "0.3.36"
+version = "0.3.47"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5dfd88e563464686c916c7e46e623e520ddc6d79fa6641390f2e3fa86e83e885"
+checksum = "743bd48c283afc0388f9b8827b976905fb217ad9e647fae3a379a9283c4def2c"
 dependencies = [
  "deranged",
  "itoa",
  "num-conv",
  "powerfmt",
- "serde",
+ "serde_core",
  "time-core",
  "time-macros",
 ]
 
 [[package]]
 name = "time-core"
-version = "0.1.2"
+version = "0.1.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "ef927ca75afb808a4d64dd374f00a2adf8d0fcff8e7b184af886c3c87ec4a3f3"
+checksum = "7694e1cfe791f8d31026952abf09c69ca6f6fa4e1a1229e18988f06a04a12dca"
 
 [[package]]
 name = "time-macros"
-version = "0.2.18"
+version = "0.2.27"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "3f252a68540fde3a3877aeea552b832b40ab9a69e318efd078774a01ddee1ccf"
+checksum = "2e70e4c5a0e0a8a4823ad65dfe1a6930e4f4d756dcd9dd7939022b5e8c501215"
 dependencies = [
  "num-conv",
  "time-core",
```

### Cargo.toml
```diff
@@ -373,7 +373,7 @@ test-log = { version = "0.2", default-features = false, features = ["trace"] }
 thiserror = "2.0"
 thread-priority = "1.2.0"
 tikv-jemallocator = "0.5.0"
-time = { version = "0.3.9", default-features = false }
+time = { version = "0.3.47", default-features = false }
 tokio = { version = "1.28", default-features = false }
 tokio-stream = { version = "0.1.2", features = ["net"] }
 tokio-util = { version = "0.7.1", features = ["codec", "io"] }
```

### integration-tests/src/tests/tools/dependencies.rs
```diff
@@ -18,12 +18,12 @@ use std::process::Command;
 use std::str;
 
 const LIBS_THRESHOLDS: [(&str, usize); 9] = [
-    ("near-primitives", 129),
-    ("near-jsonrpc-primitives", 136),
-    ("near-chain-configs", 130),
-    ("near-chain-primitives", 130),
+    ("near-primitives", 130),
+    ("near-jsonrpc-primitives", 137),
+    ("near-chain-configs", 131),
+    ("near-chain-primitives", 131),
     ("near-client-primitives", 152),
-    ("near-parameters", 67),
+    ("near-parameters", 68),
     ("near-crypto", 75),
     ("near-primitives-core", 60),
     ("near-time", 30),
```
