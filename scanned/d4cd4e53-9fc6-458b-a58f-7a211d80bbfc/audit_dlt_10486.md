# [?] fix: wrap _rpcWebSocketGeneration around when about to overflow (#28428)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-foundation/solana-web3.js
Published: 2022-10-17
Source: https://github.com/solana-foundation/solana-web3.js/commit/29be3d40134c7aca4648c5c53cbc8cf1973b5335
Type: security-commit

## Details
fix: wrap _rpcWebSocketGeneration around when about to overflow (#28428)

## Patch
### src/connection.ts
```diff
@@ -5084,7 +5084,8 @@ export class Connection {
    */
   _wsOnClose(code: number) {
     this._rpcWebSocketConnected = false;
-    this._rpcWebSocketGeneration++;
+    this._rpcWebSocketGeneration =
+      (this._rpcWebSocketGeneration + 1) % Number.MAX_SAFE_INTEGER;
     if (this._rpcWebSocketIdleTimeout) {
       clearTimeout(this._rpcWebSocketIdleTimeout);
       this._rpcWebSocketIdleTimeout = null;
```
