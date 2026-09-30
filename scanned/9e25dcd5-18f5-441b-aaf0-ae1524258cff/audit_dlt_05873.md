# [?] chore: Fix SQLX vulnerability (#2736)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2024-08-26
Source: https://github.com/matter-labs/zksync-era/commit/d8e43e77ed9bf91dde1cacdb1698afd366bb3c1a
Type: security-commit

## Details
chore: Fix SQLX vulnerability (#2736)

SQLX 0.8.0 had a vulnerability, which didn't affect us. At the time of
discovery, there was no fix. We silenced the warning to unlock
development.

This PR bumps SQLX to 0.8.1 which includes the vulnerability fix and
removes the cargo deny allowlist.

Co-authored-by: perekopskiy <53865202+perekopskiy@users.noreply.github.com>

## Patch
### Cargo.lock
```diff
@@ -889,12 +889,13 @@ checksum = "37b2a672a2cb129a2e41c10b1224bb368f9f37a2b16b612598138befd7b37eb5"
 
 [[package]]
 name = "cc"
-version = "1.0.83"
+version = "1.1.14"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f1174fb0b6ec23863f8b971027804a42614e347eafb0a95bf0b12cdae21fc4d0"
+checksum = "50d2eb3cd3d1bf4529e31c215ee6f93ec5a3d536d9f578f93d9d33ee19562932"
 dependencies = [
  "jobserver",
  "libc",
+ "shlex",
 ]
 
 [[package]]
@@ -3184,9 +3185,9 @@ checksum = "8eaf4bc02d17cbdd7ff4c7438cafcdf7fb9a4613313ad11b4f8fefe7d3fa0130"
 
 [[package]]
 name = "jobserver"
-version = "0.1.27"
+version = "0.1.32"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8c37f63953c4c63420ed5fd3d6d398c719489b9f872b9fa683262f8edd363c7d"
+checksum = "48d1dbcbbeb6a7fec7e059840aa538bd62aaccf972c7346c4d9d2059312853d0"
 dependencies = [
  "libc",
 ]
@@ -3486,9 +3487,9 @@ dependencies = [
 
 [[package]]
 name = "libsqlite3-sys"
-version = "0.28.0"
+version = "0.30.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0c10584274047cb335c23d3e61bcef8e323adae7c5c8c760540f73610177fc3f"
+checksum = "2e99fb7a497b1e3339bc746195567ed8d3e24945ecd636e3619d20b9de9e9149"
 dependencies = [
  "cc",
  "pkg-config",
@@ -6073,9 +6074,9 @@ dependencies = [
 
 [[package]]
 name = "sqlx"
-version = "0.8.0"
+version = "0.8.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "27144619c6e5802f1380337a209d2ac1c431002dd74c6e60aebff3c506dc4f0c"
+checksum = "fcfa89bea9500db4a0d038513d7a060566bfc51d46d1c014847049a45cce85e8"
 dependencies = [
  "sqlx-core",
  "sqlx-macros",
@@ -6086,9 +6087,9 @@ dependencies = [
 
 [[package]]
 name = "sqlx-core"
-version = "0.8.0"
+version = "0.8.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a999083c1af5b5d6c071d34a708a19ba3e02106ad82ef7bbd69f5e48266b613b"
+checksum = "d06e2f2bd861719b1f3f0c7dbe1d80c30bf59e76cf019f07d9014ed7eefb8e08"
 dependencies = [
  "atoi",
  "bigdecimal",
@@ -6130,9 +6131,9 @@ dependencies = [
 
 [[package]]
 name = "sqlx-macros"
-version = "0.8.0"
+version = "0.8.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a23217eb7d86c584b8cbe0337b9eacf12ab76fe7673c513141ec42565698bb88"
+checksum = "2f998a9defdbd48ed005a89362bd40dd2117502f15294f61c8d47034107dbbdc"
 dependencies = [
  "proc-macro2 1.0.86",
  "quote 1.0.36",
@@ -6143,9 +6144,9 @@ dependencies = [
 
 [[package]]
 name = "sqlx-macros-core"
-version = "0.8.0"
+version = "0.8.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1a099220ae541c5db479c6424bdf1b200987934033c2584f79a0e1693601e776"
+checksum = "3d100558134176a2629d46cec0c8891ba0be8910f7896abfdb75ef4ab6f4e7ce"
 dependencies = [
  "dotenvy",
  "either",
@@ -6169,9 +6170,9 @@ dependencies = [
 
 [[package]]
 name = "sqlx-mysql"
-version = "0.8.0"
+version = "0.8.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5afe4c38a9b417b6a9a5eeffe7235d0a106716495536e7727d1c7f4b1ff3eba6"
+checksum = "936cac0ab331b14cb3921c62156d913e4c15b74fb6ec0f3146bd4ef6e4fb3c12"
 dependencies = [
  "atoi",
  "base64 0.22.1",
@@ -6214,9 +6215,9 @@ dependencies = [
 
 [[package]]
 name = "sqlx-postgres"
-version = "0.8.0"
+version = "0.8.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b1dbb157e65f10dbe01f729339c06d239120221c9ad9fa0ba8408c4cc18ecf21"
+checksum = "9734dbce698c67ecf67c442f768a5e90a49b2a4d61a9f1d59f73874bd4cf0710"
 dependencies = [
  "atoi",
  "base64 0.22.1",
@@ -6257,9 +6258,9 @@ dependencies = [
 
 [[package]]
 name = "sqlx-sqlite"
-version = "0.8.0"
+version = "0.8.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9b2cdd83c008a622d94499c0006d8ee5f821f36c89b7d625c900e5dc30b5c5ee"
+checksum = "a75b419c3c1b1697833dd927bdc4c6545a620bc1bbafabd44e1efbe9afcd337e"
 dependencies = [
  "atoi",
  "chrono",
```

### Cargo.toml
```diff
@@ -167,7 +167,7 @@ serde_with = "1"
 serde_yaml = "0.9"
 sha2 = "0.10.8"
 sha3 = "0.10.8"
-sqlx = "0.8.0"
+sqlx = "0.8.1"
 static_assertions = "1.1"
 structopt = "0.3.20"
 strum = "0.26"
```

### deny.toml
```diff
@@ -6,9 +6,7 @@ vulnerability = "deny"
 unmaintained = "warn"
 yanked = "warn"
 notice = "warn"
-ignore = [
-    "RUSTSEC-2024-0363", # allows sqlx@0.8.0 until fix is released, more here -- https://github.com/launchbadge/sqlx/issues/3440
-]
+ignore = []
 
 [licenses]
 unlicensed = "deny"
```

### docs/guides/setup-dev.md
```diff
@@ -43,7 +43,7 @@ yarn set version 1.22.19
 # For running unit tests
 cargo install cargo-nextest
 # SQL tools
-cargo install sqlx-cli --version 0.8.0
+cargo install sqlx-cli --version 0.8.1
 
 # Foundry
 curl -L https://foundry.paradigm.xyz | bash
@@ -217,7 +217,7 @@ SQLx is a Rust library we use to interact with Postgres, and its CLI is used to
 features of the library.
 
 ```bash
-cargo install --locked sqlx-cli --version 0.8.0
+cargo install --locked sqlx-cli --version 0.8.1
 ```
 
 ## Easier method using `nix`
```

### prover/Cargo.lock
```diff
@@ -839,13 +839,13 @@ dependencies = [
 
 [[package]]
 name = "cc"
-version = "1.0.98"
+version = "1.1.14"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "41c270e7540d725e65ac7f1b212ac8ce349719624d7bcff99f8e2e488e8cf03f"
+checksum = "50d2eb3cd3d1bf4529e31c215ee6f93ec5a3d536d9f578f93d9d33ee19562932"
 dependencies = [
  "jobserver",
  "libc",
- "once_cell",
+ "shlex",
 ]
 
 [[package]]
@@ -3276,9 +3276,9 @@ dependencies = [
 
 [[package]]
 name = "libsqlite3-sys"
-version = "0.28.0"
+version = "0.30.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0c10584274047cb335c23d3e61bcef8e323adae7c5c8c760540f73610177fc3f"
+checksum = "2e99fb7a497b1e3339bc746195567ed8d3e24945ecd636e3619d20b9de9e9149"
 dependencies = [
  "cc",
  "pkg-config",
@@ -5746,9 +5746,9 @@ dependencies = [
 
 [[package]]
 name = "sqlx"
-version = "0.8.0"
+version = "0.8.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "27144619c6e5802f1380337a209d2ac1c431002dd74c6e60aebff3c506dc4f0c"
+checksum = "fcfa89bea9500db4a0d038513d7a060566bfc51d46d1c014847049a45cce85e8"
 dependencies = [
  "sqlx-core",
  "sqlx-macros",
@@ -5759,9 +5759,9 @@ dependencies = [
 
 [[package]]
 name = "sqlx-core"
-version = "0.8.0"
+version = "0.8.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a999083c1af5b5d6c071d34a708a19ba3e02106ad82ef7bbd69f5e48266b613b"
+checksum = "d06e2f2bd861719b1f3f0c7dbe1d80c30bf59e76cf019f07d9014ed7eefb8e08"
 dependencies = [
  "atoi",
  "bigdecimal",
@@ -5803,9 +5803,9 @@ dependencies = [
 
 [[package]]
 name = "sqlx-macros"
-version = "0.8.0"
+version = "0.8.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a23217eb7d86c584b8cbe0337b9eacf12ab76fe7673c513141ec42565698bb88"
+checksum = "2f998a9defdbd48ed005a89362bd40dd2117502f15294f61c8d47034107dbbdc"
 dependencies = [
  "proc-macro2 1.0.85",
  "quote 1.0.36",
@@ -5816,9 +5816,9 @@ dependencies = [
 
 [[package]]
 name = "sqlx-macros-core"
-version = "0.8.0"
+version = "0.8.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1a099220ae541c5db479c6424bdf1b200987934033c2584f79a0e1693601e776"
+checksum = "3d100558134176a2629d46cec0c8891ba0be8910f7896abfdb75ef4ab6f4e7ce"
 dependencies = [
  "dotenvy",
  "either",
@@ -5842,9 +5842,9 @@ dependencies = [
 
 [[package]]
 name = "sqlx-mysql"
-version = "0.8.0"
+version = "0.8.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5afe4c38a9b417b6a9a5eeffe7235d0a106716495536e7727d1c7f4b1ff3eba6"
+checksum = "936cac0ab331b14cb3921c62156d913e4c15b74fb6ec0f3146bd4ef6e4fb3c12"
 dependencies = [
  "atoi",
  "base64 0.22.1",
@@ -5887,9 +5887,9 @@ dependencies = [
 
 [[package]]
 name = "sqlx-postgres"
-version = "0.8.0"
+version = "0.8.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b1dbb157e65f10dbe01f729339c06d239120221c9ad9fa0ba8408c4cc18ecf21"
+checksum = "9734dbce698c67ecf67c442f768a5e90a49b2a4d61a9f1d59f73874bd4cf0710"
 dependencies = [
  "atoi",
  "base64 0.22.1",
@@ -5930,9 +5930,9 @@ dependencies = [
 
 [[package]]
 name = "sqlx-sqlite"
-version = "0.8.0"
+version = "0.8.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9b2cdd83c008a622d94499c0006d8ee5f821f36c89b7d625c900e5dc30b5c5ee"
+checksum = "a75b419c3c1b1697833dd927bdc4c6545a620bc1bbafabd44e1efbe9afcd337e"
 dependencies = [
  "atoi",
  "chrono",
```

### prover/Cargo.toml
```diff
@@ -45,7 +45,7 @@ serde = "1.0"
 serde_derive = "1.0"
 serde_json = "1.0"
 sha3 = "0.10.8"
-sqlx = { version = "0.8.0", default-features = false }
+sqlx = { version = "0.8.1", default-features = false }
 structopt = "0.3.26"
 strum = { version = "0.26" }
 tempfile = "3"
```

### zk_toolbox/Cargo.lock
```diff
@@ -501,13 +501,13 @@ dependencies = [
 
 [[package]]
 name = "cc"
-version = "1.0.104"
+version = "1.1.14"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "74b6a57f98764a267ff415d50a25e6e166f3831a5071af4995296ea97d210490"
+checksum = "50d2eb3cd3d1bf4529e31c215ee6f93ec5a3d536d9f578f93d9d33ee19562932"
 dependencies = [
  "jobserver",
  "libc",
- "once_cell",
+ "shlex",
 ]
 
 [[package]]
@@ -2573,9 +2573,9 @@ dependencies = [
 
 [[package]]
 name = "libsqlite3-sys"
-version = "0.28.0"
+version = "0.30.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0c10584274047cb335c23d3e61bcef8e323adae7c5c8c760540f73610177fc3f"
+checksum = "2e99fb7a497b1e3339bc746195567ed8d3e24945ecd636e3619d20b9de9e9149"
 dependencies = [
  "cc",
  "pkg-config",
@@ -4564,6 +4564,12 @@ dependencies = [
  "lazy_static",
 ]
 
+[[package]]
+name = "shlex"
+version = "1.3.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "0fda2ff0d084019ba4d7c6f371c95d8fd75ce3524c3cb8fb653a3023f6323e64"
+
 [[package]]
 name = "signal-hook-registry"
 version = "1.4.2"
@@ -4716,9 +4722,9 @@ dependencies = [
 
 [[package]]
 name = "sqlx"
-version = "0.8.0"
+version = "0.8.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "27144619c6e5802f1380337a209d2ac1c431002dd74c6e60aebff3c506dc4f0c"
+checksum = "fcfa89bea9500db4a0d038513d7a060566bfc51d46d1c014847049a45cce85e8"
 dependencies = [
  "sqlx-core",
  "sqlx-macros",
@@ -4729,9 +4735,9 @@ dependencies = [
 
 [[package]]
 name = "sqlx-core"
-version = "0.8.0"
+version = "0.8.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a999083c1af5b5d6c071d34a708a19ba3e02106ad82ef7bbd69f5e48266b613b"
+checksum = "d06e2f2bd861719b1f3f0c7dbe1d80c30bf59e76cf019f07d9014ed7eefb8e08"
 dependencies = [
  "atoi",
  "byteorder",
@@ -4768,9 +4774,9 @@ dependencies = [
 
 [[package]]
 name = "sqlx-macros"
-version = "0.8.0"
+version = "0.8.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a23217eb7d86c584b8cbe0337b9eacf12ab76fe7673c513141ec42565698bb88"
+checksum = "2f998a9defdbd48ed005a89362bd40dd2117502f15294f61c8d47034107dbbdc"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -4781,9 +4787,9 @@ dependencies = [
 
 [[package]]
 name = "sqlx-macros-core"
-version = "0.8.0"
+version = "0.8.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "1a099220ae541c5db479c6424bdf1b200987934033c2584f79a0e1693601e776"
+checksum = "3d100558134176a2629d46cec0c8891ba0be8910f7896abfdb75ef4ab6f4e7ce"
 dependencies = [
  "dotenvy",
  "either",
@@ -4807,9 +4813,9 @@ dependencies = [
 
 [[package]]
 name = "sqlx-mysql"
-version = "0.8.0"
+version = "0.8.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5afe4c38a9b417b6a9a5eeffe7235d0a106716495536e7727d1c7f4b1ff3eba6"
+checksum = "936cac0ab331b14cb3921c62156d913e4c15b74fb6ec0f3146bd4ef6e4fb3c12"
 dependencies = [
  "atoi",
  "base64 0.22.1",
@@ -4849,9 +4855,9 @@ dependencies = [
 
 [[package]]
 name = "sqlx-postgres"
-version = "0.8.0"
+version = "0.8.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b1dbb157e65f10dbe01f729339c06d239120221c9ad9fa0ba8408c4cc18ecf21"
+checksum = "9734dbce698c67ecf67c442f768a5e90a49b2a4d61a9f1d59f73874bd4cf0710"
 dependencies = [
  "atoi",
  "base64 0.22.1",
@@ -4887,9 +4893,9 @@ dependencies = [
 
 [[package]]
 name = "sqlx-sqlite"
-version = "0.8.0"
+version = "0.8.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9b2cdd83c008a622d94499c0006d8ee5f821f36c89b7d625c900e5dc30b5c5ee"
+checksum = "a75b419c3c1b1697833dd927bdc4c6545a620bc1bbafabd44e1efbe9afcd337e"
 dependencies = [
  "atoi",
  "flume",
```

### zk_toolbox/Cargo.toml
```diff
@@ -47,7 +47,7 @@ rand = "0.8.5"
 serde = { version = "1.0", features = ["derive"] }
 serde_json = "1.0"
 serde_yaml = "0.9"
-sqlx = { version = "0.8.0", features = [
+sqlx = { version = "0.8.1", features = [
     "runtime-tokio",
     "migrate",
     "postgres",
```
