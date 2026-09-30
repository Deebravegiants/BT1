# [?] fix(oob): capitalized columns names (#188)

## Summary
Severity: Unknown
Chain: Linea
Component: LFDT-Lineth/lineth-monorepo
Published: 2024-05-17
Source: https://github.com/LFDT-Lineth/lineth-monorepo/commit/9057825c7a3658c284df0ec811604276df29facc
Type: security-commit

## Details
fix(oob): capitalized columns names (#188)

## Patch
### oob/columns.lisp
```diff
@@ -22,13 +22,13 @@
   (IS_ECADD :binary@prove)
   (IS_ECMUL :binary@prove)
   (IS_ECPAIRING :binary@prove)
-  (IS_BLAKE2F_cds :binary@prove)
-  (IS_BLAKE2F_params :binary@prove)
-  (IS_MODEXP_cds :binary@prove)
-  (IS_MODEXP_xbs :binary@prove)
-  (IS_MODEXP_lead :binary@prove)
-  (IS_MODEXP_pricing :binary@prove)
-  (IS_MODEXP_extract :binary@prove)
+  (IS_BLAKE2F_CDS :binary@prove)
+  (IS_BLAKE2F_PARAMS :binary@prove)
+  (IS_MODEXP_CDS :binary@prove)
+  (IS_MODEXP_XBS :binary@prove)
+  (IS_MODEXP_LEAD :binary@prove)
+  (IS_MODEXP_PRICING :binary@prove)
+  (IS_MODEXP_EXTRACT :binary@prove)
   (WCP_FLAG :binary@prove)
   (ADD_FLAG :binary@prove)
   (MOD_FLAG :binary@prove)
```
