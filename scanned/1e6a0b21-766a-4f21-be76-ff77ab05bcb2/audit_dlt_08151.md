# [?] wallet_rpc_server: fix buffer read overflow in string assignment

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2019-03-15
Source: https://github.com/monero-project/monero/commit/4ee156556dfbb27fa460749bf7ae15a9df904ede
Type: security-commit

## Details
wallet_rpc_server: fix buffer read overflow in string assignment

## Patch
### src/wallet/wallet_rpc_server.cpp
```diff
@@ -3331,7 +3331,7 @@ namespace tools
       er.message = "Failed to encode seed";
       return false;
     }
-    res.seed = electrum_words.data();
+    res.seed = std::string(electrum_words.data(), electrum_words.size());
 
     if (!wal)
     {
```
