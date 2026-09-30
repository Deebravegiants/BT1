# [?] Fix crash when signing NFT transactions with no NFT information APDU received

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2022-02-09
Source: https://github.com/LedgerHQ/app-ethereum/commit/4232a8925b822d8b84f3f8a76d60fb330926ad3b
Type: security-commit

## Details
Fix crash when signing NFT transactions with no NFT information APDU received

## Patch
### src_plugins/erc1155/erc1155_ui.c
```diff
@@ -3,6 +3,8 @@
 #include "erc1155_plugin.h"
 
 static void set_approval_for_all_ui(ethQueryContractUI_t *msg, erc1155_context_t *context) {
+    uint8_t *nft_addr;
+
     switch (msg->screenIndex) {
         case 0:
             if (context->approved) {
@@ -26,7 +28,10 @@ static void set_approval_for_all_ui(ethQueryContractUI_t *msg, erc1155_context_t
             break;
         case 2:
             strlcpy(msg->title, "NFT Address", msg->titleLength);
-            getEthDisplayableAddress(msg->pluginSharedRO->txContent->destination,
+            // In case of no PROVIDE_NFT_INFO, we already have the address from the SET_PLUGIN
+            nft_addr = ((msg->item1) ? ((uint8_t *) msg->item1->nft.contractAddress)
+                                     : msg->pluginSharedRO->txContent->destination);
+            getEthDisplayableAddress(nft_addr,
                                      msg->msg,
                                      msg->msgLength,
                                      &global_sha3,
@@ -40,6 +45,8 @@ static void set_approval_for_all_ui(ethQueryContractUI_t *msg, erc1155_context_t
 }
 
 static void set_transfer_ui(ethQueryContractUI_t *msg, erc1155_context_t *context) {
+    uint8_t *nft_addr;
+
     switch (msg->screenIndex) {
         case 0:
             strlcpy(msg->title, "To", msg->titleLength);
@@ -59,7 +66,10 @@ static void set_transfer_ui(ethQueryContractUI_t *msg, erc1155_context_t *contex
             break;
         case 2:
             strlcpy(msg->title, "NFT Address", msg->titleLength);
-            getEthDisplayableAddress((uint8_t *) msg->item1->nft.contractAddress,
+            // In case of no PROVIDE_NFT_INFO, we already have the address from the SET_PLUGIN
+            nft_addr = ((msg->item1) ? ((uint8_t *) msg->item1->nft.contractAddress)
+                                     : msg->pluginSharedRO->txContent->destination);
+            getEthDisplayableAddress(nft_addr,
                                      msg->msg,
                                      msg->msgLength,
                                      &global_sha3,
@@ -85,6 +95,7 @@ static void set_transfer_ui(ethQueryContractUI_t *msg, erc1155_context_t *contex
 
 static void set_batch_transfer_ui(ethQueryContractUI_t *msg, erc1155_context_t *context) {
     char quantity_str[48];
+    uint8_t *nft_addr;
 
     switch (msg->screenIndex) {
         case 0:
@@ -105,7 +116,10 @@ static void set_batch_transfer_ui(ethQueryContractUI_t *msg, erc1155_context_t *
             break;
         case 2:
             strlcpy(msg->title, "NFT Address", msg->titleLength);
-            getEthDisplayableAddress((uint8_t *) msg->item1->nft.contractAddress,
+            // In case of no PROVIDE_NFT_INFO, we already have the address from the SET_PLUGIN
+            nft_addr = ((msg->item1) ? ((uint8_t *) msg->item1->nft.contractAddress)
+                                     : msg->pluginSharedRO->txContent->destination);
+            getEthDisplayableAddress(nft_addr,
                                      msg->msg,
                                      msg->msgLength,
                                      &global_sha3,
```

### src_plugins/erc721/erc721_ui.c
```diff
@@ -3,6 +3,8 @@
 #include "erc721_plugin.h"
 
 static void set_approval_ui(ethQueryContractUI_t *msg, erc721_context_t *context) {
+    uint8_t *nft_addr;
+
     switch (msg->screenIndex) {
         case 0:
             strlcpy(msg->title, "Allow", msg->titleLength);
@@ -22,7 +24,10 @@ static void set_approval_ui(ethQueryContractUI_t *msg, erc721_context_t *context
             break;
         case 2:
             strlcpy(msg->title, "NFT Address", msg->titleLength);
-            getEthDisplayableAddress(msg->pluginSharedRO->txContent->destination,
+            // In case of no PROVIDE_NFT_INFO, we already have the address from the SET_PLUGIN
+            nft_addr = ((msg->item1) ? ((uint8_t *) msg->item1->nft.contractAddress)
+                                     : msg->pluginSharedRO->txContent->destination);
+            getEthDisplayableAddress(nft_addr,
                                      msg->msg,
                                      msg->msgLength,
                                      &global_sha3,
@@ -51,6 +56,8 @@ static void set_approval_ui(ethQueryContractUI_t *msg, erc721_context_t *context
 }
 
 static void set_approval_for_all_ui(ethQueryContractUI_t *msg, erc721_context_t *context) {
+    uint8_t *nft_addr;
+
     switch (msg->screenIndex) {
         case 0:
             if (context->approved) {
@@ -74,7 +81,10 @@ static void set_approval_for_all_ui(ethQueryContractUI_t *msg, erc721_context_t
             break;
         case 2:
             strlcpy(msg->title, "NFT Address", msg->titleLength);
-            getEthDisplayableAddress(msg->pluginSharedRO->txContent->destination,
+            // In case of no PROVIDE_NFT_INFO, we already have the address from the SET_PLUGIN
+            nft_addr = ((msg->item1) ? ((uint8_t *) msg->item1->nft.contractAddress)
+                                     : msg->pluginSharedRO->txContent->destination);
+            getEthDisplayableAddress(nft_addr,
                                      msg->msg,
                                      msg->msgLength,
                                      &global_sha3,
@@ -96,6 +106,8 @@ static void set_approval_for_all_ui(ethQueryContractUI_t *msg, erc721_context_t
 }
 
 static void set_transfer_ui(ethQueryContractUI_t *msg, erc721_context_t *context) {
+    uint8_t *nft_addr;
+
     switch (msg->screenIndex) {
         case 0:
             strlcpy(msg->title, "To", msg->titleLength);
@@ -115,7 +127,10 @@ static void set_transfer_ui(ethQueryContractUI_t *msg, erc721_context_t *context
             break;
         case 2:
             strlcpy(msg->title, "NFT Address", msg->titleLength);
-            getEthDisplayableAddress((uint8_t *) msg->item1->nft.contractAddress,
+            // In case of no PROVIDE_NFT_INFO, we already have the address from the SET_PLUGIN
+            nft_addr = ((msg->item1) ? ((uint8_t *) msg->item1->nft.contractAddress)
+                                     : msg->pluginSharedRO->txContent->destination);
+            getEthDisplayableAddress(nft_addr,
                                      msg->msg,
                                      msg->msgLength,
                                      &global_sha3,
```
