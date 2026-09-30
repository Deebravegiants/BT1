# [?] fix cargo deny issue RUSTSEC-2026-0099

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-04-16
Source: https://github.com/Conflux-Chain/conflux-rust/commit/fc919a60c494d5de64b0d1bc1b34c2b48cb17ae1
Type: security-commit

## Details
fix cargo deny issue RUSTSEC-2026-0099

## Patch
### Cargo.lock
```diff
@@ -8242,9 +8242,9 @@ checksum = "f87165f0995f63a9fbeea62b64d10b4d9d8e78ec6d7d51fb2125fda7bb36788f"
 
 [[package]]
 name = "rustls-webpki"
-version = "0.103.10"
+version = "0.103.12"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "df33b2b81ac578cabaf06b89b0631153a3f416b0a886e8a7a1707fb51abbd1ef"
+checksum = "8279bb85272c9f10811ae6a6c547ff594d6a7f3c6c6b02ee9726d1d0dcfcdd06"
 dependencies = [
  "ring",
  "rustls-pki-types",
@@ -9819,7 +9819,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
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
@@ -6927,9 +6927,9 @@ checksum = "f87165f0995f63a9fbeea62b64d10b4d9d8e78ec6d7d51fb2125fda7bb36788f"
 
 [[package]]
 name = "rustls-webpki"
-version = "0.103.10"
+version = "0.103.12"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "df33b2b81ac578cabaf06b89b0631153a3f416b0a886e8a7a1707fb51abbd1ef"
+checksum = "8279bb85272c9f10811ae6a6c547ff594d6a7f3c6c6b02ee9726d1d0dcfcdd06"
 dependencies = [
  "ring",
  "rustls-pki-types",
```
