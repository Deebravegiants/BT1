# [?] bump rustls-webpki to 0.103.13 to clear RUSTSEC-2026-0098/0099/0104

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-05-18
Source: https://github.com/Conflux-Chain/conflux-rust/commit/151ec5a47e717f3e09678f8fe2944a166d7db7ba
Type: security-commit

## Details
bump rustls-webpki to 0.103.13 to clear RUSTSEC-2026-0098/0099/0104

Three new advisories against rustls-webpki 0.103.10 (URI name
constraint, wildcard name constraint, CRL panic) are fixed in
0.103.12+. Master already runs 0.103.13; this aligns the PR lock.

The tracy-client-sys -> windows-targets re-resolve to 0.48.5 is a
benign collateral that matches master.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

## Patch
### Cargo.lock
```diff
@@ -8104,9 +8104,9 @@ checksum = "f87165f0995f63a9fbeea62b64d10b4d9d8e78ec6d7d51fb2125fda7bb36788f"
 
 [[package]]
 name = "rustls-webpki"
-version = "0.103.10"
+version = "0.103.13"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "df33b2b81ac578cabaf06b89b0631153a3f416b0a886e8a7a1707fb51abbd1ef"
+checksum = "61c429a8649f110dddef65e2a5ad240f747e85f7758a6bccc7e5777bd33f756e"
 dependencies = [
  "ring",
  "rustls-pki-types",
@@ -9619,7 +9619,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "319c70195101a93f56db4c74733e272d720768e13471f400c78406a326b172b0"
 dependencies = [
  "cc",
- "windows-targets 0.52.6",
+ "windows-targets 0.48.5",
 ]
 
 [[package]]
```

### tools/evm-spec-tester/Cargo.lock
```diff
@@ -6762,9 +6762,9 @@ checksum = "f87165f0995f63a9fbeea62b64d10b4d9d8e78ec6d7d51fb2125fda7bb36788f"
 
 [[package]]
 name = "rustls-webpki"
-version = "0.103.10"
+version = "0.103.13"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "df33b2b81ac578cabaf06b89b0631153a3f416b0a886e8a7a1707fb51abbd1ef"
+checksum = "61c429a8649f110dddef65e2a5ad240f747e85f7758a6bccc7e5777bd33f756e"
 dependencies = [
  "ring",
  "rustls-pki-types",
```
