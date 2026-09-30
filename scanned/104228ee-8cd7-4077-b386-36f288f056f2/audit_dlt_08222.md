# [?] fix: wrap _rpcWebSocketGeneration around when about to overflow (#28428)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana
Published: 2022-10-17
Source: https://github.com/solana-labs/solana/commit/5d172151a2d3d652c6a2e089b09e6fca7f2aa50e
Type: security-commit

## Details
fix: wrap _rpcWebSocketGeneration around when about to overflow (#28428)

## Patch
### web3.js/src/connection.ts
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
