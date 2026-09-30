# [?] cargo/audit: Ignore RUSTSEC-2024-0437

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2025-03-10
Source: https://github.com/oasisprotocol/oasis-core/commit/7d2a2aa6bcfac09d3c82366066a2ccf108da3719
Type: security-commit

## Details
cargo/audit: Ignore RUSTSEC-2024-0437

## Patch
### .cargo/audit.toml
```diff
@@ -1,4 +1,5 @@
 [advisories]
 ignore = [
     "RUSTSEC-2023-0071", # Does not affect our current use of the library.
+    "RUSTSEC-2024-0437", # Ignoring until dependencies are upgraded to protobuf v3.
 ]
```
