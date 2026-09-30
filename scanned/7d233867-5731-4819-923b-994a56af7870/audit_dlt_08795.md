# [?] fix(rlprcpt): index column overflows (#252)

## Summary
Severity: Unknown
Chain: Linea
Component: LFDT-Lineth/lineth-monorepo
Published: 2024-07-15
Source: https://github.com/LFDT-Lineth/lineth-monorepo/commit/4011a9d401ed6de33b9dc9813522af70e3cc80ca
Type: security-commit

## Details
fix(rlprcpt): index column overflows (#252)

## Patch
### rlptxrcpt/columns.lisp
```diff
@@ -8,7 +8,7 @@
   (LIMB :i128 :display :bytes)
   (nBYTES :i5)
   (LIMB_CONSTRUCTED :binary@prove)
-  (INDEX :i16)
+  (INDEX :i24)
   (INDEX_LOCAL :i16)
   (PHASE :binary@prove :array [5])
   (PHASE_END :binary@prove)
```
