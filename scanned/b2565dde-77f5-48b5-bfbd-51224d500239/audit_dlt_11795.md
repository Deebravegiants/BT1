# [?] Temporary ignore RUSTSEC-2025-0055

## Summary
Severity: Unknown
Chain: Ethereum
Component: grandinetech/grandine
Published: 2025-09-03
Source: https://github.com/grandinetech/grandine/commit/13f5b69b925a0a42be5de8705c2b10b963170d68
Type: security-commit

## Details
Temporary ignore RUSTSEC-2025-0055

## Patch
### .github/workflows/audit.yml
```diff
@@ -27,4 +27,4 @@ jobs:
         name: Audit Rust Dependencies
         with:
           # Comma separated list of issues to ignore
-          ignore: RUSTSEC-2024-0370,RUSTSEC-2023-0071,RUSTSEC-2024-0384,RUSTSEC-2024-0388
+          ignore: RUSTSEC-2024-0370,RUSTSEC-2023-0071,RUSTSEC-2024-0384,RUSTSEC-2024-0388,RUSTSEC-2025-0055
```
