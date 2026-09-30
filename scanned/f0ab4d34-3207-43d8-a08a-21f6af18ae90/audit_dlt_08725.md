# [?] chore(rust): update thin-vec to patch RUSTSEC-2026-0103 (#20208)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2026-04-21
Source: https://github.com/ethereum-optimism/optimism/commit/6af6c02b77f022407b1b9a7c59ad53b80a757517
Type: security-commit

## Details
chore(rust): update thin-vec to patch RUSTSEC-2026-0103 (#20208)

Co-authored-by: wwared <541936+wwared@users.noreply.github.com>

## Patch
### rust/Cargo.lock
```diff
@@ -13924,9 +13924,9 @@ dependencies = [
 
 [[package]]
 name = "thin-vec"
-version = "0.2.14"
+version = "0.2.16"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "144f754d318415ac792f9d69fc87abbbfc043ce2ef041c60f16ad828f638717d"
+checksum = "259cdf8ed4e4aca6f1e9d011e10bd53f524a2d0637d7b28450f6c64ac298c4c6"
 
 [[package]]
 name = "thiserror"
```
