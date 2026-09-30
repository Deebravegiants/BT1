# [?] fix: ignore RUSTSEC-2024-0402 which we don't care about

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2024-12-05
Source: https://github.com/fedimint/fedimint/commit/7787c10f0b56f0ff7a710bf4c2323def30a062e3
Type: security-commit

## Details
fix: ignore RUSTSEC-2024-0402 which we don't care about

## Patch
### .cargo/audit.toml
```diff
@@ -9,4 +9,9 @@
 #
 # See the full example in: https://raw.githubusercontent.com/rustsec/rustsec/main/cargo-audit/audit.toml.example
 [advisories]
-ignore = ["RUSTSEC-2023-0052", "RUSTSEC-2023-0071"]
+ignore = [
+  "RUSTSEC-2023-0052",
+  "RUSTSEC-2023-0071",
+  # we don't use borsch encoding
+  "RUSTSEC-2024-0402"
+]
```
