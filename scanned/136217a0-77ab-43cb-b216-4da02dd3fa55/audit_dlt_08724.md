# [?] deps: bump h2 to 0.4.16 to fix RUSTSEC-2026-0258 (#22462)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2026-08-18
Source: https://github.com/ethereum-optimism/optimism/commit/c38228bf4061f7918439312781713b535c3bc556
Type: security-commit

## Details
deps: bump h2 to 0.4.16 to fix RUSTSEC-2026-0258 (#22462)

Co-authored-by: Claude <noreply@anthropic.com>

## Patch
### rust/Cargo.lock
```diff
@@ -5457,9 +5457,9 @@ dependencies = [
 
 [[package]]
 name = "h2"
-version = "0.4.13"
+version = "0.4.16"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "2f44da3a8150a6703ed5d34e164b875fd14c2cdab9af1252a9a1020bde2bdc54"
+checksum = "a9f37a958b41b3b19ee2707c06439c0e9e547e847223eb791ecb0cb821c65e27"
 dependencies = [
  "atomic-waker",
  "bytes",
```
