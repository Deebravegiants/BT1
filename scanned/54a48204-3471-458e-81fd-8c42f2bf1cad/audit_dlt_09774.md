# [?] Ignore RUSTSEC-2024-0421 (#2489)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/fuel-core
Published: 2024-12-09
Source: https://github.com/FuelLabs/fuel-core/commit/ab053a8511edb245da1f49da5b6f54c430541332
Type: security-commit

## Details
Ignore RUSTSEC-2024-0421 (#2489)

Tracked by https://github.com/FuelLabs/fuel-core/issues/2488

## Patch
### .cargo/audit.toml
```diff
@@ -1,2 +1,4 @@
 [advisories]
-ignore = []
\ No newline at end of file
+ignore = [
+    "RUSTSEC-2024-0421" # https://github.com/FuelLabs/fuel-core/issues/2488
+]
\ No newline at end of file
```
