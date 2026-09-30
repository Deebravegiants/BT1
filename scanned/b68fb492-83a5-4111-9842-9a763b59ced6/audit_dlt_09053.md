# [?] fix: Integer wrap in external-plugin review pair count causes out-of-bounds writes in ui_approve_tx

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2026-04-28
Source: https://github.com/LedgerHQ/app-ethereum/commit/5e3c57805b0ca7562e9afcaaf7123faf4ca586dc
Type: security-commit

## Details
fix: Integer wrap in external-plugin review pair count causes out-of-bounds writes in ui_approve_tx

(cherry picked from commit 77f9112a6fdc183522a4d14f2ec66f0bf08e2a75)

## Patch
### src/features/sign_tx/logic_sign_tx.c
```diff
@@ -369,14 +369,22 @@ __attribute__((noinline)) static uint16_t finalize_parsing_helper(const txContex
             PRINTF("pluginFinalize.result %d successful\n", pluginFinalize.result);
             // Handle the right interface
             switch (pluginFinalize.uiType) {
-                case ETH_UI_TYPE_GENERIC:
+                case ETH_UI_TYPE_GENERIC: {
+                    size_t total_items = (size_t) pluginFinalize.numScreens +
+                                         (size_t) pluginProvideInfo.additionalScreens;
+                    if (total_items > MAX_PLUGIN_UI_ITEMS) {
+                        PRINTF("Too many plugin screens requested\n");
+                        report_finalize_error();
+                        error = SWO_NO_RESPONSE;
+                        goto end;
+                    }
                     // Use the dedicated ETH plugin UI
                     tmpContent.txContent.dataPresent = false;
                     // Add the number of screens + the number of additional screens to get the total
                     // number of screens needed.
-                    dataContext.tokenContext.pluginUiMaxItems =
-                        pluginFinalize.numScreens + pluginProvideInfo.additionalScreens;
+                    dataContext.tokenContext.pluginUiMaxItems = (uint8_t) total_items;
                     break;
+                }
 
                 // TODO: needs to be removed from the plugin SDK altogether
                 case ETH_UI_TYPE_AMOUNT_ADDRESS:
```

### src/nbgl/ui_approve_tx.c
```diff
@@ -129,6 +129,9 @@ static bool setTagValuePairs(bool displayNetwork, bool fromPlugin) {
         for (pairIndex = 0; pairIndex < dataContext.tokenContext.pluginUiMaxItems; pairIndex++) {
             // for the next dataContext.tokenContext.pluginUiMaxItems items, get tag/value from
             // plugin_ui_get_item_internal()
+            if (nbPairs >= g_pairsList->nbPairs) {
+                return false;
+            }
             dataContext.tokenContext.pluginUiCurrentItem = pairIndex;
             if (!plugin_ui_get_item_internal((uint8_t *) plugin_buffers[counter].title,
                                              TAG_MAX_LEN,
@@ -250,8 +253,8 @@ static bool setTagValuePairs(bool displayNetwork, bool fromPlugin) {
  * transaction
  * @return The number of g_pairs to display
  */
-static uint8_t getNbPairs(bool displayNetwork, bool fromPlugin) {
-    uint8_t nbPairs = 0;
+static size_t getNbPairs(bool displayNetwork, bool fromPlugin) {
+    size_t nbPairs = 0;
 
     // Setup data to display
     if (fromPlugin) {
@@ -310,7 +313,7 @@ static uint8_t getNbPairs(bool displayNetwork, bool fromPlugin) {
 static bool ux_init(bool fromPlugin, uint8_t title_len, uint8_t finish_len) {
     uint64_t chain_id = 0;
     uint16_t buf_size = 0;
-    uint8_t nbPairs = 0;
+    size_t nbPairs = 0;
     bool displayNetwork = false;
 
     chain_id = get_tx_chain_id();
@@ -319,9 +322,13 @@ static bool ux_init(bool fromPlugin, uint8_t title_len, uint8_t finish_len) {
     }
     // Compute the number of g_pairs to display
     nbPairs = getNbPairs(displayNetwork, fromPlugin);
+    if (nbPairs > UINT8_MAX) {
+        PRINTF("Error: Too many review pairs: %u\n", (unsigned) nbPairs);
+        goto error;
+    }
 
     // Initialize the buffers
-    if (!ui_pairs_init(nbPairs)) {
+    if (!ui_pairs_init((uint8_t) nbPairs)) {
         // Initialization failed, cleanup and return
         goto error;
     }
```

### src/shared_context.h
```diff
@@ -9,6 +9,12 @@
 
 #define PLUGIN_ID_LENGTH 30
 
+// Maximum number of plugin-driven items that can be added to the transaction review.
+// The review builder counts pluginUiMaxItems plus up to 3 fixed pairs (From, Network,
+// Max fees) into a uint8_t (g_pairsList->nbPairs and the cast at ui_pairs_init).
+// Bound the source so the sum never overflows the 8-bit pair counter.
+#define MAX_PLUGIN_UI_ITEMS (UINT8_MAX - 3)
+
 // Address length
 #define ADDRESS_LENGTH_STR     ((ADDRESS_LENGTH * 2) + 1)  // 2 hex chars per byte + '\0'
 #define ADDRESS_LENGTH_HEX_STR (ADDRESS_LENGTH_STR + 2)    // with '0x' prefix
```
