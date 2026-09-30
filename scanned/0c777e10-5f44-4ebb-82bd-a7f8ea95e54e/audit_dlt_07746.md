# [?] chore: ignore RUSTSEC-2025-0141 bincode advisory (#20815)

## Summary
Severity: Unknown
Chain: Ethereum
Component: paradigmxyz/reth
Published: 2026-01-07
Source: https://github.com/paradigmxyz/reth/commit/050d9f440fd35407f40b56fa80654e5b0141798f
Type: security-commit

## Details
chore: ignore RUSTSEC-2025-0141 bincode advisory (#20815)

## Patch
### deny.toml
```diff
@@ -8,8 +8,8 @@ ignore = [
     "RUSTSEC-2024-0384",
     # https://rustsec.org/advisories/RUSTSEC-2024-0436 paste! is unmaintained
     "RUSTSEC-2024-0436",
-    # https://rustsec.org/advisories/RUSTSEC-2025-0137 `reciprocal_mg10` OOB, unused
-    "RUSTSEC-2025-0137",
+    # https://rustsec.org/advisories/RUSTSEC-2025-0141 bincode is unmaintained, need to transition all deps to wincode first
+    "RUSTSEC-2025-0141",
 ]
 
 # This section is considered when running `cargo deny check bans`.
```
