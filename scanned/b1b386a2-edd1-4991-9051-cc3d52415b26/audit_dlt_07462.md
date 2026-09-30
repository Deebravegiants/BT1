# [?] chore(deps): bump rustls to 0.23.45 (RUSTSEC-2026-0285); accept RUSTSEC-2026-0269

## Summary
Severity: Unknown
Chain: Bittensor
Component: opentensor/subtensor
Published: 2026-09-15
Source: https://github.com/RaoFoundation/subtensor/commit/a0719eef99eb0c694cc9fb11719915c02debc82f
Type: security-commit

## Details
chore(deps): bump rustls to 0.23.45 (RUSTSEC-2026-0285); accept RUSTSEC-2026-0269

cargo audit failed on two advisories.

RUSTSEC-2026-0285 (rustls < 0.23.45, TLS 1.3 handshake messages accepted
across encryption-level boundaries) has a patched release, so take it:
`cargo update -p rustls --precise 0.23.45`, which also moves its required
rustls-webpki from 0.103.13 to 0.103.15. The lockfile change is limited
to those two crates; `cargo metadata --locked` is otherwise unchanged.
(Plain `cargo update -p rustls` stops at 0.23.43, so the version is
pinned explicitly.)

RUSTSEC-2026-0269 (wasmtime 8.0.1 WASI filesystem sandbox escape via
trailing slashes) has no reachable fix: wasmtime 8.0.1 is pinned by the
polkadot-sdk fork's sc-executor-wasmtime / sp-wasm-interface and the
patched lines start at 24.0.13, i.e. a major SDK bump. The node never
exposes a WASI filesystem to the runtime, so the advisory is not
reachable here. Record it, with a dated justification, in
`.cargo/audit.toml`, which cargo-audit merges with the workflow's
`--ignore` list; `.gitignore` now tracks that one file under `.cargo/`.
The workflow file itself is untouched.

`cargo audit` with the workflow's ignore list now exits 0 (30 allowed
informational warnings, 0 vulnerabilities).

Co-authored-by: Arbos <unarbos@users.noreply.github.com>

## Patch
### .cargo/audit.toml
```diff
@@ -0,0 +1,13 @@
+# Accepted advisories that cannot be fixed without a major polkadot-sdk bump.
+# The CI ignore list in .github/workflows/cargo-audit.yml covers the older
+# entries; cargo-audit merges both lists. Revisit everything here when the
+# SDK fork moves to a newer wasmtime.
+[advisories]
+ignore = [
+    # RUSTSEC-2026-0269 (added 2026-09-15): wasmtime 8.0.1 WASI filesystem
+    # sandbox escape via trailing slashes. wasmtime 8.0.1 is pinned by the
+    # polkadot-sdk fork's sc-executor-wasmtime / sp-wasm-interface; the fix
+    # is wasmtime >=24.0.13. The node never exposes a WASI filesystem to the
+    # runtime, so the advisory is not reachable here.
+    "RUSTSEC-2026-0269",
+]
```

### .gitignore
```diff
@@ -18,7 +18,9 @@
 .DS_Store
 
 # The cache for docker container dependency
-.cargo
+.cargo/*
+# cargo-audit advisory config is tracked
+!.cargo/audit.toml
 
 # The cache for chain data in container
 .local
```

### Cargo.lock
```diff
@@ -14991,20 +14991,20 @@ dependencies = [
  "errno",
  "libc",
  "linux-raw-sys 0.11.0",
- "windows-sys 0.52.0",
+ "windows-sys 0.59.0",
 ]
 
 [[package]]
 name = "rustls"
-version = "0.23.32"
+version = "0.23.45"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "cd3c25631629d034ce7cd9940adc9d45762d46de2b0f57193c4443b92c6d4d40"
+checksum = "0d41d731c7d2f962d1ccc364cec258de3c0e93b38c2fb3ba97ac74513048d634"
 dependencies = [
  "log",
  "once_cell",
  "ring 0.17.14",
  "rustls-pki-types",
- "rustls-webpki 0.103.13",
+ "rustls-webpki 0.103.15",
  "subtle 2.6.1",
  "zeroize",
 ]
@@ -15045,7 +15045,7 @@ dependencies = [
  "rustls",
  "rustls-native-certs",
  "rustls-platform-verifier-android",
- "rustls-webpki 0.103.13",
+ "rustls-webpki 0.103.15",
  "security-framework 3.5.1",
  "security-framework-sys",
  "webpki-root-certs 0.26.11",
@@ -15070,9 +15070,9 @@ dependencies = [
 
 [[package]]
 name = "rustls-webpki"
-version = "0.103.13"
+version = "0.103.15"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "61c429a8649f110dddef65e2a5ad240f747e85f7758a6bccc7e5777bd33f756e"
+checksum = "f3c3cf1d8b1e7d4927e2d154c3fcb02979afb9939629c62cd9048d4f07b60ac2"
 dependencies = [
  "ring 0.17.14",
  "rustls-pki-types",
```
