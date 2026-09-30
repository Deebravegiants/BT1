# [?] Ignore RUSTSEC-2026-{0098, 0099} for now (#3266)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/fuel-core
Published: 2026-04-16
Source: https://github.com/FuelLabs/fuel-core/commit/a4767fbecdaa8d34ecb6813aa225599af784df8d
Type: security-commit

## Details
Ignore RUSTSEC-2026-{0098, 0099} for now (#3266)

See #3265. Ignores RUSTSEC-2026-{0098, 0099} that are currently blocking
our CI.

## Patch
### .cargo/audit.toml
```diff
@@ -1,4 +1,6 @@
 [advisories]
 ignore = [
     "RUSTSEC-2025-0009", # https://github.com/FuelLabs/fuel-core/issues/2814
+    "RUSTSEC-2026-0098", # https://github.com/FuelLabs/fuel-core/issues/3265
+    "RUSTSEC-2026-0099", # https://github.com/FuelLabs/fuel-core/issues/3265
 ]
```
