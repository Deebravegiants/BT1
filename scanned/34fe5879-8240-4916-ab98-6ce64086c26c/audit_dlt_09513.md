# [?] fix: RUSTSEC-2024-0019 (#4604)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2024-03-05
Source: https://github.com/chainflip-io/chainflip-backend/commit/be69d97f57ddc5bf3ee9dcc4fa0358a7028a1ec8
Type: security-commit

## Details
fix: RUSTSEC-2024-0019 (#4604)

## Patch
### Cargo.lock
```diff
@@ -6578,9 +6578,9 @@ dependencies = [
 
 [[package]]
 name = "mio"
-version = "0.8.10"
+version = "0.8.11"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "8f3d0b296e374a4e6f3c7b0a1f5a51d748a0d34c85e7dc48fc3fa9a87657fe09"
+checksum = "a4a650543ca06a924e8b371db273b2756685faae30f8487da1b56505a8f78b0c"
 dependencies = [
  "libc",
  "wasi 0.11.0+wasi-snapshot-preview1",
```
