# [?] Remove RustSec Ignore for RUSTSEC-2022-0093 (#1586)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/fuel-core
Published: 2024-01-06
Source: https://github.com/FuelLabs/fuel-core/commit/df821a0fe57754fd24b0adc1cf5acfa7a8c949a6
Type: security-commit

## Details
Remove RustSec Ignore for RUSTSEC-2022-0093 (#1586)

Closes https://github.com/FuelLabs/fuel-core/issues/1298

---------

Co-authored-by: Green Baneling <XgreenX9999@gmail.com>

## Patch
### .cargo/audit.toml
```diff
@@ -1,2 +1,2 @@
 [advisories]
-ignore = ["RUSTSEC-2022-0093", "RUSTSEC-2023-0052"] # https://github.com/FuelLabs/fuel-core/issues/1298, https://github.com/FuelLabs/fuel-core/issues/1317
\ No newline at end of file
+ignore = ["RUSTSEC-2023-0052"] # https://github.com/FuelLabs/fuel-core/issues/1317
\ No newline at end of file
```
