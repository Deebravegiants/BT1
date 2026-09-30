# [?] rust: Add RUSTSEC-2026-0099 to audit.toml

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2026-04-15
Source: https://github.com/oasisprotocol/oasis-core/commit/6330716cf8c463fb1ece4ba4bc59f3aad870c026
Type: security-commit

## Details
rust: Add RUSTSEC-2026-0099 to audit.toml

## Patch
### .cargo/audit.toml
```diff
@@ -3,4 +3,5 @@ ignore = [
     "RUSTSEC-2023-0071", # Does not affect our current use of the library.
     "RUSTSEC-2026-0049", # Vulnerable crate is only used in simple-rofl test runtime.
     "RUSTSEC-2026-0098", # Vulnerable crate is only used in simple-rofl test runtime.
+    "RUSTSEC-2026-0099", # Vulnerable crate is only used in simple-rofl test runtime.
 ]
```
