# [?] chore: ignore RUSTSEC-2024-0370 (#8821)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2024-09-06
Source: https://github.com/foundry-rs/foundry/commit/4f202da4ea6d94f18cbab8cab43ff4d7e0f6aeb2
Type: security-commit

## Details
chore: ignore RUSTSEC-2024-0370 (#8821)

## Patch
### deny.toml
```diff
@@ -8,6 +8,8 @@ ignore = [
     # https://github.com/watchexec/watchexec/issues/852
     "RUSTSEC-2024-0350",
     "RUSTSEC-2024-0351",
+    # proc-macro-error is unmaintained
+    "RUSTSEC-2024-0370",
 ]
 
 # This section is considered when running `cargo deny check bans`.
```
