# [?] change dataContext.tokenContext.fieldIndex to uint16_t to avoid plugin's 'context->parameterOffset' overflow on large tx (#228)

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2022-11-23
Source: https://github.com/LedgerHQ/app-ethereum/commit/071c96ea1309fc765b656eff1eab281dff87678d
Type: security-commit

## Details
change dataContext.tokenContext.fieldIndex to uint16_t to avoid plugin's 'context->parameterOffset' overflow on large tx (#228)

## Patch
### src/shared_context.h
```diff
@@ -53,7 +53,7 @@ typedef struct tokenContext_t {
     uint8_t pluginStatus;
 
     uint8_t data[INT256_LENGTH];
-    uint8_t fieldIndex;
+    uint16_t fieldIndex;
     uint8_t fieldOffset;
 
     uint8_t pluginUiMaxItems;
```
