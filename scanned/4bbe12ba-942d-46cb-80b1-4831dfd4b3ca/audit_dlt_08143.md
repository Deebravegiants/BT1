# [?] cryptonote_protocol: expand basic DoS protection

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2019-03-08
Source: https://github.com/monero-project/monero/commit/1cc61018e52893382ae110430b38d1e0bf6e5870
Type: security-commit

## Details
cryptonote_protocol: expand basic DoS protection

Count transactions as well

## Patch
### src/cryptonote_protocol/cryptonote_protocol_handler.h
```diff
@@ -52,7 +52,7 @@ PUSH_WARNINGS
 DISABLE_VS_WARNINGS(4355)
 
 #define LOCALHOST_INT 2130706433
-#define CURRENCY_PROTOCOL_MAX_BLOCKS_REQUEST_COUNT 500
+#define CURRENCY_PROTOCOL_MAX_OBJECT_REQUEST_COUNT 500
 
 namespace cryptonote
 {
```

### src/cryptonote_protocol/cryptonote_protocol_handler.inl
```diff
@@ -915,12 +915,12 @@ namespace cryptonote
   {
     MLOG_P2P_MESSAGE("Received NOTIFY_REQUEST_GET_OBJECTS (" << arg.blocks.size() << " blocks, " << arg.txs.size() << " txes)");
 
-    if (arg.blocks.size() > CURRENCY_PROTOCOL_MAX_BLOCKS_REQUEST_COUNT)
+    if (arg.blocks.size() + arg.txs.size() > CURRENCY_PROTOCOL_MAX_OBJECT_REQUEST_COUNT)
       {
         LOG_ERROR_CCONTEXT(
             "Requested objects count is too big ("
-            << arg.blocks.size() << ") expected not more then "
-            << CURRENCY_PROTOCOL_MAX_BLOCKS_REQUEST_COUNT);
+            << arg.blocks.size() + arg.txs.size() << ") expected not more then "
+            << CURRENCY_PROTOCOL_MAX_OBJECT_REQUEST_COUNT);
         drop_connection(context, false, false);
         return 1;
       }
```
