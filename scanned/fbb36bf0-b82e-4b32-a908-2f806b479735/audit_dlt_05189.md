# [?] security: bump rustls-webpki to 0.103.13 (RUSTSEC-2026-0104)

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-04-22
Source: https://github.com/Conflux-Chain/conflux-rust/commit/246c23edb05a53e294d80d6d4d472954d1d9478e
Type: security-commit

## Details
security: bump rustls-webpki to 0.103.13 (RUSTSEC-2026-0104)

Reachable panic in CRL parsing via BorrowedCertRevocationList::from_der
(mishandled empty BIT STRING in onlySomeReasons of IssuingDistributionPoint).
We do not configure CRL verification, so the vulnerable path is not reached;
bump to the SemVer-compatible patch release to clear the advisory.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

## Patch
### Cargo.lock
```diff
@@ -8191,9 +8191,9 @@ checksum = "f87165f0995f63a9fbeea62b64d10b4d9d8e78ec6d7d51fb2125fda7bb36788f"
 
 [[package]]
 name = "rustls-webpki"
-version = "0.103.12"
+version = "0.103.13"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8279bb85272c9f10811ae6a6c547ff594d6a7f3c6c6b02ee9726d1d0dcfcdd06"
+checksum = "61c429a8649f110dddef65e2a5ad240f747e85f7758a6bccc7e5777bd33f756e"
 dependencies = [
  "ring",
  "rustls-pki-types",
```

### tools/evm-spec-tester/Cargo.lock
```diff
@@ -6887,9 +6887,9 @@ checksum = "f87165f0995f63a9fbeea62b64d10b4d9d8e78ec6d7d51fb2125fda7bb36788f"
 
 [[package]]
 name = "rustls-webpki"
-version = "0.103.12"
+version = "0.103.13"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8279bb85272c9f10811ae6a6c547ff594d6a7f3c6c6b02ee9726d1d0dcfcdd06"
+checksum = "61c429a8649f110dddef65e2a5ad240f747e85f7758a6bccc7e5777bd33f756e"
 dependencies = [
  "ring",
  "rustls-pki-types",
```
