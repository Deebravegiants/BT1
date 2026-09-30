# [?] Resolve RUSTSEC-2025-0006 (#2816)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/fuel-core
Published: 2025-03-07
Source: https://github.com/FuelLabs/fuel-core/commit/e25c7d68e745ec72f8643d8a8e263e6a8daa2ea0
Type: security-commit

## Details
Resolve RUSTSEC-2025-0006 (#2816)

Closes https://github.com/FuelLabs/fuel-core/issues/2815

## Patch
### .cargo/audit.toml
```diff
@@ -1,4 +1,5 @@
 [advisories]
 ignore = [
-    "RUSTSEC-2024-0421" # https://github.com/FuelLabs/fuel-core/issues/2488
+    "RUSTSEC-2024-0421", # https://github.com/FuelLabs/fuel-core/issues/2488
+    "RUSTSEC-2025-0009", # https://github.com/FuelLabs/fuel-core/issues/2814
 ]
\ No newline at end of file
```
