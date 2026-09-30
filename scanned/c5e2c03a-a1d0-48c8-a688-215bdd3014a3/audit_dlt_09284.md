# [?] chore: bump crossbeam-epoch for RUSTSEC-2026-0204 (#15614)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-07-07
Source: https://github.com/foundry-rs/foundry/commit/0b5a8c4d4e80590ac350b0bc6b78db80780e6abe
Type: security-commit

## Details
chore: bump crossbeam-epoch for RUSTSEC-2026-0204 (#15614)

## Patch
### Cargo.lock
```diff
@@ -3844,9 +3844,9 @@ dependencies = [
 
 [[package]]
 name = "crossbeam-epoch"
-version = "0.9.18"
+version = "0.9.20"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5b82ac4a3c2ca9c3460964f020e1402edd5753411d7737aa39c3714ad1b5420e"
+checksum = "2d6914041f254d6e9176c01941b21115dcfb7089e55135a35411081bd106ef3f"
 dependencies = [
  "crossbeam-utils",
 ]
```
