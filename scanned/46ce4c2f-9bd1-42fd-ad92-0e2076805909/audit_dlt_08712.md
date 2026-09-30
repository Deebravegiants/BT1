# [?] Avoid overflow when adding postingGas

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2025-05-20
Source: https://github.com/OffchainLabs/nitro/commit/2921d4f5f6e07cd6a354b90b229c5fc4c1abba70
Type: security-commit

## Details
Avoid overflow when adding postingGas

## Patch
### go-ethereum
```diff
@@ -1 +1 @@
-Subproject commit fe26733018a512f6977381f4e1883d375587688e
+Subproject commit c0bc96bfef14209be6b8a046b7a7826ea0b03d9d
```
