# [?] fix(wallet-server): don't crash if bitcoind not available on start

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2025-01-18
Source: https://github.com/fedimint/fedimint/commit/dfd63afed147b5a930dec36af53f233bf09369ff
Type: security-commit

## Details
fix(wallet-server): don't crash if bitcoind not available on start

## Patch
### modules/fedimint-wallet-server/src/lib.rs
```diff
@@ -1011,10 +1011,11 @@ impl Wallet {
         let bitcoind_rpc = bitcoind;
 
         let bitcoind_net = NetworkLegacyEncodingWrapper(
-            bitcoind_rpc
-                .get_network()
-                .await
-                .map_err(|e| WalletCreationError::RpcError(e.to_string()))?,
+            retry("verify network", backoff_util::aggressive_backoff(), || {
+                bitcoind_rpc.get_network()
+            })
+            .await
+            .map_err(|e| WalletCreationError::RpcError(e.to_string()))?,
         );
         if bitcoind_net != cfg.consensus.network {
             return Err(WalletCreationError::WrongNetwork(
```
