# [?] Fix overflow on amount formatting in ERC20 & ETH2 internal plugins

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2024-10-30
Source: https://github.com/LedgerHQ/app-ethereum/commit/0fc44f8585b0d986a1a10754a3348531769aaa8a
Type: security-commit

## Details
Fix overflow on amount formatting in ERC20 & ETH2 internal plugins

## Patch
### src_plugins/erc20/erc20_plugin.c
```diff
@@ -189,7 +189,7 @@ void erc20_plugin_call(int message, void *parameters) {
                                             context->decimals,
                                             context->ticker,
                                             msg->msg,
-                                            100)) {
+                                            msg->msgLength)) {
                             msg->result = ETH_PLUGIN_RESULT_ERROR;
                             break;
                         }
```

### src_plugins/eth2/eth2_plugin.c
```diff
@@ -206,7 +206,7 @@ void eth2_plugin_call(int message, void *parameters) {
                                         decimals,
                                         ticker,
                                         msg->msg,
-                                        100)) {
+                                        msg->msgLength)) {
                         msg->result = ETH_PLUGIN_RESULT_ERROR;
                         break;
                     }
```
