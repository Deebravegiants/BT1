# [?] Merge pull request from GHSA-7hmg-5627-mv35

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2023-04-24
Source: https://github.com/LedgerHQ/app-ethereum/commit/2a095bfc936ea5016529abe5720bb8b64301ef38
Type: security-commit

## Details
Merge pull request from GHSA-7hmg-5627-mv35

Fix finalizeParsing()

## Patch
### src/eth_plugin_handler.h
```diff
@@ -31,6 +31,4 @@ eth_plugin_result_t eth_plugin_perform_init(uint8_t *contractAddress,
 // NULL for cached address, or base contract address
 eth_plugin_result_t eth_plugin_call(int method, void *parameter);
 
-void plugin_ui_start(void);
-
 #endif  // _ETH_PLUGIN_HANDLER_H_
```

### src/eth_plugin_ui.c
```diff
@@ -1,11 +0,0 @@
-#include "shared_context.h"
-#include "eth_plugin_handler.h"
-#include "ux.h"
-#include "feature_signTx.h"
-
-void plugin_ui_start() {
-    dataContext.tokenContext.pluginUiState = PLUGIN_UI_OUTSIDE;
-    dataContext.tokenContext.pluginUiCurrentItem = 0;
-
-    ux_approve_tx(true);
-}
```

### src/shared_context.h
```diff
@@ -175,7 +175,7 @@ typedef enum {
 
 #define NETWORK_STRING_MAX_SIZE 16
 
-typedef struct txStringProperties_t {
+typedef struct txStringProperties_s {
     char fullAddress[43];
     char fullAmount[79];  // 2^256 is 78 digits long
     char maxFee[50];
@@ -190,7 +190,7 @@ typedef struct txStringProperties_t {
 #endif
 #define SHARED_CTX_FIELD_2_SIZE 40
 
-typedef struct strDataTmp_t {
+typedef struct strDataTmp_s {
     char tmp[SHARED_CTX_FIELD_1_SIZE];
     char tmp2[SHARED_CTX_FIELD_2_SIZE];
 } strDataTmp_t;
```

### src_common/uint256.c
```diff
@@ -230,18 +230,20 @@ bool tostring256(const uint256_t *const number,
     UPPER(LOWER(base)) = 0;
     LOWER(LOWER(base)) = baseParam;
     uint32_t offset = 0;
-    if ((baseParam < 2) || (baseParam > 16)) {
+    if ((outLength == 0) || (baseParam < 2) || (baseParam > 16)) {
         return false;
     }
     do {
-        if (offset > (outLength - 1)) {
-            return false;
-        }
         divmod256(&rDiv, &base, &rDiv, &rMod);
         out[offset++] = HEXDIGITS[(uint8_t) LOWER(LOWER(rMod))];
-    } while (!zero256(&rDiv));
+    } while (!zero256(&rDiv) && (offset < outLength));
 
-    if (offset > (outLength - 1)) {
+    if (offset == outLength) {  // destination buffer too small
+        if (outLength > 3) {
+            strcpy(out, "...");
+        } else {
+            out[0] = '\0';
+        }
         return false;
     }
 
```

### src_features/signTx/logic_signTx.c
```diff
@@ -9,6 +9,7 @@
 #include "ethUtils.h"
 #include "common_ui.h"
 #include "ui_callbacks.h"
+#include <ctype.h>
 
 #define ERR_SILENT_MODE_CHECK_FAILED 0x6001
 
@@ -170,26 +171,6 @@ customStatus_e customProcessor(txContext_t *context) {
     return CUSTOM_NOT_HANDLED;
 }
 
-void to_uppercase(char *str, unsigned char size) {
-    for (unsigned char i = 0; i < size && str[i] != 0; i++) {
-        str[i] = str[i] >= 'a' ? str[i] - ('a' - 'A') : str[i];
-    }
-}
-
-void compareOrCopy(char *preapproved_string, size_t size, char *parsed_string, bool silent_mode) {
-    if (silent_mode) {
-        /* ETH address are not fundamentally case sensitive but might
-        have some for checksum purpose, so let's get rid of these diffs */
-        to_uppercase(preapproved_string, strlen(preapproved_string));
-        to_uppercase(parsed_string, strlen(parsed_string));
-        if (memcmp(preapproved_string, parsed_string, strlen(preapproved_string))) {
-            THROW(ERR_SILENT_MODE_CHECK_FAILED);
-        }
-    } else {
-        strlcpy(preapproved_string, parsed_string, size);
-    }
-}
-
 void reportFinalizeError(bool direct) {
     reset_app_context();
     if (direct) {
@@ -200,20 +181,20 @@ void reportFinalizeError(bool direct) {
     }
 }
 
-// Convert `BEgasPrice` and `BEgasLimit` to Uint256 and then stores the multiplication of both in
-// `output`.
-static void computeFees(txInt256_t *BEgasPrice, txInt256_t *BEgasLimit, uint256_t *output) {
-    uint256_t gasPrice = {0};
-    uint256_t gasLimit = {0};
-
-    PRINTF("Gas price %.*H\n", BEgasPrice->length, BEgasPrice->value);
-    PRINTF("Gas limit %.*H\n", BEgasLimit->length, BEgasLimit->value);
-    convertUint256BE(BEgasPrice->value, BEgasPrice->length, &gasPrice);
-    convertUint256BE(BEgasLimit->value, BEgasLimit->length, &gasLimit);
-    mul256(&gasPrice, &gasLimit, output);
+static void address_to_string(uint8_t *in,
+                              size_t in_len,
+                              char *out,
+                              size_t out_len,
+                              cx_sha3_t *sha3,
+                              uint64_t chainId) {
+    if (in_len != 0) {
+        getEthDisplayableAddress(in, out, out_len, sha3, chainId);
+    } else {
+        strlcpy(out, "Contract", out_len);
+    }
 }
 
-static void feesToString(uint256_t *rawFee, char *displayBuffer, uint32_t displayBufferSize) {
+static void raw_fee_to_string(uint256_t *rawFee, char *displayBuffer, uint32_t displayBufferSize) {
     const char *feeTicker = get_network_ticker();
     uint8_t tickerOffset = 0;
     uint32_t i;
@@ -255,32 +236,40 @@ static void feesToString(uint256_t *rawFee, char *displayBuffer, uint32_t displa
 }
 
 // Compute the fees, transform it to a string, prepend a ticker to it and copy everything to
-// `displayBuffer`.
-void prepareAndCopyFees(txInt256_t *BEGasPrice,
-                        txInt256_t *BEGasLimit,
-                        char *displayBuffer,
-                        uint32_t displayBufferSize) {
+// `displayBuffer` output
+static void max_transaction_fee_to_string(const txInt256_t *BEGasPrice,
+                                          const txInt256_t *BEGasLimit,
+                                          char *displayBuffer,
+                                          uint32_t displayBufferSize) {
+    // Use temporary variables to convert values to uint256_t
+    uint256_t gasPrice = {0};
+    uint256_t gasLimit = {0};
+    // Use temporary variable to store the result of the operation in uint256_t
     uint256_t rawFee = {0};
-    computeFees(BEGasPrice, BEGasLimit, &rawFee);
-    feesToString(&rawFee, displayBuffer, displayBufferSize);
+
+    PRINTF("Gas price %.*H\n", BEGasPrice->length, BEGasPrice->value);
+    PRINTF("Gas limit %.*H\n", BEGasLimit->length, BEGasLimit->value);
+    convertUint256BE(BEGasPrice->value, BEGasPrice->length, &gasPrice);
+    convertUint256BE(BEGasLimit->value, BEGasLimit->length, &gasLimit);
+    mul256(&gasPrice, &gasLimit, &rawFee);
+    raw_fee_to_string(&rawFee, displayBuffer, displayBufferSize);
 }
 
-void prepareFeeDisplay() {
-    prepareAndCopyFees(&tmpContent.txContent.gasprice,
-                       &tmpContent.txContent.startgas,
-                       strings.common.maxFee,
-                       sizeof(strings.common.maxFee));
+static void nonce_to_string(const txInt256_t *nonce, char *out, size_t out_size) {
+    uint256_t nonce_uint256;
+    convertUint256BE(nonce->value, nonce->length, &nonce_uint256);
+    tostring256(&nonce_uint256, 10, out, out_size);
 }
 
-void prepareNetworkDisplay() {
+static void get_network_as_string(char *out, size_t out_size) {
     const char *name = get_network_name();
     if (name == NULL) {
         // No network name found so simply copy the chain ID as the network name.
         uint64_t chain_id = get_chain_id();
-        u64_to_string(chain_id, strings.common.network_name, sizeof(strings.common.network_name));
+        u64_to_string(chain_id, out, out_size);
     } else {
         // Network name found, simply copy it.
-        strlcpy(strings.common.network_name, name, sizeof(strings.common.network_name));
+        strlcpy(out, name, out_size);
     }
 }
 
@@ -305,12 +294,27 @@ static void get_public_key(uint8_t *out, uint8_t outLength) {
     getEthAddressFromKey(&publicKey, out, &global_sha3);
 }
 
+/* Local implmentation of strncasecmp, workaround of the segfaulting base implem
+ * Remove once strncasecmp is fixed
+ */
+static int strcasecmp_workaround(const char *str1, const char *str2) {
+    unsigned char c1, c2;
+    do {
+        c1 = *str1++;
+        c2 = *str2++;
+        if (toupper(c1) != toupper(c2)) {
+            return toupper(c1) - toupper(c2);
+        }
+    } while (c1 != '\0');
+    return 0;
+}
+
 void finalizeParsing(bool direct) {
     char displayBuffer[50];
     uint8_t decimals = WEI_TO_ETHER;
     const char *ticker = get_network_ticker();
     ethPluginFinalize_t pluginFinalize;
-    bool genericUI = true;
+    bool use_standard_UI = true;
 
     // Verify the chain
     if (chainConfig->chainId != ETHEREUM_MAINNET_CHAINID) {
@@ -335,7 +339,6 @@ void finalizeParsing(bool direct) {
 
     // Finalize the plugin handling
     if (dataContext.tokenContext.pluginStatus >= ETH_PLUGIN_RESULT_SUCCESSFUL) {
-        genericUI = false;
         eth_plugin_prepare_finalize(&pluginFinalize);
 
         uint8_t msg_sender[ADDRESS_LENGTH] = {0};
@@ -381,14 +384,17 @@ void finalizeParsing(bool direct) {
             // Handle the right interface
             switch (pluginFinalize.uiType) {
                 case ETH_UI_TYPE_GENERIC:
+                    // Use the dedicated ETH plugin UI
+                    use_standard_UI = false;
                     tmpContent.txContent.dataPresent = false;
                     // Add the number of screens + the number of additional screens to get the total
                     // number of screens needed.
                     dataContext.tokenContext.pluginUiMaxItems =
                         pluginFinalize.numScreens + pluginProvideInfo.additionalScreens;
                     break;
                 case ETH_UI_TYPE_AMOUNT_ADDRESS:
-                    genericUI = true;
+                    // Use the standard ETH UI as this plugin uses the amount/address UI
+                    use_standard_UI = true;
                     tmpContent.txContent.dataPresent = false;
                     if ((pluginFinalize.amount == NULL) || (pluginFinalize.address == NULL)) {
                         PRINTF("Incorrect amount/address set by plugin\n");
@@ -413,11 +419,15 @@ void finalizeParsing(bool direct) {
                         return;
                     }
             }
-        } else {
-            genericUI = true;
         }
     }
 
+    // User has just validated a swap but ETH received apdus about a non standard plugin / contract
+    if (called_from_swap && !use_standard_UI) {
+        PRINTF("ERR_SILENT_MODE_CHECK_FAILED, called_from_swap\n");
+        THROW(ERR_SILENT_MODE_CHECK_FAILED);
+    }
+
     if (tmpContent.txContent.dataPresent && !N_storage.dataAllowed) {
         reportFinalizeError(direct);
         ui_warning_contract_data();
@@ -426,66 +436,94 @@ void finalizeParsing(bool direct) {
         }
     }
 
-    // Prepare destination address to display
-    if (genericUI) {
-        if (tmpContent.txContent.destinationLength != 0) {
-            getEthDisplayableAddress(tmpContent.txContent.destination,
-                                     displayBuffer,
-                                     sizeof(displayBuffer),
-                                     &global_sha3,
-                                     chainConfig->chainId);
-            compareOrCopy(strings.common.fullAddress,
-                          sizeof(strings.common.fullAddress),
+    // Prepare destination address and amount to display
+    if (use_standard_UI) {
+        // Format the address in a temporary buffer, if in swap case compare it with validated
+        // address, else commit it
+        address_to_string(tmpContent.txContent.destination,
+                          tmpContent.txContent.destinationLength,
                           displayBuffer,
-                          called_from_swap);
+                          sizeof(displayBuffer),
+                          &global_sha3,
+                          chainConfig->chainId);
+        if (called_from_swap) {
+            // Ensure the values are the same that the ones that have been previously validated
+            if (strcasecmp_workaround(strings.common.fullAddress, displayBuffer) != 0) {
+                PRINTF("ERR_SILENT_MODE_CHECK_FAILED, address check failed\n");
+                THROW(ERR_SILENT_MODE_CHECK_FAILED);
+            }
         } else {
-            strcpy(strings.common.fullAddress, "Contract");
+            strlcpy(strings.common.fullAddress, displayBuffer, sizeof(strings.common.fullAddress));
         }
-    }
+        PRINTF("Address displayed: %s\n", strings.common.fullAddress);
 
-    // Prepare amount to display
-    if (genericUI) {
+        // Format the amount in a temporary buffer, if in swap case compare it with validated
+        // amount, else commit it
         amountToString(tmpContent.txContent.value.value,
                        tmpContent.txContent.value.length,
                        decimals,
                        ticker,
                        displayBuffer,
                        sizeof(displayBuffer));
-        compareOrCopy(strings.common.fullAmount,
-                      sizeof(strings.common.fullAmount),
-                      displayBuffer,
-                      called_from_swap);
+        if (called_from_swap) {
+            // Ensure the values are the same that the ones that have been previously validated
+            if (strcmp(strings.common.fullAmount, displayBuffer) != 0) {
+                PRINTF("ERR_SILENT_MODE_CHECK_FAILED, amount check failed\n");
+                THROW(ERR_SILENT_MODE_CHECK_FAILED);
+            }
+        } else {
+            strlcpy(strings.common.fullAmount, displayBuffer, sizeof(strings.common.fullAmount));
+        }
+        PRINTF("Amount displayed: %s\n", strings.common.fullAmount);
     }
 
-    // Prepare nonce to display
-    uint256_t nonce;
-    convertUint256BE(tmpContent.txContent.nonce.value, tmpContent.txContent.nonce.length, &nonce);
-    tostring256(&nonce, 10, displayBuffer, sizeof(displayBuffer));
-    strlcpy(strings.common.nonce, displayBuffer, sizeof(strings.common.nonce));
+    // Compute the max fee in a temporary buffer, if in swap case compare it with validated max fee,
+    // else commit it
+    max_transaction_fee_to_string(&tmpContent.txContent.gasprice,
+                                  &tmpContent.txContent.startgas,
+                                  displayBuffer,
+                                  sizeof(displayBuffer));
+    if (called_from_swap) {
+        // Ensure the values are the same that the ones that have been previously validated
+        if (strcmp(strings.common.maxFee, displayBuffer) != 0) {
+            PRINTF("ERR_SILENT_MODE_CHECK_FAILED, fees check failed\n");
+            THROW(ERR_SILENT_MODE_CHECK_FAILED);
+        }
+    } else {
+        strlcpy(strings.common.maxFee, displayBuffer, sizeof(strings.common.maxFee));
+    }
 
-    // Compute maximum fee
-    prepareFeeDisplay();
     PRINTF("Fees displayed: %s\n", strings.common.maxFee);
 
+    // Prepare nonce to display
+    nonce_to_string(&tmpContent.txContent.nonce,
+                    strings.common.nonce,
+                    sizeof(strings.common.nonce));
+    PRINTF("Nonce: %s\n", strings.common.nonce);
+
     // Prepare chainID field
-    prepareNetworkDisplay();
+    get_network_as_string(strings.common.network_name, sizeof(strings.common.network_name));
     PRINTF("Network: %s\n", strings.common.network_name);
 
-    bool no_consent;
+    bool no_consent_check;
 
-    no_consent = called_from_swap;
+    // If called from swap, the user as already validated a standard transaction
+    // We have already checked the fields of this transaction above
+    no_consent_check = called_from_swap && use_standard_UI;
 
 #ifdef NO_CONSENT
-    no_consent = true;
+    no_consent_check = true;
 #endif  // NO_CONSENT
 
-    if (no_consent) {
+    if (no_consent_check) {
         io_seproxyhal_touch_tx_ok(NULL);
     } else {
-        if (genericUI) {
+        if (use_standard_UI) {
             ux_approve_tx(false);
         } else {
-            plugin_ui_start();
+            dataContext.tokenContext.pluginUiState = PLUGIN_UI_OUTSIDE;
+            dataContext.tokenContext.pluginUiCurrentItem = 0;
+            ux_approve_tx(true);
         }
     }
 }
```

### tests/speculos/test_sign_cmd.py
```diff
@@ -619,7 +619,7 @@ def test_sign_blind_and_nonce_display(cmd):
 
     transaction = Transaction(
         txType=0xEB,
-        nonce=2**64-1,
+        nonce=1844674,
         gasPrice=0x0306dc4200,
         gasLimit=0x5208,
         to="0x5a321744667052affa8386ed49e00ef223cbffc3",
@@ -699,6 +699,6 @@ def test_sign_blind_and_nonce_display(cmd):
 
     v, r, s = result
 
-    assert v == 0x25 # 37
-    assert r.hex() == "737c07042022d37286216312d62163c4238536d82c5b45937ce9fbf259d11b7d"
-    assert s.hex() == "5604485e0cf37e465a84290eb26a18e40a430f1b0fda184c56b2c3a51ada2e6c"
+    assert v == 0x26 # 38
+    assert r.hex() == "c8d7cd5c1711ea1af7da048d15d1a95fc9347d4622afa11f32320d73384984d1"
+    assert s.hex() == "3165ca0a27f565e1a87560ed3d3a144c4ac9732370428da5e6952e93659f6ac2"
```
