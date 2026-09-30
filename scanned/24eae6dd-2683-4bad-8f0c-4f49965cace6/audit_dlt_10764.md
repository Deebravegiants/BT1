# [?] Upgrade shlex from 1.2.0 to 1.3.0, fix RUSTSEC-2024-0006

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2024-01-23
Source: https://github.com/nervosnetwork/ckb/commit/20533ea22bd40d27bf4846ee656b4e535380c919
Type: security-commit

## Details
Upgrade shlex from 1.2.0 to 1.3.0, fix RUSTSEC-2024-0006

## Patch
### Cargo.lock
```diff
@@ -4317,9 +4317,9 @@ dependencies = [
 
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
