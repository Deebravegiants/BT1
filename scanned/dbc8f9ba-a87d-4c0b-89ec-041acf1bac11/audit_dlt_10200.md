# [?] ci: Ignore RUSTSEC-2020-0071 and RUSTSEC-2020-0159 for now

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2021-10-18
Source: https://github.com/oasisprotocol/oasis-core/commit/0f7ccd373aad28ebdfb27ad407017e95f633e5a7
Type: security-commit

## Details
ci: Ignore RUSTSEC-2020-0071 and RUSTSEC-2020-0159 for now

Upstream dependencies must update and runtimes should never be querying
local time anyway.

## Patch
### .cargo/audit.toml
```diff
@@ -0,0 +1,5 @@
+[advisories]
+ignore = [
+    "RUSTSEC-2020-0071", # Remove once upstream dependencies are updated.
+    "RUSTSEC-2020-0159", # Remove once upstream dependencies are updated.
+]
```
