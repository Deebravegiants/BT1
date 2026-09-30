# [?] fix: 8-bit pair counters overflow in generic clear-signing UI builder src/nbgl/ui_gcs.c

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2026-04-10
Source: https://github.com/LedgerHQ/app-ethereum/commit/d32cb3d22c6d63f3fd4d3dcadc29e6a0082f8d1b
Type: security-commit

## Details
fix: 8-bit pair counters overflow in generic clear-signing UI builder src/nbgl/ui_gcs.c

(cherry picked from commit b9327948c18b026495d004aebe52da440ffdeb05)

## Patch
### src/nbgl/ui_gcs.c
```diff
@@ -402,8 +402,9 @@ bool ui_gcs(void) {
     bool show_network;
     nbgl_contentValueExt_t *ext = NULL;
     nbgl_contentInfoList_t *infolist = NULL;
-    uint8_t nbPairs = 0;
-    uint8_t pair = 0;
+    size_t nbPairs = 0;
+    size_t pair = 0;
+    size_t table_size = 0;
     uint8_t tx_idx = 0;
     const s_tx_info *info_tx = get_current_tx_info();
 
@@ -429,22 +430,29 @@ bool ui_gcs(void) {
         return false;
     }
 
+    // Get the number of TX fields to display
+    table_size = field_table_size();
     // Contract info
     nbPairs += 1;
     // Batch transactions
     if (txContext.batch_nb_tx > 1) {
         nbPairs += txContext.batch_nb_tx;  // one page per sub-tx
     }
     // TX fields
-    nbPairs += field_table_size();
+    nbPairs += table_size;
     show_network = get_tx_chain_id() != chainConfig->chainId;
     if (show_network) {
         nbPairs += 1;
     }
     // Fees
     nbPairs += 1;
 
-    if (!ui_pairs_init(nbPairs)) {
+    if (nbPairs > UINT8_MAX) {
+        PRINTF("Error: Too many review fields: %u\n", (unsigned) nbPairs);
+        return false;
+    }
+
+    if (!ui_pairs_init((uint8_t) nbPairs)) {
         return false;
     }
 
@@ -486,11 +494,16 @@ bool ui_gcs(void) {
     pair++;
 
     // TX fields
-    for (int i = 0; i < (int) field_table_size(); ++i) {
+    for (size_t i = 0; i < table_size; ++i) {
         if ((field = get_from_field_table(i)) == NULL) {
             return false;
         }
-        if ((field->start_intent) && (txContext.batch_nb_tx > 1)) {
+        bool add_intermediate = (field->start_intent) && (txContext.batch_nb_tx > 1);
+        size_t needed = add_intermediate ? 2 : 1;
+        if (pair + needed > g_pairsList->nbPairs) {
+            return false;
+        }
+        if (add_intermediate) {
             // Batch intermediate page
             tx_idx++;
             snprintf(tmp_buf, tmp_buf_size, "%d of %d", tx_idx, txContext.batch_nb_tx);
@@ -508,9 +521,9 @@ bool ui_gcs(void) {
                 return false;
             }
         }
-
+        // Switch to the next pair
         pair++;
-        if ((field->end_intent) && (txContext.batch_nb_tx > 1)) {
+        if ((field->end_intent) && (txContext.batch_nb_tx > 1) && (pair < g_pairsList->nbPairs)) {
             // End of batch transaction : start next info on full page
             g_pairs[pair].forcePageStart = true;
         }
```
