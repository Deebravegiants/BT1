# [?] chore: ignore RUSTSEC-2026-0002 (#20819)

## Summary
Severity: Unknown
Chain: Ethereum
Component: paradigmxyz/reth
Published: 2026-01-07
Source: https://github.com/paradigmxyz/reth/commit/a8980bf7c1c7a7d3c1d65f81ec43396e646b2592
Type: security-commit

## Details
chore: ignore RUSTSEC-2026-0002 (#20819)

## Patch
### deny.toml
```diff
@@ -10,6 +10,8 @@ ignore = [
     "RUSTSEC-2024-0436",
     # https://rustsec.org/advisories/RUSTSEC-2025-0141 bincode is unmaintained, need to transition all deps to wincode first
     "RUSTSEC-2025-0141",
+    #  https://rustsec.org/advisories/RUSTSEC-2026-0002 lru unused directly: <https://github.com/alloy-rs/alloy/pull/3460>
+    "RUSTSEC-2026-0002",
 ]
 
 # This section is considered when running `cargo deny check bans`.
```
