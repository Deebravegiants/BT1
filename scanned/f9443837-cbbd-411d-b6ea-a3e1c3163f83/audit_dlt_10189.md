# [?] Merge pull request #5348 from oasisprotocol/kostko/fix/audit-ignore-RUSTSEC-2022-0093

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2023-08-15
Source: https://github.com/oasisprotocol/oasis-core/commit/d9ea485e8095126ff8fe9d4519cd3c7bf2aaeadd
Type: security-commit

## Details
Merge pull request #5348 from oasisprotocol/kostko/fix/audit-ignore-RUSTSEC-2022-0093

cargo: Ignore RUSTSEC-2022-0093 until we can update ed25519-dalek to v2

## Patch
### .cargo/audit.toml
```diff
@@ -1,6 +1,6 @@
 [advisories]
 ignore = [
     "RUSTSEC-2020-0071", # Remove once upstream dependencies are updated.
-    "RUSTSEC-2020-0159", # Remove once upstream dependencies are updated.
     "RUSTSEC-2021-0124", # Remove once upstream dependencies are updated.
+    "RUSTSEC-2022-0093", # Remove once we can update to ed25519-dalek to v2.
 ]
```
