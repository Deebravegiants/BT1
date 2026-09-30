# [?] Merge pull request #3562 from peilun-conflux/fix/cargo-deny-rustsec-2026-0190

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-07-01
Source: https://github.com/Conflux-Chain/conflux-rust/commit/eaff64ef48a526f273e0e0976447c146b29931f7
Type: security-commit

## Details
Merge pull request #3562 from peilun-conflux/fix/cargo-deny-rustsec-2026-0190

build(deps): bump anyhow to 1.0.103 for RUSTSEC-2026-0190

## Patch
### Cargo.lock
```diff
@@ -580,9 +580,9 @@ dependencies = [
 
 [[package]]
 name = "anyhow"
-version = "1.0.98"
+version = "1.0.103"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e16d2d3311acee920a9eb8d33b8cbc1787ce4a264e85f964c2404b969bdcd487"
+checksum = "2a4385e2e34eb35d6b3efe798b9eb88096925d87726c0798709bf56d9ed84af3"
 
 [[package]]
 name = "app_dirs"
```
