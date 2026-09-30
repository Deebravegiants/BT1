# [?] fix(deps): bump quinn-proto to 0.11.15 for RUSTSEC-2026-0185 (#12022)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-06-24
Source: https://github.com/iotaledger/iota/commit/7d8798af303ec6fbbb5d65806b99f481664606fc
Type: security-commit

## Details
fix(deps): bump quinn-proto to 0.11.15 for RUSTSEC-2026-0185 (#12022)

Co-authored-by: Claude <noreply@anthropic.com>

## Patch
### Cargo.lock
```diff
@@ -11579,9 +11579,9 @@ dependencies = [
 
 [[package]]
 name = "quinn-proto"
-version = "0.11.14"
+version = "0.11.15"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "434b42fec591c96ef50e21e886936e66d3cc3f737104fdb9b737c40ffb94c098"
+checksum = "4fcb935c5bec503c2f0e306bdd3e58bb9029dcb14fa8d9ac76e3a5256ac0763e"
 dependencies = [
  "bytes",
  "fastbloom",
```

### crates/iota-core/Cargo.toml
```diff
@@ -39,7 +39,7 @@ object_store.workspace = true
 once_cell.workspace = true
 parking_lot.workspace = true
 prometheus.workspace = true
-quinn-proto = "0.11.14"
+quinn-proto = "0.11.15"
 rand.workspace = true
 rayon = "1.5.3"
 reqwest.workspace = true
```
