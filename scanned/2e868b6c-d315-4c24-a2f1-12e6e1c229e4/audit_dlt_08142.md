# [?] cryptonote_protocol: fix another potential P2P DoS

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2019-03-09
Source: https://github.com/monero-project/monero/commit/68ad548193134c111c75382939f7d77dbd15ad3f
Type: security-commit

## Details
cryptonote_protocol: fix another potential P2P DoS

When asking for txes in a fluffy transaction, one might ask
for the same (large) tx many times

## Patch
### src/cryptonote_protocol/cryptonote_protocol_handler.inl
```diff
@@ -809,12 +809,27 @@ namespace cryptonote
     NOTIFY_NEW_FLUFFY_BLOCK::request fluffy_response;
     fluffy_response.b.block = t_serializable_object_to_blob(b);
     fluffy_response.current_blockchain_height = arg.current_blockchain_height;
+    std::vector<bool> seen(b.tx_hashes.size(), false);
     for(auto& tx_idx: arg.missing_tx_indices)
     {
       if(tx_idx < b.tx_hashes.size())
       {
         MDEBUG("  tx " << b.tx_hashes[tx_idx]);
+        if (seen[tx_idx])
+        {
+          LOG_ERROR_CCONTEXT
+          (
+            "Failed to handle request NOTIFY_REQUEST_FLUFFY_MISSING_TX"
+            << ", request is asking for duplicate tx "
+            << ", tx index = " << tx_idx << ", block tx count " << b.tx_hashes.size()
+            << ", block_height = " << arg.current_blockchain_height
+            << ", dropping connection"
+          );
+          drop_connection(context, true, false);
+          return 1;
+        }
         txids.push_back(b.tx_hashes[tx_idx]);
+        seen[tx_idx] = true;
       }
       else
       {
```
