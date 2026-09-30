# [?] rust: Add RUSTSEC-2026-0104 to audit.toml

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2026-04-22
Source: https://github.com/oasisprotocol/oasis-core/commit/262b576129b3b7bde9bb62514d9c4cf8b0b196cc
Type: security-commit

## Details
rust: Add RUSTSEC-2026-0104 to audit.toml

## Patch
### .cargo/audit.toml
```diff
@@ -4,4 +4,5 @@ ignore = [
     "RUSTSEC-2026-0049", # Vulnerable crate is only used in simple-rofl test runtime.
     "RUSTSEC-2026-0098", # Vulnerable crate is only used in simple-rofl test runtime.
     "RUSTSEC-2026-0099", # Vulnerable crate is only used in simple-rofl test runtime.
+    "RUSTSEC-2026-0104", # Vulnerable crate is only used in simple-rofl test runtime.
 ]
```

### .changelog/6513.internal.md
```diff
@@ -0,0 +1 @@
+rust: Add RUSTSEC-2026-0104 to audit.toml
```
