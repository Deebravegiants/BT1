# [?] Update rustls to address RUSTSEC-2026-0285 (#179)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-program/token
Published: 2026-09-18
Source: https://github.com/solana-program/token/commit/408c9c1c5bb10a99c7e230a53e70ab1295385870
Type: security-commit

## Details
Update rustls to address RUSTSEC-2026-0285 (#179)

This PR bumps the locked `rustls` from 0.23.37 to 0.23.45 (along with the `rustls-webpki` 0.103.15 it requires) to clear RUSTSEC-2026-0285, in which TLS 1.3 handshake messages were accepted across encryption level boundaries. The crate only reaches the workspace through the Rust client's optional `fetch` feature via `solana-rpc-client` and `reqwest`, so this is a lockfile-only change with no manifest edits.

## Patch
### Cargo.lock
```diff
@@ -4272,9 +4272,9 @@ dependencies = [
 
 [[package]]
 name = "rustls"
-version = "0.23.37"
+version = "0.23.45"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "758025cb5fccfd3bc2fd74708fd4682be41d99e5dff73c377c0646c6012c73a4"
+checksum = "0d41d731c7d2f962d1ccc364cec258de3c0e93b38c2fb3ba97ac74513048d634"
 dependencies = [
  "once_cell",
  "ring",
@@ -4335,9 +4335,9 @@ checksum = "f87165f0995f63a9fbeea62b64d10b4d9d8e78ec6d7d51fb2125fda7bb36788f"
 
 [[package]]
 name = "rustls-webpki"
-version = "0.103.13"
+version = "0.103.15"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "61c429a8649f110dddef65e2a5ad240f747e85f7758a6bccc7e5777bd33f756e"
+checksum = "f3c3cf1d8b1e7d4927e2d154c3fcb02979afb9939629c62cd9048d4f07b60ac2"
 dependencies = [
  "ring",
  "rustls-pki-types",
```
