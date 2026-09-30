# [?] fix: sdk crashes in node if `terminate` is not available in the socket

## Summary
Severity: Unknown
Chain: WalletConnect
Component: WalletConnect/walletconnect-monorepo
Published: 2025-03-11
Source: https://github.com/WalletConnect/walletconnect-monorepo/commit/70ce8a34ddce6270146da0933e2ed553124b2fef
Type: security-commit

## Details
fix: sdk crashes in node if `terminate` is not available in the socket

## Patch
### packages/core/src/controllers/relayer.ts
```diff
@@ -448,16 +448,16 @@ export class Relayer extends IRelayer {
 
   private resetPingTimeout = () => {
     if (!isNode()) return;
-    try {
-      clearTimeout(this.pingTimeout);
-      this.pingTimeout = setTimeout(() => {
+    clearTimeout(this.pingTimeout);
+    this.pingTimeout = setTimeout(() => {
+      try {
         this.logger.debug({}, "pingTimeout: Connection stalled, terminating...");
         //@ts-expect-error
-        this.provider?.connection?.socket?.terminate();
-      }, this.heartBeatTimeout);
-    } catch (e) {
-      this.logger.warn(e, (e as Error)?.message);
-    }
+        this.provider?.connection?.socket?.terminate?.();
+      } catch (e) {
+        this.logger.warn(e, (e as Error)?.message);
+      }
+    }, this.heartBeatTimeout);
   };
 
   private async createProvider() {
```
