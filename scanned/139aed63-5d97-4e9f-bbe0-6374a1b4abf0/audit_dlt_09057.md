# [?] Fix 'use-after-free' or 'double-free' issues

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2026-04-01
Source: https://github.com/LedgerHQ/app-ethereum/commit/601c8286ee4854c01609a0c31461490ae99d67dd
Type: security-commit

## Details
Fix 'use-after-free' or 'double-free' issues

## Patch
### src/features/generic_tx_parser/tx_ctx.c
```diff
@@ -88,6 +88,9 @@ static void delete_tx_ctx(s_tx_ctx *node) {
         delete_tx_info(node->tx_info);
     }
     if (node->calldata != NULL) {
+        if (g_parked_calldata == node->calldata) {
+            g_parked_calldata = NULL;
+        }
         calldata_delete(node->calldata);
     }
     APP_MEM_FREE(node);
@@ -165,23 +168,29 @@ static bool process_empty_tx(const s_tx_ctx *tx_ctx) {
 }
 
 bool process_empty_txs_before(void) {
-    for (list_node_t *tmp = ((list_node_t *) g_tx_ctx_current)->prev;
-         (tmp != NULL) && (((s_tx_ctx *) tmp)->calldata == NULL);
-         tmp = tmp->prev) {
+    list_node_t *tmp = ((list_node_t *) g_tx_ctx_current)->prev;
+    while ((tmp != NULL) && (((s_tx_ctx *) tmp)->calldata == NULL)) {
+        // process_empty_tx calls list_remove + delete_tx_ctx, which frees tmp.
+        // Ensure reading tmp->prev before the call to avoid use-after-free.
+        list_node_t *prev = tmp->prev;
         if (!process_empty_tx((s_tx_ctx *) tmp)) {
             return false;
         }
+        tmp = prev;
     }
     return true;
 }
 
 bool process_empty_txs_after(void) {
-    for (flist_node_t *tmp = ((flist_node_t *) g_tx_ctx_current)->next;
-         (tmp != NULL) && (((s_tx_ctx *) tmp)->calldata == NULL);
-         tmp = tmp->next) {
+    flist_node_t *tmp = ((flist_node_t *) g_tx_ctx_current)->next;
+    while ((tmp != NULL) && (((s_tx_ctx *) tmp)->calldata == NULL)) {
+        // process_empty_tx calls list_remove + delete_tx_ctx, which frees tmp.
+        // Ensure reading tmp->next before the call to avoid use-after-free.
+        flist_node_t *next = tmp->next;
         if (!process_empty_tx((s_tx_ctx *) tmp)) {
             return false;
         }
+        tmp = next;
     }
     return true;
 }
@@ -291,6 +300,15 @@ bool tx_ctx_init(s_calldata *calldata,
         return false;
     }
     list_push_back((list_node_t **) &g_tx_ctx_list, (list_node_t *) node);
+
+    // Ownership of the calldata has been transferred to the node.
+    // Clear g_parked_calldata now so callers cannot double-free it if we return
+    // false below (e.g. when field_table_init fails after the node is in the list
+    // and will be freed by tx_ctx_cleanup via delete_tx_ctx).
+    if (g_parked_calldata == calldata) {
+        g_parked_calldata = NULL;
+    }
+
     if ((appState == APP_STATE_SIGNING_TX) && (node == g_tx_ctx_list)) {
         return field_table_init();
     }
@@ -302,5 +320,8 @@ void gcs_cleanup(void) {
     field_table_cleanup();
     tx_ctx_cleanup();
     // just in case
-    if (g_parked_calldata != NULL) calldata_delete(g_parked_calldata);
+    if (g_parked_calldata != NULL) {
+        calldata_delete(g_parked_calldata);
+        g_parked_calldata = NULL;
+    }
 }
```

### src/features/provide_network_info/network_info.c
```diff
@@ -417,11 +417,14 @@ void network_info_cleanup(network_info_t *network) {
         // Remove from list
         flist_remove((flist_node_t **) &g_dynamic_network_list, (flist_node_t *) network, NULL);
 
-        // Free the network info structure
-        APP_MEM_FREE_AND_NULL((void **) &network);
+        // Save address before freeing to check if it's the last added network
+        bool was_last = (g_last_added_network == network);
+
+        // Free the network info structure (local parameter — no need to null it)
+        APP_MEM_FREE((void *) network);
 
         // Reset last added network pointer if it was this network
-        if (g_last_added_network == network) {
+        if (was_last) {
             g_last_added_network = NULL;
             // Also cleanup temporary buffers associated with this network
             clear_icon();
```
