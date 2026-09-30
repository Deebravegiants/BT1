# [?] fix(core): fix OOB read in NFC card emulation

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2026-03-26
Source: https://github.com/trezor/trezor-firmware/commit/74618edb847b023f326b398a8df7c84eda3aa57a
Type: security-commit

## Details
fix(core): fix OOB read in NFC card emulation

[no changelog]

## Patch
### core/embed/io/nfc/st25/card_emulation.c
```diff
@@ -64,6 +64,17 @@ enum States {
 #define FID_NDEF 0x0001 /*!< File ID number for NDEF file */
 #define T3T_BLOCK_SIZE \
   0x10 /*!< Block size in Type 3 Tag                        */
+/**
+ * T3T minimum fixed-offset accesses:
+ *   [0]     LEN
+ *   [1]     CMD
+ *   [2..9]  NFCID2
+ *   [10]    NoS
+ *   [11..12] Service code
+ *   [13]    NoB
+ *   [14..] Block list + Block data (variable)
+ */
+#define T3T_MIN_CMD_LEN 14
 /**
  * @}
  */
@@ -170,15 +181,21 @@ static uint8_t InformationBlock[] = {
  * @brief  Compare 2 commands supplied in parameters
  *
  * @param[in]  cmd : pointer to the received command.
+ * @param[in]  cmdLen : length of the received command.
  * @param[in]  find : pointer to the avalaible command.
  * @param[in]  len : length of the available command.
  *
  * @retval True : Same command.
  * @retval False : Different command.
  *****************************************************************************
  */
-static bool cmd_compare(uint8_t *cmd, uint8_t *find, uint16_t len) {
-  for (int i = 0; i < 20; i++) {
+static bool cmd_compare(uint8_t *cmd, uint16_t cmdLen, uint8_t *find,
+                        uint16_t len) {
+  if (len > cmdLen) {
+    return false;
+  }
+  uint16_t limit = (uint16_t)(cmdLen - len);
+  for (uint16_t i = 0; i <= limit; i++) {
     if (!memcmp(&cmd[i], find, len)) {
       return true;
     }
@@ -191,12 +208,14 @@ static bool cmd_compare(uint8_t *cmd, uint8_t *find, uint16_t len) {
  * @brief  Manage the T4T Select answer to the reader
  *
  * @param[in]  cmdData    : pointer to the received command.
+ * @param[in]  cmdDataLen : length of the received command.
  * @param[out] rspData    : pointer to the answer to send.
  *
  * @return Answer size.
  *****************************************************************************
  */
-static uint16_t card_emulation_t4t_select(uint8_t *cmdData, uint8_t *rspData) {
+static uint16_t card_emulation_t4t_select(uint8_t *cmdData, uint16_t cmdDataLen,
+                                          uint8_t *rspData) {
   bool success = false;
   /*
    * Cmd: CLA(1) | INS(1) | P1(1) | P2(1) | Lc(1) | Data(n) | [Le(1)]
@@ -213,17 +232,18 @@ static uint16_t card_emulation_t4t_select(uint8_t *cmdData, uint8_t *rspData) {
   uint8_t fidNDEF[] = {FID_NDEF >> 8, FID_NDEF & 0xFF};
   uint8_t selectFileId[] = {0xA4, 0x00, 0x0C, 0x02, 0x00, 0x01};
 
-  if (cmd_compare(cmdData, aid, sizeof(aid))) { /* Select Appli */
+  if (cmd_compare(cmdData, cmdDataLen, aid, sizeof(aid))) { /* Select Appli */
     nState = STATE_APP_SELECTED;
     success = true;
   } else if ((nState >= STATE_APP_SELECTED) &&
-             cmd_compare(cmdData, fidCC, sizeof(fidCC))) { /* Select CC */
+             cmd_compare(cmdData, cmdDataLen, fidCC,
+                         sizeof(fidCC))) { /* Select CC */
     nState = STATE_CC_SELECTED;
     nSelectedIdx = 0;
     success = true;
   } else if ((nState >= STATE_APP_SELECTED) &&
-             (cmd_compare(cmdData, fidNDEF, sizeof(fidNDEF)) ||
-              cmd_compare(cmdData, selectFileId,
+             (cmd_compare(cmdData, cmdDataLen, fidNDEF, sizeof(fidNDEF)) ||
+              cmd_compare(cmdData, cmdDataLen, selectFileId,
                           sizeof(selectFileId)))) { /* Select NDEF */
     nState = STATE_FID_SELECTED;
     nSelectedIdx = 1;
@@ -243,18 +263,25 @@ static uint16_t card_emulation_t4t_select(uint8_t *cmdData, uint8_t *rspData) {
  * @brief  Manage the T4T Read answer to the reader
  *
  * @param[in]  cmdData    : pointer to the received command.
+ * @param[in]  cmdDataLen : length of the received command.
  * @param[out] rspData    : pointer to the answer to send.
  * @param[in]  rspDataLen : size of the answer buffer.
  *
  * @return Answer size.
  *****************************************************************************
  */
-static uint16_t card_emulation_t4t_read(uint8_t *cmdData, uint8_t *rspData,
-                                        uint16_t rspDataLen) {
+static uint16_t card_emulation_t4t_read(uint8_t *cmdData, uint16_t cmdDataLen,
+                                        uint8_t *rspData, uint16_t rspDataLen) {
   /*
    * Cmd: CLA(1) | INS(1) | P1(1).. offset inside file high | P2(1).. offset
    * inside file high | Le(1).. nBytes to read Rsp: BytesRead | SW12
    */
+  if (cmdDataLen < 5) {
+    /* Need CLA INS P1 P2 Le — truncated frame */
+    rspData[0] = (char)0x67;
+    rspData[1] = (char)0x00;
+    return 2;
+  }
   unsigned short offset = (cmdData[2] << 8) | cmdData[3];
   unsigned short toRead = cmdData[4];
   uint8_t *ppbMemory;
@@ -294,13 +321,21 @@ static uint16_t card_emulation_t4t_read(uint8_t *cmdData, uint8_t *rspData,
  *****************************************************************************
  * @brief  Manage the T4T Update answer to the reader
  *
- * @param[in]  cmdData : pointer to the received command.
- * @param[in]  rspData : pointer to the answer to send.
+ * @param[in]  cmdData    : pointer to the received command.
+ * @param[in]  cmdDataLen : length of the received command.
+ * @param[out] rspData    : pointer to the answer to send.
  *
  * @return Answer size.
  *****************************************************************************
  */
-static uint16_t card_emulation_t4t_update(uint8_t *cmdData, uint8_t *rspData) {
+static uint16_t card_emulation_t4t_update(uint8_t *cmdData, uint16_t cmdDataLen,
+                                          uint8_t *rspData) {
+  if (cmdDataLen < 5) {
+    /* Need CLA INS P1 P2 Lc — truncated frame */
+    rspData[0] = (char)0x67;
+    rspData[1] = (char)0x00;
+    return 2;
+  }
   uint32_t offset = (cmdData[2] << 8) | cmdData[3];
   uint32_t length = cmdData[4];
 
@@ -316,6 +351,13 @@ static uint16_t card_emulation_t4t_update(uint8_t *cmdData, uint8_t *rspData) {
     return 2;
   }
 
+  if (cmdDataLen < (uint32_t)(5 + length)) {
+    /* Frame too short to contain the declared Lc payload */
+    rspData[0] = (char)0x67;
+    rspData[1] = (char)0x00;
+    return 2;
+  }
+
   memcpy((ndefFile + offset), &cmdData[5], length);
 
   rspData[0] = ((char)0x90);
@@ -325,16 +367,18 @@ static uint16_t card_emulation_t4t_update(uint8_t *cmdData, uint8_t *rspData) {
 
 /**
  *****************************************************************************
- * @brief  Manage the T4T Read answer to the reader
+ * @brief  Manage the T3T Check answer to the reader
  *
  * @param[in]  cmdData    : pointer to the received command.
+ * @param[in]  cmdDataLen : length of the received command.
  * @param[out] rspData    : pointer to the answer to send.
  * @param[in]  rspDataLen : size of the answer buffer.
  *
  * @return Answer size.
  *****************************************************************************
  */
-static uint16_t card_emulation_t3t_check(uint8_t *cmdData, uint8_t *rspData,
+static uint16_t card_emulation_t3t_check(uint8_t *cmdData, uint16_t cmdDataLen,
+                                         uint8_t *rspData,
                                          uint16_t rspDataLen) {
   /*
    * Cmd: cmd | NFCID2 | NoS | Service code list | NoB | Block list
@@ -346,6 +390,10 @@ static uint16_t card_emulation_t3t_check(uint8_t *cmdData, uint8_t *rspData,
   uint32_t cnt = 0;
   uint32_t nbmax = 0;
 
+  if (cmdDataLen < T3T_MIN_CMD_LEN) {
+    return 0;
+  }
+
   /* Command response */
   rspData[idx++] = RFAL_NFCF_CMD_READ_WITHOUT_ENCRYPTION + 1;
 
@@ -379,8 +427,14 @@ static uint16_t card_emulation_t3t_check(uint8_t *cmdData, uint8_t *rspData,
   rspData[idx++] = cmdData[13];
 
   /* Retrieving block to read */
-  block = &cmdData[14];
+  block = &cmdData[T3T_MIN_CMD_LEN];
   for (cnt = 0; cnt < cmdData[13]; cnt++) {
+    /* Bounds check: need at least 1 byte to read the block list element flag */
+    if ((block - cmdData) >= cmdDataLen) {
+      rspData[idx - 3] = 0xFF;
+      rspData[idx - 2] = 0xFF;
+      return (idx - 1);
+    }
     /* TS T3T 5.6.1.5 Service Code List Order value SHALL be between 0 and NoS-1
      */
     if (((*block) & 0x0F) >= cmdData[10]) {
@@ -392,10 +446,20 @@ static uint16_t card_emulation_t3t_check(uint8_t *cmdData, uint8_t *rspData,
     /* Check block list element size */
     if (*block & 0x80) {
       /* 2-byte Block List element */
+      if ((block - cmdData) + 2 > cmdDataLen) {
+        rspData[idx - 3] = 0xFF;
+        rspData[idx - 2] = 0xFF;
+        return (idx - 1);
+      }
       blocknb[cnt] = *(block + 1);
       block += 2;
     } else {
       /* 3-byte Block List element */
+      if ((block - cmdData) + 3 > cmdDataLen) {
+        rspData[idx - 3] = 0xFF;
+        rspData[idx - 2] = 0xFF;
+        return (idx - 1);
+      }
       blocknb[cnt] = *(block + 2); /* Little Endian Format */
       blocknb[cnt] <<= 8;
       blocknb[cnt] |= *(block + 1);
@@ -433,13 +497,15 @@ static uint16_t card_emulation_t3t_check(uint8_t *cmdData, uint8_t *rspData,
  *****************************************************************************
  * @brief  Manage the T3T Update answer to the reader
  *
- * @param[in]  cmdData : pointer to the received command.
- * @param[in]  rspData : pointer to the answer to send.
+ * @param[in]  cmdData    : pointer to the received command.
+ * @param[in]  cmdDataLen : length of the received command.
+ * @param[out] rspData    : pointer to the answer to send.
  *
  * @return Answer size.
  *****************************************************************************
  */
-static uint16_t card_emulation_t3t_update(uint8_t *cmdData, uint8_t *rspData) {
+static uint16_t card_emulation_t3t_update(uint8_t *cmdData, uint16_t cmdDataLen,
+                                          uint8_t *rspData) {
   /*
    * Cmd: cmd | NFCID2 | NoS | Service code list | NoB | Block list | Block Data
    * Rsp: rsp | NFCID2 | Status Flag 1 | Status Flag 2
@@ -450,6 +516,10 @@ static uint16_t card_emulation_t3t_update(uint8_t *cmdData, uint8_t *rspData) {
   uint32_t cnt = 0;
   uint32_t nbmax = 0;
 
+  if (cmdDataLen < T3T_MIN_CMD_LEN) {
+    return 0;
+  }
+
   /* Command response */
   rspData[idx++] = RFAL_NFCF_CMD_WRITE_WITHOUT_ENCRYPTION + 1;
 
@@ -474,16 +544,32 @@ static uint16_t card_emulation_t3t_update(uint8_t *cmdData, uint8_t *rspData) {
     rspData[idx++] = 0x00;
   }
 
-  /* Retrieving block to read */
-  block = &cmdData[14];
+  /* Retrieving block list */
+  block = &cmdData[T3T_MIN_CMD_LEN];
   for (cnt = 0; cnt < cmdData[13]; cnt++) {
+    /* Bounds check: need at least 1 byte to read the block list element flag */
+    if ((block - cmdData) >= cmdDataLen) {
+      rspData[idx - 2] = 0xFF;
+      rspData[idx - 1] = 0xFF;
+      return idx;
+    }
     /* Check block list element size */
     if (*block & 0x80) {
       /* 2-byte Block List element */
+      if ((block - cmdData) + 2 > cmdDataLen) {
+        rspData[idx - 2] = 0xFF;
+        rspData[idx - 1] = 0xFF;
+        return idx;
+      }
       blocknb[cnt] = *(block + 1);
       block += 2;
     } else {
       /* 3-byte Block List element */
+      if ((block - cmdData) + 3 > cmdDataLen) {
+        rspData[idx - 2] = 0xFF;
+        rspData[idx - 1] = 0xFF;
+        return idx;
+      }
       blocknb[cnt] = *(block + 2); /* Little Endian Format */
       blocknb[cnt] <<= 8;
       blocknb[cnt] |= *(block + 1);
@@ -500,6 +586,12 @@ static uint16_t card_emulation_t3t_update(uint8_t *cmdData, uint8_t *rspData) {
   }
 
   for (cnt = 0; cnt < cmdData[13]; cnt++) {
+    /* Bounds check: need T3T_BLOCK_SIZE bytes of payload per block */
+    if ((block - cmdData) + T3T_BLOCK_SIZE > cmdDataLen) {
+      rspData[idx - 2] = 0xFF;
+      rspData[idx - 1] = 0xFF;
+      return idx;
+    }
     if (blocknb[cnt] == 0x0000) {
       /* Write information block */
       memcpy(InformationBlock, block, T3T_BLOCK_SIZE);
@@ -574,13 +666,13 @@ uint16_t card_emulation_t4t(uint8_t *rxData, uint16_t rxDataLen, uint8_t *txBuf,
     if (rxData[0] == T4T_CLA_00) {
       switch (rxData[1]) {
         case T4T_INS_SELECT:
-          return card_emulation_t4t_select(rxData, txBuf);
+          return card_emulation_t4t_select(rxData, rxDataLen, txBuf);
 
         case T4T_INS_READ:
-          return card_emulation_t4t_read(rxData, txBuf, txBufLen);
+          return card_emulation_t4t_read(rxData, rxDataLen, txBuf, txBufLen);
 
         case T4T_INS_UPDATE:
-          return card_emulation_t4t_update(rxData, txBuf);
+          return card_emulation_t4t_update(rxData, rxDataLen, txBuf);
 
         default:
           break;
@@ -619,10 +711,10 @@ uint16_t card_emulation_t3t(uint8_t *rxData, uint16_t rxDataLen, uint8_t *txBuf,
   if ((rxData != NULL) && (rxDataLen >= 4)) {
     switch (rxData[1]) {
       case RFAL_NFCF_CMD_READ_WITHOUT_ENCRYPTION:
-        return card_emulation_t3t_check(rxData, txBuf, txBufLen);
+        return card_emulation_t3t_check(rxData, rxDataLen, txBuf, txBufLen);
 
       case RFAL_NFCF_CMD_WRITE_WITHOUT_ENCRYPTION:
-        return card_emulation_t3t_update(rxData, txBuf);
+        return card_emulation_t3t_update(rxData, rxDataLen, txBuf);
 
       default:
         break;
```
