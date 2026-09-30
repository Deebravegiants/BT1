# [?] [V-375] fix(erc20): validate extra-data offset bounds to prevent OOB memmove

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2026-08-27
Source: https://github.com/LedgerHQ/app-ethereum/commit/45facb7c8965712420b2e86b7438ea5ad1a981e2
Type: security-commit

## Details
[V-375] fix(erc20): validate extra-data offset bounds to prevent OOB memmove

## Patch
### src/plugins/erc20/erc20_plugin.c
```diff
@@ -99,13 +99,15 @@ void erc20_plugin_call(eth_plugin_msg_t message, void *parameters) {
                     msg->result = ETH_PLUGIN_RESULT_OK;
                     break;
 
-                default:
-                    if (msg->parameterOffset <= CALLDATA_SELECTOR_SIZE + CALLDATA_CHUNK_SIZE +
-                                                    (MAX_EXTRA_DATA_CHUNKS * CALLDATA_CHUNK_SIZE)) {
+                default: {
+                    const uint32_t extra_data_base =
+                        CALLDATA_SELECTOR_SIZE + (CALLDATA_CHUNK_SIZE * 2);
+                    if ((msg->parameterOffset >= extra_data_base) &&
+                        (msg->parameterOffset <= extra_data_base +
+                                                     sizeof(context->extra_data) -
+                                                     CALLDATA_CHUNK_SIZE)) {
                         // store extra data for possible later use
-                        size_t extra_data_offset =
-                            msg->parameterOffset -
-                            (CALLDATA_SELECTOR_SIZE + (CALLDATA_CHUNK_SIZE * 2));
+                        size_t extra_data_offset = msg->parameterOffset - extra_data_base;
                         memmove(context->extra_data + extra_data_offset,
                                 msg->parameter,
                                 CALLDATA_CHUNK_SIZE);
@@ -122,6 +124,7 @@ void erc20_plugin_call(eth_plugin_msg_t message, void *parameters) {
                         msg->result = ETH_PLUGIN_RESULT_ERROR;
                     }
                     break;
+                }
             }
         } break;
 
```
