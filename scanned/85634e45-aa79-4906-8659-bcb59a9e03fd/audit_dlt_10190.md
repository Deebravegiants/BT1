# [?] cargo: Ignore RUSTSEC-2022-0093 until we can update ed25519-dalek to v2

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2023-08-15
Source: https://github.com/oasisprotocol/oasis-core/commit/f024c7bba395a976801474ed641e98eb1b297c55
Type: security-commit

## Details
cargo: Ignore RUSTSEC-2022-0093 until we can update ed25519-dalek to v2

This vulnerability does not affect our current use of the library.

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
