# [?] chore(deny): ignore RUSTSEC-2026-0097 (#14272)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-04-12
Source: https://github.com/foundry-rs/foundry/commit/9dff1b5e4572fb2a678b9ad8ff2084b7617fa614
Type: security-commit

## Details
chore(deny): ignore RUSTSEC-2026-0097 (#14272)

## Patch
### deny.toml
```diff
@@ -9,6 +9,8 @@ ignore = [
     "RUSTSEC-2024-0436",
     # https://rustsec.org/advisories/RUSTSEC-2025-0141 bincode is unmaintained
     "RUSTSEC-2025-0141",
+    # https://rustsec.org/advisories/RUSTSEC-2026-0097 rand is unsound with a custom logger
+    "RUSTSEC-2026-0097",
 ]
 
 # This section is considered when running `cargo deny check bans`.
```
