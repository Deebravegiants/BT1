# [?] Merge pull request #5484 from oasisprotocol/peternose/trivial/audit-ignore-RUSTSEC-2023-0071

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2023-11-28
Source: https://github.com/oasisprotocol/oasis-core/commit/d8a4377f483279467398e6008fd074069a1c779b
Type: security-commit

## Details
Merge pull request #5484 from oasisprotocol/peternose/trivial/audit-ignore-RUSTSEC-2023-0071

cargo: Ignore RUSTSEC-2023-0071

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
