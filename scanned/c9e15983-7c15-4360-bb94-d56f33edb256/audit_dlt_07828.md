# [?] Resolve RUSTSEC-2020-0146 (#2242)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2021-03-04
Source: https://github.com/sigp/lighthouse/commit/c37010071957dc1bbd7634d215bba29254688990
Type: security-commit

## Details
Resolve RUSTSEC-2020-0146 (#2242)

## Issue Addressed

Closes #2237

## Proposed Changes

Bump `generic-array` to patched version `0.12.4`

## Patch
### .github/workflows/test-suite.yml
```diff
@@ -11,6 +11,8 @@ on:
 env:
   # Deny warnings in CI
   RUSTFLAGS: "-D warnings"
+  # The Nightly version used for cargo-udeps, might need updating from time to time.
+  PINNED_NIGHTLY: nightly-2021-03-01
 jobs:
   target-branch-check:
     name: target-branch-check
@@ -178,8 +180,8 @@ jobs:
     needs: cargo-fmt
     steps:
     - uses: actions/checkout@v1
-    - name: Install a nightly compiler with rustfmt, as a kind of quality control
-      run: rustup toolchain install --component=rustfmt nightly
+    - name: Install Rust (${{ env.PINNED_NIGHTLY }})
+      run: rustup toolchain install $PINNED_NIGHTLY
     - name: Install cargo-udeps
       run: cargo install cargo-udeps --locked
     - name: Run cargo udeps to identify unused crates in the dependency graph
```

### Cargo.lock
```diff
@@ -757,7 +757,7 @@ dependencies = [
  "block-padding 0.1.5",
  "byte-tools",
  "byteorder",
- "generic-array 0.12.3",
+ "generic-array 0.12.4",
 ]
 
 [[package]]
@@ -1324,7 +1324,7 @@ version = "0.7.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "4434400df11d95d556bac068ddfedd482915eb18fe8bea89bc80b6e4b1c179e5"
 dependencies = [
- "generic-array 0.12.3",
+ "generic-array 0.12.4",
  "subtle 1.0.0",
 ]
 
@@ -1549,7 +1549,7 @@ version = "0.8.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "f3d0c8c8752312f9713efd397ff63acb9f85585afbf179282e720e7704954dd5"
 dependencies = [
- "generic-array 0.12.3",
+ "generic-array 0.12.4",
 ]
 
 [[package]]
@@ -2501,9 +2501,9 @@ dependencies = [
 
 [[package]]
 name = "generic-array"
-version = "0.12.3"
+version = "0.12.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "c68f0274ae0e023facc3c97b2e00f076be70e254bc851d972503b328db79b2ec"
+checksum = "ffdf9f34f1447443d37393cc6c2b8313aebddcd96906caf34e54c68d8e57d7bd"
 dependencies = [
  "typenum",
 ]
@@ -2807,7 +2807,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "c6e570451493f10f6581b48cdd530413b63ea9e780f544bfd3bdcaa0d89d1a7b"
 dependencies = [
  "digest 0.8.1",
- "generic-array 0.12.3",
+ "generic-array 0.12.4",
  "hmac 0.7.1",
 ]
 
```

### Makefile
```diff
@@ -10,6 +10,8 @@ BUILD_PATH_X86_64 = "target/$(X86_64_TAG)/release"
 AARCH64_TAG = "aarch64-unknown-linux-gnu"
 BUILD_PATH_AARCH64 = "target/$(AARCH64_TAG)/release"
 
+PINNED_NIGHTLY ?= nightly
+
 # Builds the Lighthouse binary in release (optimized).
 #
 # Binaries will most likely be found in `./target/release`
@@ -136,11 +138,11 @@ arbitrary-fuzz:
 # Runs cargo audit (Audit Cargo.lock files for crates with security vulnerabilities reported to the RustSec Advisory Database)
 audit:
 	cargo install --force cargo-audit
-	cargo audit --ignore RUSTSEC-2020-0146
+	cargo audit
 
 # Runs `cargo udeps` to check for unused dependencies
 udeps:
-	cargo +nightly udeps --tests --all-targets --release
+	cargo +$(PINNED_NIGHTLY) udeps --tests --all-targets --release
 
 # Performs a `cargo` clean and cleans the `ef_tests` directory.
 clean:
```
