# [?] cryptonote_protocol_handler: prevent potential DoS

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2019-03-09
Source: https://github.com/monero-project/monero/commit/8f66b7053a8e4521fdd68c1d74718e73345fb158
Type: security-commit

## Details
cryptonote_protocol_handler: prevent potential DoS

Essentially, one can send such a large amount of IDs that core exhausts
all free memory. This issue can theoretically be exploited using very
large CN blockchains, such as Monero.

This is a partial fix. Thanks and credit given to CryptoNote author
'cryptozoidberg' for collaboration and the fix. Also thanks to
'moneromooo'. Referencing HackerOne report #506595.

## Patch
### src/cryptonote_protocol/cryptonote_protocol_handler.h
```diff
@@ -52,6 +52,7 @@ PUSH_WARNINGS
 DISABLE_VS_WARNINGS(4355)
 
 #define LOCALHOST_INT 2130706433
+#define CURRENCY_PROTOCOL_MAX_BLOCKS_REQUEST_COUNT 500
 
 namespace cryptonote
 {
```

### src/cryptonote_protocol/cryptonote_protocol_handler.inl
```diff
@@ -914,6 +914,17 @@ namespace cryptonote
   int t_cryptonote_protocol_handler<t_core>::handle_request_get_objects(int command, NOTIFY_REQUEST_GET_OBJECTS::request& arg, cryptonote_connection_context& context)
   {
     MLOG_P2P_MESSAGE("Received NOTIFY_REQUEST_GET_OBJECTS (" << arg.blocks.size() << " blocks, " << arg.txs.size() << " txes)");
+
+    if (arg.blocks.size() > CURRENCY_PROTOCOL_MAX_BLOCKS_REQUEST_COUNT)
+      {
+        LOG_ERROR_CCONTEXT(
+            "Requested objects count is too big ("
+            << arg.blocks.size() << ") expected not more then "
+            << CURRENCY_PROTOCOL_MAX_BLOCKS_REQUEST_COUNT);
+        drop_connection(context, false, false);
+        return 1;
+      }
+
     NOTIFY_RESPONSE_GET_OBJECTS::request rsp;
     if(!m_core.handle_get_objects(arg, rsp, context))
     {
```
