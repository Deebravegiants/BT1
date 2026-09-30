# [?] fix(deps): bump crossbeam-epoch to 0.9.20 in root Cargo.lock (RUSTSEC-2026-0204) (#12179)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-07-08
Source: https://github.com/iotaledger/iota/commit/0fbba46b37f6d7623a31951baba420e863f9b965
Type: security-commit

## Details
fix(deps): bump crossbeam-epoch to 0.9.20 in root Cargo.lock (RUSTSEC-2026-0204) (#12179)

Co-authored-by: Claude <noreply@anthropic.com>

## Patch
### Cargo.lock
```diff
@@ -2747,9 +2747,9 @@ dependencies = [
 
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
