# [?] chore: ignore RUSTSEC-2025-0137 (#20633)

## Summary
Severity: Unknown
Chain: Ethereum
Component: paradigmxyz/reth
Published: 2025-12-24
Source: https://github.com/paradigmxyz/reth/commit/8ae7a1c8d14025243919d9c05d3505ef414f6937
Type: security-commit

## Details
chore: ignore RUSTSEC-2025-0137 (#20633)

## Patch
### deny.toml
```diff
@@ -8,6 +8,8 @@ ignore = [
     "RUSTSEC-2024-0384",
     # https://rustsec.org/advisories/RUSTSEC-2024-0436 paste! is unmaintained
     "RUSTSEC-2024-0436",
+    # https://rustsec.org/advisories/RUSTSEC-2025-0137 `reciprocal_mg10` OOB, unused
+    "RUSTSEC-2025-0137",
 ]
 
 # This section is considered when running `cargo deny check bans`.
```
