# [?] chore: bump crossbeam-epoch to 0.9.20 for RUSTSEC-2026-0204 (#6711)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2026-07-07
Source: https://github.com/chainflip-io/chainflip-backend/commit/a542a40023f33036d8ad3bb55c43a5c2ff9f7251
Type: security-commit

## Details
chore: bump crossbeam-epoch to 0.9.20 for RUSTSEC-2026-0204 (#6711)

Co-authored-by: Claude Fable 5 <noreply@anthropic.com>

## Patch
### Cargo.lock
```diff
@@ -3024,9 +3024,9 @@ dependencies = [
 
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
