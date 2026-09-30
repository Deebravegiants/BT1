# [?] fix: bump crossbeam-epoch to 0.9.20 for RUSTSEC-2026-0204 (#12166)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-07-07
Source: https://github.com/iotaledger/iota/commit/e160eac9778ac0674c4b0e452376cb97107eddab
Type: security-commit

## Details
fix: bump crossbeam-epoch to 0.9.20 for RUSTSEC-2026-0204 (#12166)

Co-authored-by: Claude <noreply@anthropic.com>

## Patch
### external-crates/move/Cargo.lock
```diff
@@ -675,9 +675,9 @@ dependencies = [
 
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
