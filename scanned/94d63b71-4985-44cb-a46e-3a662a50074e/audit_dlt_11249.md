# [?] fix: update rustls-webpki to 0.103.10 (RUSTSEC-2026-0049) (#11942)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-03-23
Source: https://github.com/noir-lang/noir/commit/66086a0e9aa2fb16850b0b1ccb4bc06e40e5ec0c
Type: security-commit

## Details
fix: update rustls-webpki to 0.103.10 (RUSTSEC-2026-0049) (#11942)

## Patch
### Cargo.lock
```diff
@@ -5149,9 +5149,9 @@ checksum = "f87165f0995f63a9fbeea62b64d10b4d9d8e78ec6d7d51fb2125fda7bb36788f"
 
 [[package]]
 name = "rustls-webpki"
-version = "0.103.9"
+version = "0.103.10"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d7df23109aa6c1567d1c575b9952556388da57401e4ace1d15f79eedad0d8f53"
+checksum = "df33b2b81ac578cabaf06b89b0631153a3f416b0a886e8a7a1707fb51abbd1ef"
 dependencies = [
  "ring",
  "rustls-pki-types",
```
