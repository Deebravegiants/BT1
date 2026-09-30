# [?] fix(engine): avoids race condition when deleting pairing/session (#1408)

## Summary
Severity: Unknown
Chain: WalletConnect
Component: WalletConnect/walletconnect-monorepo
Published: 2022-09-02
Source: https://github.com/WalletConnect/walletconnect-monorepo/commit/9f55c9acf010b6c5166f11089aa243d34039b0e9
Type: security-commit

## Details
fix(engine): avoids race condition when deleting pairing/session (#1408)

## Patch
### packages/sign-client/src/controllers/engine.ts
```diff
@@ -353,8 +353,9 @@ export class Engine extends IEngine {
 
   private deleteSession: EnginePrivate["deleteSession"] = async (topic) => {
     const { self } = this.client.session.get(topic);
+    // Await the unsubscribe first to avoid deleting the symKey too early below.
+    await this.client.core.relayer.unsubscribe(topic);
     await Promise.all([
-      this.client.core.relayer.unsubscribe(topic),
       this.client.session.delete(topic, getSdkError("USER_DISCONNECTED")),
       this.client.core.crypto.deleteKeyPair(self.publicKey),
       this.client.core.crypto.deleteSymKey(topic),
@@ -363,8 +364,9 @@ export class Engine extends IEngine {
   };
 
   private deletePairing: EnginePrivate["deleteSession"] = async (topic) => {
+    // Await the unsubscribe first to avoid deleting the symKey too early below.
+    await this.client.core.relayer.unsubscribe(topic);
     await Promise.all([
-      this.client.core.relayer.unsubscribe(topic),
       this.client.pairing.delete(topic, getSdkError("USER_DISCONNECTED")),
       this.client.core.crypto.deleteSymKey(topic),
       this.client.expirer.del(topic),
```
