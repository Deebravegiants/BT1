# [?] fix: RUSTSEC-2024-0006 (#4439)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2024-01-22
Source: https://github.com/chainflip-io/chainflip-backend/commit/ccf5c70a56e4c46b3921fa743664a3093b7ed5f1
Type: security-commit

## Details
fix: RUSTSEC-2024-0006 (#4439)

## Patch
### Cargo.lock
```diff
@@ -11018,9 +11018,9 @@ dependencies = [
 
 [[package]]
 name = "shlex"
-version = "1.2.0"
+version = "1.3.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a7cee0529a6d40f580e7a5e6c495c8fbfe21b7b52795ed4bb5e62cdf92bc6380"
+checksum = "0fda2ff0d084019ba4d7c6f371c95d8fd75ce3524c3cb8fb653a3023f6323e64"
 
 [[package]]
 name = "signal-hook-registry"
```
