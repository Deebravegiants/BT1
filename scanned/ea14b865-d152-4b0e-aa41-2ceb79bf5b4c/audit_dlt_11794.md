# [?] Ignore RUSTSEC-2025-0137

## Summary
Severity: Unknown
Chain: Ethereum
Component: grandinetech/grandine
Published: 2026-01-02
Source: https://github.com/grandinetech/grandine/commit/d5f18315e583677c5e00aab9d3bcb80f89963372
Type: security-commit

## Details
Ignore RUSTSEC-2025-0137

The RUSTSEC-2025-0137 comes from risc0-build crate. It is used only
during build-time, we don't care about unsoundness issue.

## Patch
### .github/workflows/audit.yml
```diff
@@ -27,4 +27,4 @@ jobs:
         name: Audit Rust Dependencies
         with:
           # Comma separated list of issues to ignore
-          ignore: RUSTSEC-2024-0370,RUSTSEC-2023-0071,RUSTSEC-2024-0384,RUSTSEC-2024-0388,RUSTSEC-2025-0055,RUSTSEC-2025-0009,RUSTSEC-2024-0336
+          ignore: RUSTSEC-2024-0370,RUSTSEC-2023-0071,RUSTSEC-2024-0384,RUSTSEC-2024-0388,RUSTSEC-2025-0055,RUSTSEC-2025-0009,RUSTSEC-2024-0336,RUSTSEC-2025-0137
```
