# [?] deps: bump rustls to 0.23.45 (RUSTSEC-2026-0285) (#15239)

## Summary
Severity: Unknown
Chain: Solana
Component: anza-xyz/agave
Published: 2026-09-14
Source: https://github.com/anza-xyz/agave/commit/7fea95b69167d42480566de3b812ef92c8402eb0
Type: security-commit

## Details
deps: bump rustls to 0.23.45 (RUSTSEC-2026-0285) (#15239)

Problem

rustls 0.23.43 accepts TLS 1.3 handshake messages sent at the wrong
encryption level when they follow a key-changing message in the same
record - e.g. a plaintext EncryptedExtensions packed behind ServerHello.
RFC 8446 5.1 says terminate with unexpected_message instead.

* transcript stays authenticated, so no handshake tampering
* practical effect - peer sends in plaintext what must be encrypted
* medium, 5.3, confidentiality only
* https://rustsec.org/advisories/RUSTSEC-2026-0285

Summary of Changes

* bump workspace rustls pin to 0.23.45
* refresh the rustls entry in all four audited lock files

## Patch
### Cargo.lock
```diff
@@ -6132,9 +6132,9 @@ dependencies = [
 
 [[package]]
 name = "rustls"
-version = "0.23.43"
+version = "0.23.45"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0283386ce02abc0151e1761d08802dfe86c173b0b494af5cbc086574e453da06"
+checksum = "0d41d731c7d2f962d1ccc364cec258de3c0e93b38c2fb3ba97ac74513048d634"
 dependencies = [
  "log",
  "once_cell",
```

### Cargo.toml
```diff
@@ -313,7 +313,7 @@ rolling-file = "0.2.0"
 rpassword = "7.5"
 rts-alloc = { version = "5.1.0" }
 rusb = "0.9"
-rustls = { version = "0.23.43", features = ["std"], default-features = false }
+rustls = { version = "0.23.45", features = ["std"], default-features = false }
 rustls-webpki = { version = "0.103.15", default-features = false, features = ["std"] }
 scopeguard = "1.2.0"
 semver = "1.0.28"
```

### ci/xtask/Cargo.lock
```diff
@@ -1758,9 +1758,9 @@ dependencies = [
 
 [[package]]
 name = "rustls"
-version = "0.23.43"
+version = "0.23.45"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0283386ce02abc0151e1761d08802dfe86c173b0b494af5cbc086574e453da06"
+checksum = "0d41d731c7d2f962d1ccc364cec258de3c0e93b38c2fb3ba97ac74513048d634"
 dependencies = [
  "log",
  "once_cell",
```

### dev-bins/Cargo.lock
```diff
@@ -5078,9 +5078,9 @@ dependencies = [
 
 [[package]]
 name = "rustls"
-version = "0.23.43"
+version = "0.23.45"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0283386ce02abc0151e1761d08802dfe86c173b0b494af5cbc086574e453da06"
+checksum = "0d41d731c7d2f962d1ccc364cec258de3c0e93b38c2fb3ba97ac74513048d634"
 dependencies = [
  "log",
  "once_cell",
```

### programs/sbf/Cargo.lock
```diff
@@ -5044,9 +5044,9 @@ dependencies = [
 
 [[package]]
 name = "rustls"
-version = "0.23.43"
+version = "0.23.45"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0283386ce02abc0151e1761d08802dfe86c173b0b494af5cbc086574e453da06"
+checksum = "0d41d731c7d2f962d1ccc364cec258de3c0e93b38c2fb3ba97ac74513048d634"
 dependencies = [
  "log",
  "once_cell",
```
