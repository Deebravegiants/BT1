# [?] fix(deps): remediate cargo audit vulnerabilities (#3328)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/fuel-core
Published: 2026-09-05
Source: https://github.com/FuelLabs/fuel-core/commit/add100d30d21498e8528c46be8567fbd2ea019af
Type: security-commit

## Details
fix(deps): remediate cargo audit vulnerabilities (#3328)

## Summary
- update the vulnerable dependency graph so `cargo audit` has no
unignored vulnerabilities
- migrate affected integrations to current Axum/Hyper, AWS SDK, libp2p,
Wasmtime, EventSource, and shared-sequencer APIs
- bump the pinned Rust toolchain to 1.94.1, the minimum supported by the
upgraded Wasmtime graph
- retain only two narrowly documented audit exceptions for
`hickory-proto` 0.25 through `libp2p-dns` 0.44: one advisory has no
fixed release, and the other requires hickory 0.26 while current libp2p
still pins 0.25

## Compatibility checks
- Axum HTTP server lifecycle, graceful shutdown, timeout status, and
relayer mock server exercised
- GraphQL SSE subscriptions exercised with the new LaunchDarkly
transport abstraction and a pooled Reqwest client
- libp2p 0.56 API migrations covered by the P2P all-features suite,
including DNS resolution and discovery
- AWS S3 remote-cache behavior covered by its full unit suite
- shared-sequencer Tendermint JSON-RPC requests covered with wire-level
mock tests
- Wasmtime 46 executor paths covered by the upgradable-executor suite

## Verification
- `cargo audit --no-fetch`
- `RUSTFLAGS='-D warnings' cargo clippy --all-targets --all-features`
- `cargo nextest run --workspace` (1810 passed)
- `cargo nextest run --all-features --workspace` (1433 passed)
- `cargo +nightly-2025-09-28 fmt --all -- --check`
- `cargo sort -w --check`

## Patch
### .cargo/audit.toml
```diff
@@ -1,11 +1,5 @@
 [advisories]
 ignore = [
-    "RUSTSEC-2025-0009", # https://github.com/FuelLabs/fuel-core/issues/2814
-    "RUSTSEC-2026-0098", # https://github.com/FuelLabs/fuel-core/issues/3265
-    "RUSTSEC-2026-0099", # https://github.com/FuelLabs/fuel-core/issues/3265
-    "RUSTSEC-2026-0104", # https://github.com/FuelLabs/fuel-core/issues/3279
-    "RUSTSEC-2026-0114", # https://github.com/FuelLabs/fuel-core/issues/3293
-    "RUSTSEC-2026-0119", # https://github.com/FuelLabs/fuel-core/issues/3296
-    "RUSTSEC-2026-0222", # https://rustsec.org/advisories/RUSTSEC-2026-0222 — wasmtime 43.x has no patched release in its line; fix requires a major-version bump (>=46.0.2 or >=47.0.3), out of scope here
-    "RUSTSEC-2026-0258", # https://rustsec.org/advisories/RUSTSEC-2026-0258 — h2 unbounded empty DATA frames; 0.4 line patched at >=0.4.16, but hyper 0.14 / reqwest 0.11 / tonic 0.11 still pin h2 0.3.27 with no 0.3 patch
+    "RUSTSEC-2026-0118", # hickory-proto 0.25 via libp2p-dns 0.43; advisory has no fixed release
+    "RUSTSEC-2026-0119", # https://github.com/FuelLabs/fuel-core/issues/3296 — libp2p-dns 0.43 pins hickory-proto 0.25
 ]
```

### .changes/changed/3328.md
```diff
@@ -0,0 +1 @@
+Updated vulnerable dependencies and the Rust toolchain to current patched versions.
```

### .github/workflows/ci.yml
```diff
@@ -22,7 +22,7 @@ env:
   AWS_ROLE_ARN: arn:aws:iam::024848458133:role/github_oidc_FuelLabs_fuel-core
   AWS_ECR_ORG: fuellabs
   CARGO_TERM_COLOR: always
-  RUST_VERSION: 1.93.0
+  RUST_VERSION: 1.94.1
   RUST_VERSION_FMT: nightly-2025-09-28
   RUST_VERSION_COV: nightly-2025-09-28
   RUSTFLAGS: -D warnings
@@ -131,7 +131,7 @@ jobs:
           # for `fuel-core 0.26.0`(because of the bug with `--offline`
           # and `--locked` when we build `fuel-core-wasm-executor 0.26.0`).
           - command: check
-            args: --manifest-path version-compatibility/Cargo.toml --workspace && cargo test --manifest-path version-compatibility/Cargo.toml --workspace
+            args: --manifest-path version-compatibility/Cargo.toml --workspace --locked && cargo test --manifest-path version-compatibility/Cargo.toml --workspace --locked
           - command: build
             args: -p fuel-core-bin --no-default-features --features production
 
```

### .github/workflows/dependencies.yml
```diff
@@ -16,7 +16,7 @@ defaults:
 env:
   # So cargo doesn't complain about unstable features
   RUSTC_BOOTSTRAP: 1
-  RUST_VERSION: 1.93.0
+  RUST_VERSION: 1.94.1
   PR_TITLE: Weekly `cargo update`
   PR_MESSAGE: |
     Automation to keep dependencies in `Cargo.lock` current.
```

### .github/workflows/docker-images.yml
```diff
@@ -16,7 +16,7 @@ env:
   AWS_ROLE_ARN: arn:aws:iam::024848458133:role/github_oidc_FuelLabs_fuel-core
   AWS_ECR_ORG: fuellabs
   CARGO_TERM_COLOR: always
-  RUST_VERSION: 1.93.0
+  RUST_VERSION: 1.94.1
   RUST_VERSION_FMT: nightly-2023-10-29
   RUST_VERSION_COV: nightly-2024-06-05
   RUSTFLAGS: -D warnings
```

### .github/workflows/publish-codecov.yml
```diff
@@ -11,7 +11,7 @@ env:
   AWS_ROLE_ARN: arn:aws:iam::024848458133:role/github_oidc_FuelLabs_fuel-core
   AWS_ECR_ORG: fuellabs
   CARGO_TERM_COLOR: always
-  RUST_VERSION: 1.93.0
+  RUST_VERSION: 1.94.1
   RUST_VERSION_FMT: nightly-2023-10-29
   RUST_VERSION_COV: nightly-2024-06-05
   RUSTFLAGS: -D warnings
```

### AGENTS.md
```diff
@@ -22,7 +22,7 @@ Keep `RUST_VERSION_FMT` in sync with `.github/workflows/ci.yml` (`env.RUST_VERSI
 
 ### Hard rules
 
-- **Never** run `cargo fmt` / `cargo fmt --all` on the **stable / 1.93.0** toolchain from `rust-toolchain.toml`. `.rustfmt.toml` uses nightly-only options (`imports_layout`, `imports_granularity`, `normalize_comments`, `trailing_semicolon`). Stable ignores them and can rewrite hundreds of files with compact import layout.
+- **Never** run `cargo fmt` / `cargo fmt --all` on the **stable / 1.94.1** toolchain from `rust-toolchain.toml`. `.rustfmt.toml` uses nightly-only options (`imports_layout`, `imports_granularity`, `normalize_comments`, `trailing_semicolon`). Stable ignores them and can rewrite hundreds of files with compact import layout.
 - Prefer formatting the whole workspace with the CI nightly (`cargo +nightly-2025-09-28 fmt --all`) so the PR matches CI. If you must format a subset, still use that nightly + this repo's `.rustfmt.toml`.
 - Also run `cargo clippy` (stable pin) with `-D warnings` on touched crates when practical; CI enforces warnings as errors.
 
```

### Cargo.toml
```diff
@@ -54,7 +54,7 @@ homepage = "https://fuel.network/"
 keywords = ["blockchain", "cryptocurrencies", "fuel-vm", "vm"]
 license = "BUSL-1.1"
 repository = "https://github.com/FuelLabs/fuel-core"
-rust-version = "1.93.0"
+rust-version = "1.94.1"
 version = "0.48.3"
 
 [workspace.dependencies]
@@ -75,11 +75,10 @@ async-graphql-value = { version = "7.0.15" }
 async-trait = "0.1"
 
 # Fuel dependencies
-aws-config = { version = "1.8.11", features = ["behavior-version-latest"] }
-aws-sdk-kms = "1.96.0"
-aws-sdk-s3 = "1.119.0"
-aws-smithy-mocks = "0.2.0"
-axum = "0.5"
+aws-config = { version = "1.11.0", features = ["behavior-version-latest"] }
+aws-sdk-kms = { version = "1.116.0", default-features = false, features = ["default-https-client", "rt-tokio"] }
+aws-sdk-s3 = { version = "1.143.0", default-features = false, features = ["default-https-client", "http-1x", "rt-tokio", "sigv4a"] }
+axum = "0.8"
 bytes = "1.5.0"
 clap = "4.4"
 cynic = { version = "=3.12.0", features = ["http-reqwest"] }
@@ -127,7 +126,7 @@ fuel-gas-price-algorithm = { version = "0.48.3", path = "crates/fuel-gas-price-a
 fuel-vm-private = { version = "0.66.4", package = "fuel-vm", default-features = false }
 futures = "0.3"
 hex = { version = "0.4", features = ["serde"] }
-hyper = { version = "0.14" }
+hyper = { version = "1.7", features = ["http1", "http2", "server"] }
 impl-tools = "0.11"
 indicatif = { version = "0.18", default-features = false }
 insta = "1.8"
@@ -143,7 +142,7 @@ pin-project-lite = "0.2"
 postcard = "1.0"
 pretty_assertions = "1.4.0"
 primitive-types = { version = "0.12", default-features = false }
-prometheus-client = "0.22.0"
+prometheus-client = "0.22.3"
 proptest = "1.1"
 prost = "0.14.1"
 rand = "0.8"
```

### ci_checks.sh
```diff
@@ -6,7 +6,7 @@
 # The script runs almost all CI checks locally.
 #
 # Requires installed:
-# - Rust `1.93.0`
+# - Rust `1.94.1`
 # - Nightly rust formatter
 # - `cargo install cargo-sort`
 # - `cargo install cargo-make`
```

### crates/client/Cargo.toml
```diff
@@ -26,10 +26,10 @@ rpc = [
 test-helpers = []
 subscriptions = [
     "base64",
+    "bytes",
     "eventsource-client",
     "futures",
-    "hyper",
-    "hyper-rustls",
+    "launchdarkly-sdk-transport",
     "dep:postcard",
     "fuel-core-types/serde",
 ]
@@ -40,21 +40,20 @@ anyhow = { workspace = true }
 aws-config = { workspace = true, optional = true }
 aws-sdk-s3 = { workspace = true, optional = true }
 base64 = { version = "0.22.1", optional = true }
+bytes = { workspace = true, optional = true }
 cynic = { workspace = true }
 derive_more = { workspace = true }
-eventsource-client = { version = "0.13.0", optional = true }
+eventsource-client = { version = "0.17.0", default-features = false, optional = true }
 flate2 = { workspace = true, optional = true }
 fuel-core-block-aggregator-api = { workspace = true, optional = true }
 fuel-core-types = { workspace = true, features = ["alloc", "serde"] }
 futures = { workspace = true, optional = true }
 hex = { workspace = true }
-# Included to enable webpki in the eventsource client
-hyper = { version = "0.14", features = ["client", "http1", "tcp"], optional = true }
-hyper-rustls = { version = "0.24", features = ["webpki-tokio"], optional = true }
 itertools = { workspace = true }
+launchdarkly-sdk-transport = { version = "0.1.4", default-features = false, optional = true }
 postcard = { workspace = true, optional = true }
 prost = { workspace = true, optional = true }
-reqwest = { workspace = true }
+reqwest = { workspace = true, features = ["stream"] }
 serde = { workspace = true, features = ["derive"] }
 serde_json = { version = "1.0", features = ["raw_value"] }
 # We force the version because 4.1.0 update leap seconds that breaks our timestamps
@@ -71,3 +70,5 @@ serde_json = { version = "1.0", features = ["raw_value"] }
 [dev-dependencies]
 fuel-core-types = { workspace = true, features = ["serde", "std", "test-helpers"] }
 insta = { workspace = true }
+mockito = "1.6.1"
+tokio = { workspace = true, features = ["macros", "rt"] }
```

### crates/client/src/lib.rs
```diff
@@ -2,6 +2,11 @@
 #![deny(clippy::cast_possible_truncation)]
 #![deny(unused_crate_dependencies)]
 #![deny(warnings)]
+#[cfg(all(test, not(feature = "subscriptions")))]
+use {
+    mockito as _,
+    tokio as _,
+};
 pub mod client;
 pub mod reqwest_ext;
 pub mod schema;
```
