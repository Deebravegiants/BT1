# [?] fix: resolves a race condition where toEstablishConnection could trigger new ws connection because of delayed socket ready state

## Summary
Severity: Unknown
Chain: WalletConnect
Component: WalletConnect/walletconnect-monorepo
Published: 2025-05-01
Source: https://github.com/WalletConnect/walletconnect-monorepo/commit/b4d372f9720f1e2edeac276ffdcc787a99705c0c
Type: security-commit

## Details
fix: resolves a race condition where toEstablishConnection could trigger new ws connection because of delayed socket ready state

## Patch
### packages/core/src/controllers/relayer.ts
```diff
@@ -651,6 +651,10 @@ export class Relayer extends IRelayer {
   private async toEstablishConnection() {
     await this.confirmOnlineStateOrThrow();
     if (this.connected) return;
+    if (this.connectPromise) {
+      await this.connectPromise;
+      return;
+    }
     await this.connect();
   }
 }
```
