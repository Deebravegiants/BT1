# [?] cargo: Ignore RUSTSEC-2023-0071

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2023-11-28
Source: https://github.com/oasisprotocol/oasis-core/commit/223a963c6c92125a040d3d81c76991d4b31ca28c
Type: security-commit

## Details
cargo: Ignore RUSTSEC-2023-0071

This vulnerability does not affect our current use of the library.

## Patch
### .cargo/audit.toml
```diff
@@ -2,4 +2,5 @@
 ignore = [
     "RUSTSEC-2020-0071", # Remove once upstream dependencies are updated.
     "RUSTSEC-2021-0124", # Remove once upstream dependencies are updated.
+    "RUSTSEC-2023-0071", # Does not affect our current use of the library.
 ]
```
