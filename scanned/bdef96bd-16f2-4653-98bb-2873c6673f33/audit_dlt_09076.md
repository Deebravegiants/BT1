# [?] use size_t instead of uint8_t to prevent potential integer overflows

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2022-01-20
Source: https://github.com/LedgerHQ/app-ethereum/commit/6c03be385cc0434e81dfad4089bc83d8a61a90a4
Type: security-commit

## Details
use size_t instead of uint8_t to prevent potential integer overflows

## Patch
### src_features/provideNFTInformation/cmd_provideNFTInfo.c
```diff
@@ -73,7 +73,7 @@ void handleProvideNFTInformation(uint8_t p1,
 
     PRINTF("Provisioning currentItemIndex %d\n", tmpCtx.transactionContext.currentItemIndex);
 
-    uint8_t offset = 0;
+    size_t offset = 0;
 
     if (dataLength <= HEADER_SIZE) {
         PRINTF("Data too small for headers: expected at least %d, got %d\n",
@@ -108,8 +108,8 @@ void handleProvideNFTInformation(uint8_t p1,
     offset += NAME_LENGTH_SIZE;
 
     // Size of the payload (everything except the signature)
-    uint8_t payloadSize = HEADER_SIZE + collectionNameLength + ADDRESS_LENGTH + CHAIN_ID_SIZE +
-                          KEY_ID_SIZE + ALGORITHM_ID_SIZE;
+    size_t payloadSize = HEADER_SIZE + collectionNameLength + ADDRESS_LENGTH + CHAIN_ID_SIZE +
+                         KEY_ID_SIZE + ALGORITHM_ID_SIZE;
     if (dataLength < payloadSize) {
         PRINTF("Data too small for payload: expected at least %d, got %d\n",
                payloadSize,
```

### src_features/setPlugin/cmd_setPlugin.c
```diff
@@ -98,7 +98,7 @@ void handleSetPlugin(uint8_t p1,
     cx_ecfp_public_key_t pluginKey = {0};
     tokenContext_t *tokenContext = &dataContext.tokenContext;
 
-    uint8_t offset = 0;
+    size_t offset = 0;
 
     if (dataLength <= HEADER_SIZE) {
         PRINTF("Data too small for headers: expected at least %d, got %d\n",
@@ -135,8 +135,8 @@ void handleSetPlugin(uint8_t p1,
     offset += PLUGIN_NAME_LENGTH_SIZE;
 
     // Size of the payload (everything except the signature)
-    uint8_t payloadSize = HEADER_SIZE + pluginNameLength + ADDRESS_LENGTH + SELECTOR_SIZE +
-                          CHAIN_ID_SIZE + KEY_ID_SIZE + ALGORITHM_ID_SIZE;
+    size_t payloadSize = HEADER_SIZE + pluginNameLength + ADDRESS_LENGTH + SELECTOR_SIZE +
+                         CHAIN_ID_SIZE + KEY_ID_SIZE + ALGORITHM_ID_SIZE;
     if (dataLength < payloadSize) {
         PRINTF("Data too small for payload: expected at least %d, got %d\n",
                payloadSize,
```
