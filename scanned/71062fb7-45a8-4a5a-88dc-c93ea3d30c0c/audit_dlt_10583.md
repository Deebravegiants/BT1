# [?] chore: ignore RUSTSEC-2025-0137 (#12941)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2025-12-28
Source: https://github.com/foundry-rs/foundry/commit/82d530d5c991153eb0fe054870c308474f5f1a27
Type: security-commit

## Details
chore: ignore RUSTSEC-2025-0137 (#12941)

Co-authored-by: Claude <noreply@anthropic.com>

## Patch
### deny.toml
```diff
@@ -9,6 +9,8 @@ ignore = [
     "RUSTSEC-2024-0436",
     # https://rustsec.org/advisories/RUSTSEC-2024-0437 protobuf! Crash due to uncontrolled recursion in protobuf crate.
     "RUSTSEC-2024-0437",
+    # https://rustsec.org/advisories/RUSTSEC-2025-0137 `reciprocal_mg10` OOB, unused
+    "RUSTSEC-2025-0137",
 ]
 
 # This section is considered when running `cargo deny check bans`.
```
