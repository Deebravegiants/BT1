# [?] wallet_rpc_server: fix crash in validate_address if no wallet is loaded

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2019-04-24
Source: https://github.com/monero-project/monero/commit/968848a77b9761f42d4ae1df8a30a48e381024c6
Type: security-commit

## Details
wallet_rpc_server: fix crash in validate_address if no wallet is loaded

Reported by SmajeNz0

## Patch
### src/wallet/wallet_rpc_server.cpp
```diff
@@ -4067,9 +4067,10 @@ namespace tools
       { cryptonote::TESTNET, "testnet" },
       { cryptonote::STAGENET, "stagenet" },
     };
+    if (!req.any_net_type && !m_wallet) return not_open(er);
     for (const auto &net_type: net_types)
     {
-      if (!req.any_net_type && net_type.type != m_wallet->nettype())
+      if (!req.any_net_type && (!m_wallet || net_type.type != m_wallet->nettype()))
         continue;
       if (req.allow_openalias)
       {
```
