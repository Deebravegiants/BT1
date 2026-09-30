# [?] fix: decodeCalldata crash (#1200)

## Summary
Severity: Unknown
Chain: Rabby
Component: RabbyHub/Rabby
Published: 2022-12-18
Source: https://github.com/RabbyHub/Rabby/commit/0a8c70ff649288887b773e202696baf0698021bd
Type: security-commit

## Details
fix: decodeCalldata crash (#1200)

## Patch
### src/ui/views/DexSwap/hooks.tsx
```diff
@@ -84,7 +84,11 @@ export const useVerifyCalldata = <
 ) => {
   const callDataResult = useMemo(() => {
     if (dexId && dexId !== DEX_ENUM.WRAPTOKEN && tx) {
-      return decodeCalldata(dexId, tx) as DecodeCalldataResult;
+      try {
+        return decodeCalldata(dexId, tx) as DecodeCalldataResult;
+      } catch (error) {
+        return null;
+      }
     }
     return null;
   }, [dexId, tx]);
```
