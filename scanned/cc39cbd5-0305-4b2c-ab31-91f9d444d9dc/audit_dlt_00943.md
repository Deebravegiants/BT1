# [?] fix: Bound MAP_ENTRY descriptor list to prevent memory pool DoS

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2026-05-12
Source: https://github.com/LedgerHQ/app-ethereum/commit/ce1915487b6a82f6c1ee6138bd7aa870645ea429
Type: security-commit

## Details
fix: Bound MAP_ENTRY descriptor list to prevent memory pool DoS

verify_map_entry_struct() appended every validly-signed map entry to
g_map_entry_list without bound. The list is cleared on
reset_app_context() between transactions, so the growth isn't
permanent, but a host with N legitimately-signed descriptors can call
INS_PROVIDE_MAP_ENTRY repeatedly during a single signing flow and
exhaust the shared app-memory pool, denying allocation to other
features (trusted_name, enum_value, safe_account, gating, GCS).

Cap the list at MAX_MAP_ENTRIES (32). 32 distinct
(chain, contract, selector, id, key) tuples is well above realistic
per-transaction clear-signing needs while keeping the worst-case
footprint around ~3.5 KB.

This only addresses the DoS component of the finding. Replay
protection (binding the descriptor to a per-session challenge in its
signed TLV) requires a backend payload change and is left out of
scope.

## Patch
### src/features/provide_map_entry/map_entry.c
```diff
@@ -13,6 +13,11 @@
 
 #define STRUCT_VERSION 0x01
 
+// Cap on accepted map entries to bound the shared app-memory pool. Map entries
+// are scoped to one transaction (cleared by reset_app_context), so this only
+// needs to cover the largest legitimate per-tx use, not aggregate session use.
+#define MAX_MAP_ENTRIES 32
+
 static s_map_entry *g_map_entry_list = NULL;
 
 static bool handle_version(const tlv_data_t *data, s_map_entry_ctx *context) {
@@ -137,6 +142,10 @@ bool verify_map_entry_struct(const s_map_entry_ctx *context) {
         PRINTF("Error: Signature verification failed for MAP_ENTRY descriptor!\n");
         return false;
     }
+    if (flist_size((flist_node_t **) &g_map_entry_list) >= MAX_MAP_ENTRIES) {
+        PRINTF("Error: MAP_ENTRY list cap reached (%d)\n", MAX_MAP_ENTRIES);
+        return false;
+    }
     if ((entry = APP_MEM_ALLOC(sizeof(*entry))) == NULL) {
         PRINTF("Error: Not enough memory for MAP_ENTRY!\n");
         return false;
```
