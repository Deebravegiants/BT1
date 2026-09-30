# [?] Fix multiple vulnerabilities

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2022-07-08
Source: https://github.com/LedgerHQ/app-ethereum/commit/e0218520d81ebf5b2aa0a5d2721a8a2d9302e78a
Type: security-commit

## Details
Fix multiple vulnerabilities

## Patch
### src/main.c
```diff
@@ -480,6 +480,36 @@ void handleGetWalletId(volatile unsigned int *tx) {
 
 #endif  // HAVE_WALLET_ID_SDK
 
+uint8_t *parseBip32(uint8_t *dataBuffer, uint16_t *dataLength, bip32_path_t *bip32) {
+    if (*dataLength < 1) {
+        PRINTF("Invalid data\n");
+        return NULL;
+    }
+
+    bip32->length = *dataBuffer;
+
+    if (bip32->length < 0x1 || bip32->length > MAX_BIP32_PATH) {
+        PRINTF("Invalid bip32\n");
+        return NULL;
+    }
+
+    dataBuffer++;
+    (*dataLength)--;
+
+    if (*dataLength < sizeof(uint32_t) * (bip32->length)) {
+        PRINTF("Invalid data\n");
+        return NULL;
+    }
+
+    for (uint8_t i = 0; i < bip32->length; i++) {
+        bip32->path[i] = U4BE(dataBuffer, 0);
+        dataBuffer += sizeof(uint32_t);
+        *dataLength -= sizeof(uint32_t);
+    }
+
+    return dataBuffer;
+}
+
 void handleApdu(unsigned int *flags, unsigned int *tx) {
     unsigned short sw = 0;
 
```

### src/shared_context.h
```diff
@@ -18,6 +18,11 @@
 
 #define N_storage (*(volatile internalStorage_t *) PIC(&N_storage_real))
 
+typedef struct bip32_path_t {
+    uint8_t length;
+    uint32_t path[MAX_BIP32_PATH];
+} bip32_path_t;
+
 typedef struct internalStorage_t {
     unsigned char dataAllowed;
     unsigned char contractDetails;
@@ -82,24 +87,21 @@ typedef union extraInfo_t {
 } extraInfo_t;
 
 typedef struct transactionContext_t {
-    uint8_t pathLength;
-    uint32_t bip32Path[MAX_BIP32_PATH];
+    bip32_path_t bip32;
     uint8_t hash[INT256_LENGTH];
     union extraInfo_t extraInfo[MAX_ITEMS];
     uint8_t tokenSet[MAX_ITEMS];
     uint8_t currentItemIndex;
 } transactionContext_t;
 
 typedef struct messageSigningContext_t {
-    uint8_t pathLength;
-    uint32_t bip32Path[MAX_BIP32_PATH];
+    bip32_path_t bip32;
     uint8_t hash[INT256_LENGTH];
     uint32_t remainingLength;
 } messageSigningContext_t;
 
 typedef struct messageSigningContext712_t {
-    uint8_t pathLength;
-    uint32_t bip32Path[MAX_BIP32_PATH];
+    bip32_path_t bip32;
     uint8_t domainHash[32];
     uint8_t messageHash[32];
 } messageSigningContext712_t;
@@ -217,5 +219,6 @@ extern uint32_t eth2WithdrawalIndex;
 #endif
 
 void reset_app_context(void);
+uint8_t *parseBip32(uint8_t *, uint16_t *, bip32_path_t *);
 
 #endif  // _SHARED_CONTEXT_H_
```

### src_common/ethUstream.c
```diff
@@ -296,6 +296,12 @@ static void processV(txContext_t *context) {
         PRINTF("Invalid type for RLP_V\n");
         THROW(EXCEPTION);
     }
+
+    if (context->currentFieldLength > sizeof(context->content->v)) {
+        PRINTF("Invalid length for RLP_V\n");
+        THROW(EXCEPTION);
+    }
+
     if (context->currentFieldPos < context->currentFieldLength) {
         uint32_t copySize =
             MIN(context->commandLength, context->currentFieldLength - context->currentFieldPos);
```

### src_common/uint256.c
```diff
@@ -476,6 +476,11 @@ bool tostring256(uint256_t *number, uint32_t baseParam, char *out, uint32_t outL
         divmod256(&rDiv, &base, &rDiv, &rMod);
         out[offset++] = HEXDIGITS[(uint8_t) LOWER(LOWER(rMod))];
     } while (!zero256(&rDiv));
+
+    if (offset > (outLength - 1)) {
+        return false;
+    }
+
     out[offset] = '\0';
     reverseString(out, offset);
     return true;
```

### src_features/getEth2PublicKey/cmd_getEth2PublicKey.c
```diff
@@ -46,29 +46,25 @@ void handleGetEth2PublicKey(uint8_t p1,
                             uint16_t dataLength,
                             unsigned int *flags,
                             unsigned int *tx) {
-    UNUSED(dataLength);
-    uint32_t bip32Path[MAX_BIP32_PATH];
-    uint32_t i;
-    uint8_t bip32PathLength = *(dataBuffer++);
+    bip32_path_t bip32;
 
     if (!called_from_swap) {
         reset_app_context();
     }
-    if ((bip32PathLength < 0x01) || (bip32PathLength > MAX_BIP32_PATH)) {
-        PRINTF("Invalid path\n");
-        THROW(0x6a80);
-    }
     if ((p1 != P1_CONFIRM) && (p1 != P1_NON_CONFIRM)) {
         THROW(0x6B00);
     }
     if (p2 != 0) {
         THROW(0x6B00);
     }
-    for (i = 0; i < bip32PathLength; i++) {
-        bip32Path[i] = U4BE(dataBuffer, 0);
-        dataBuffer += 4;
+
+    dataBuffer = parseBip32(dataBuffer, &dataLength, &bip32);
+
+    if (dataBuffer == NULL) {
+        THROW(0x6a80);
     }
-    getEth2PublicKey(bip32Path, bip32PathLength, tmpCtx.publicKeyContext.publicKey.W);
+
+    getEth2PublicKey(bip32.path, bip32.length, tmpCtx.publicKeyContext.publicKey.W);
 
 #ifndef NO_CONSENT
     if (p1 == P1_NON_CONFIRM)
```

### src_features/getPublicKey/cmd_getPublicKey.c
```diff
@@ -11,35 +11,33 @@ void handleGetPublicKey(uint8_t p1,
                         uint16_t dataLength,
                         unsigned int *flags,
                         unsigned int *tx) {
-    UNUSED(dataLength);
     uint8_t privateKeyData[INT256_LENGTH];
-    uint32_t bip32Path[MAX_BIP32_PATH];
-    uint32_t i;
-    uint8_t bip32PathLength = *(dataBuffer++);
+    bip32_path_t bip32;
     cx_ecfp_private_key_t privateKey;
+
     if (!called_from_swap) {
         reset_app_context();
     }
-    if ((bip32PathLength < 0x01) || (bip32PathLength > MAX_BIP32_PATH)) {
-        PRINTF("Invalid path\n");
-        THROW(0x6a80);
-    }
+
     if ((p1 != P1_CONFIRM) && (p1 != P1_NON_CONFIRM)) {
         THROW(0x6B00);
     }
     if ((p2 != P2_CHAINCODE) && (p2 != P2_NO_CHAINCODE)) {
         THROW(0x6B00);
     }
-    for (i = 0; i < bip32PathLength; i++) {
-        bip32Path[i] = U4BE(dataBuffer, 0);
-        dataBuffer += 4;
+
+    dataBuffer = parseBip32(dataBuffer, &dataLength, &bip32);
+
+    if (dataBuffer == NULL) {
+        THROW(0x6a80);
     }
+
     tmpCtx.publicKeyContext.getChaincode = (p2 == P2_CHAINCODE);
     io_seproxyhal_io_heartbeat();
     os_perso_derive_node_bip32(
         CX_CURVE_256K1,
-        bip32Path,
-        bip32PathLength,
+        bip32.path,
+        bip32.length,
         privateKeyData,
         (tmpCtx.publicKeyContext.getChaincode ? tmpCtx.publicKeyContext.chainCode : NULL));
     cx_ecfp_init_private_key(CX_CURVE_256K1, privateKeyData, 32, &privateKey);
```

### src_features/performPrivacyOperation/cmd_performPrivacyOperation.c
```diff
@@ -29,39 +29,35 @@ void handlePerformPrivacyOperation(uint8_t p1,
                                    uint16_t dataLength,
                                    unsigned int *flags,
                                    unsigned int *tx) {
-    UNUSED(dataLength);
     uint8_t privateKeyData[INT256_LENGTH];
     uint8_t privateKeyDataSwapped[INT256_LENGTH];
-    uint32_t bip32Path[MAX_BIP32_PATH];
-    uint8_t bip32PathLength = *(dataBuffer++);
+    bip32_path_t bip32;
     cx_err_t status = CX_OK;
-    if (p2 == P2_PUBLIC_ENCRYPTION_KEY) {
-        if (dataLength < 1 + 4 * bip32PathLength) {
-            THROW(0x6700);
-        }
-    } else if (p2 == P2_SHARED_SECRET) {
-        if (dataLength < 1 + 4 * bip32PathLength + 32) {
-            THROW(0x6700);
-        }
-    } else {
+
+    if ((p1 != P1_CONFIRM) && (p1 != P1_NON_CONFIRM)) {
         THROW(0x6B00);
     }
-    cx_ecfp_private_key_t privateKey;
-    if ((bip32PathLength < 0x01) || (bip32PathLength > MAX_BIP32_PATH)) {
-        PRINTF("Invalid path\n");
-        THROW(0x6a80);
+
+    if ((p2 != P2_PUBLIC_ENCRYPTION_KEY) && (p2 != P2_SHARED_SECRET)) {
+        THROW(0x6700);
     }
-    if ((p1 != P1_CONFIRM) && (p1 != P1_NON_CONFIRM)) {
-        THROW(0x6B00);
+
+    dataBuffer = parseBip32(dataBuffer, &dataLength, &bip32);
+
+    if (dataBuffer == NULL) {
+        THROW(0x6a80);
     }
-    for (uint8_t i = 0; i < bip32PathLength; i++) {
-        bip32Path[i] = U4BE(dataBuffer, 0);
-        dataBuffer += 4;
+
+    if ((p2 == P2_SHARED_SECRET) && (dataLength < 32)) {
+        THROW(0x6700);
     }
+
+    cx_ecfp_private_key_t privateKey;
+
     os_perso_derive_node_bip32(
         CX_CURVE_256K1,
-        bip32Path,
-        bip32PathLength,
+        bip32.path,
+        bip32.length,
         privateKeyData,
         (tmpCtx.publicKeyContext.getChaincode ? tmpCtx.publicKeyContext.chainCode : NULL));
     cx_ecfp_init_private_key(CX_CURVE_256K1, privateKeyData, 32, &privateKey);
```

### src_features/signMessage/cmd_signMessage.c
```diff
@@ -119,39 +119,26 @@ void handleSignPersonalMessage(uint8_t p1,
                                unsigned int *tx) {
     UNUSED(tx);
     uint8_t hashMessage[INT256_LENGTH];
+
     if (p1 == P1_FIRST) {
         char tmp[11] = {0};
-        uint32_t i;
-        if (dataLength < 1) {
-            PRINTF("Invalid data\n");
-            THROW(0x6a80);
-        }
+
         if (appState != APP_STATE_IDLE) {
             reset_app_context();
         }
         appState = APP_STATE_SIGNING_MESSAGE;
 
-        tmpCtx.messageSigningContext.pathLength = workBuffer[0];
-        if ((tmpCtx.messageSigningContext.pathLength < 0x01) ||
-            (tmpCtx.messageSigningContext.pathLength > MAX_BIP32_PATH)) {
-            PRINTF("Invalid path\n");
+        workBuffer = parseBip32(workBuffer, &dataLength, &tmpCtx.messageSigningContext.bip32);
+
+        if (workBuffer == NULL) {
             THROW(0x6a80);
         }
-        workBuffer++;
-        dataLength--;
-        for (i = 0; i < tmpCtx.messageSigningContext.pathLength; i++) {
-            if (dataLength < sizeof(uint32_t)) {
-                PRINTF("Invalid data\n");
-                THROW(0x6a80);
-            }
-            tmpCtx.messageSigningContext.bip32Path[i] = U4BE(workBuffer, 0);
-            workBuffer += sizeof(uint32_t);
-            dataLength -= sizeof(uint32_t);
-        }
+
         if (dataLength < sizeof(uint32_t)) {
             PRINTF("Invalid data\n");
             THROW(0x6a80);
         }
+
         tmpCtx.messageSigningContext.remainingLength = U4BE(workBuffer, 0);
         workBuffer += sizeof(uint32_t);
         dataLength -= sizeof(uint32_t);
```

### src_features/signMessage/ui_common_signMessage.c
```diff
@@ -9,8 +9,8 @@ unsigned int io_seproxyhal_touch_signMessage_ok(__attribute__((unused)) const ba
     uint32_t tx = 0;
     io_seproxyhal_io_heartbeat();
     os_perso_derive_node_bip32(CX_CURVE_256K1,
-                               tmpCtx.messageSigningContext.bip32Path,
-                               tmpCtx.messageSigningContext.pathLength,
+                               tmpCtx.messageSigningContext.bip32.path,
+                               tmpCtx.messageSigningContext.bip32.length,
                                privateKeyData,
                                NULL);
     io_seproxyhal_io_heartbeat();
```

### src_features/signMessageEIP712/cmd_signMessage712.c
```diff
@@ -9,40 +9,20 @@ void handleSignEIP712Message(uint8_t p1,
                              uint16_t dataLength,
                              unsigned int *flags,
                              unsigned int *tx) {
-    uint8_t i;
-
     UNUSED(tx);
     if ((p1 != 00) || (p2 != 00)) {
         THROW(0x6B00);
     }
     if (appState != APP_STATE_IDLE) {
         reset_app_context();
     }
-    if (dataLength < 1) {
-        PRINTF("Invalid data\n");
-        THROW(0x6a80);
-    }
-    tmpCtx.messageSigningContext712.pathLength = workBuffer[0];
-    if ((tmpCtx.messageSigningContext712.pathLength < 0x01) ||
-        (tmpCtx.messageSigningContext712.pathLength > MAX_BIP32_PATH)) {
-        PRINTF("Invalid path\n");
-        THROW(0x6a80);
-    }
-    workBuffer++;
-    dataLength--;
-    for (i = 0; i < tmpCtx.messageSigningContext712.pathLength; i++) {
-        if (dataLength < 4) {
-            PRINTF("Invalid data\n");
-            THROW(0x6a80);
-        }
-        tmpCtx.messageSigningContext712.bip32Path[i] = U4BE(workBuffer, 0);
-        workBuffer += 4;
-        dataLength -= 4;
-    }
-    if (dataLength < 32 + 32) {
-        PRINTF("Invalid data\n");
+
+    workBuffer = parseBip32(workBuffer, &dataLength, &tmpCtx.messageSigningContext.bip32);
+
+    if (workBuffer == NULL || dataLength < 32 + 32) {
         THROW(0x6a80);
     }
+
     memmove(tmpCtx.messageSigningContext712.domainHash, workBuffer, 32);
     memmove(tmpCtx.messageSigningContext712.messageHash, workBuffer + 32, 32);
 
```

### src_features/signMessageEIP712/ui_common_signMessage712.c
```diff
@@ -34,8 +34,8 @@ unsigned int io_seproxyhal_touch_signMessage712_v0_ok(__attribute__((unused))
     PRINTF("EIP712 hash to sign %.*H\n", 32, hash);
     io_seproxyhal_io_heartbeat();
     os_perso_derive_node_bip32(CX_CURVE_256K1,
-                               tmpCtx.messageSigningContext712.bip32Path,
-                               tmpCtx.messageSigningContext712.pathLength,
+                               tmpCtx.messageSigningContext712.bip32.path,
+                               tmpCtx.messageSigningContext712.bip32.length,
                                privateKeyData,
                                NULL);
     io_seproxyhal_io_heartbeat();
```

### src_features/signTx/cmd_signTx.c
```diff
@@ -12,43 +12,33 @@ void handleSign(uint8_t p1,
                 unsigned int *tx) {
     UNUSED(tx);
     parserStatus_e txResult;
-    uint32_t i;
 
     if (os_global_pin_is_validated() != BOLOS_UX_OK) {
         PRINTF("Device is PIN-locked");
         THROW(0x6982);
     }
     if (p1 == P1_FIRST) {
-        if (dataLength < 1) {
-            PRINTF("Invalid data\n");
-            THROW(0x6a80);
-        }
         if (appState != APP_STATE_IDLE) {
             reset_app_context();
         }
         appState = APP_STATE_SIGNING_TX;
-        tmpCtx.transactionContext.pathLength = workBuffer[0];
-        if ((tmpCtx.transactionContext.pathLength < 0x01) ||
-            (tmpCtx.transactionContext.pathLength > MAX_BIP32_PATH)) {
-            PRINTF("Invalid path\n");
+
+        workBuffer = parseBip32(workBuffer, &dataLength, &tmpCtx.transactionContext.bip32);
+
+        if (workBuffer == NULL) {
             THROW(0x6a80);
         }
-        workBuffer++;
-        dataLength--;
-        for (i = 0; i < tmpCtx.transactionContext.pathLength; i++) {
-            if (dataLength < 4) {
-                PRINTF("Invalid data\n");
-                THROW(0x6a80);
-            }
-            tmpCtx.transactionContext.bip32Path[i] = U4BE(workBuffer, 0);
-            workBuffer += 4;
-            dataLength -= 4;
-        }
+
         tmpContent.txContent.dataPresent = false;
         dataContext.tokenContext.pluginStatus = ETH_PLUGIN_RESULT_UNAVAILABLE;
 
         initTx(&txContext, &global_sha3, &tmpContent.txContent, customProcessor, NULL);
 
+        if (dataLength < 1) {
+            PRINTF("Invalid data\n");
+            THROW(0x6a80);
+        }
+
         // EIP 2718: TransactionType might be present before the TransactionPayload.
         uint8_t txType = *workBuffer;
         if (txType >= MIN_TX_TYPE && txType <= MAX_TX_TYPE) {
```
