# [?] cargo: Ignore RUSTSEC-2021-0124 until fortanix loader bumps tokio

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2021-11-17
Source: https://github.com/oasisprotocol/oasis-core/commit/24a90ce84ffd7d552b78b9f2b8f2d0a8c8092101
Type: security-commit

## Details
cargo: Ignore RUSTSEC-2021-0124 until fortanix loader bumps tokio

## Patch
### .cargo/audit.toml
```diff
@@ -2,4 +2,5 @@
 ignore = [
     "RUSTSEC-2020-0071", # Remove once upstream dependencies are updated.
     "RUSTSEC-2020-0159", # Remove once upstream dependencies are updated.
+    "RUSTSEC-2021-0124", # Remove once upstream dependencies are updated.
 ]
```
