# [?] Remove RUSTSEC-2023-0052 from ignored errors as it's fixed now (#2090)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/fuel-core
Published: 2024-08-15
Source: https://github.com/FuelLabs/fuel-core/commit/59fe33338f5e8e3354b0cdba51a450683f9d7f6d
Type: security-commit

## Details
Remove RUSTSEC-2023-0052 from ignored errors as it's fixed now (#2090)

Closes #1316, closes #1317 

We no longer depend on `webpki`

## Patch
### .cargo/audit.toml
```diff
@@ -1,5 +1,4 @@
 [advisories]
 ignore = [
-    "RUSTSEC-2023-0052", # https://github.com/FuelLabs/fuel-core/issues/1316
     "RUSTSEC-2024-0336" # https://github.com/FuelLabs/fuel-core/issues/1843
-    ]
\ No newline at end of file
+]
\ No newline at end of file
```
