# [?] Merge pull request #4368 from eval-exec/exec/fix-RUSTSEC-2024-0019

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2024-03-05
Source: https://github.com/nervosnetwork/ckb/commit/7611ae7490e5a858d38e0f463c21580374d66078
Type: security-commit

## Details
Merge pull request #4368 from eval-exec/exec/fix-RUSTSEC-2024-0019

Fix RUSTSEC-2024-0019 #4367, upgrade mio from 0.8.9 to 0.8.11

## Patch
### Cargo.lock
```diff
@@ -3319,9 +3319,9 @@ dependencies = [
 
 [[package]]
 name = "mio"
-version = "0.8.9"
+version = "0.8.11"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "3dce281c5e46beae905d4de1870d8b1509a9142b62eedf18b443b011ca8343d0"
+checksum = "a4a650543ca06a924e8b371db273b2756685faae30f8487da1b56505a8f78b0c"
 dependencies = [
  "libc",
  "wasi 0.11.0+wasi-snapshot-preview1",
```
