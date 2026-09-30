# [?] Merge pull request #5691 from WalletConnect/fix/crash-if-terminate-is-undefined

## Summary
Severity: Unknown
Chain: WalletConnect
Component: WalletConnect/walletconnect-monorepo
Published: 2025-03-12
Source: https://github.com/WalletConnect/walletconnect-monorepo/commit/7ce73a42e6802647b47d22b84ac53a0691d6b5a4
Type: security-commit

## Details
Merge pull request #5691 from WalletConnect/fix/crash-if-terminate-is-undefined

fix: crash if terminate is undefined

## Patch
### packages/core/src/controllers/relayer.ts
```diff
@@ -452,16 +452,16 @@ export class Relayer extends IRelayer {
 
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

### packages/core/test/relayer.spec.ts
```diff
@@ -362,6 +362,30 @@ describe("Relayer", () => {
         expect(relayer.connected).to.be.true;
         expect(wsConnection.url.startsWith(RELAYER_DEFAULT_RELAY_URL)).to.be.true;
       });
+      it("should not throw an error if terminate() is not available", async () => {
+        const relayer = new Relayer({
+          core,
+          relayUrl: TEST_CORE_OPTIONS.relayUrl,
+          projectId: TEST_CORE_OPTIONS.projectId,
+        });
+        await relayer.init();
+        relayer.subscriber.subscriptions.set(randomTopic, {
+          topic: randomTopic,
+          id: randomTopic,
+          relay: { protocol: "irn" },
+        });
+        await relayer.transportOpen();
+        expect(relayer.connected).to.be.true;
+        //@ts-expect-error - private property
+        relayer.provider.connection.socket.terminate = undefined;
+        //@ts-expect-error - private property
+        relayer.heartBeatTimeout = 1000;
+        //@ts-expect-error - private method
+        relayer.resetPingTimeout();
+        await throttle(2000);
+        await relayer.transportClose();
+        expect(relayer.connected).to.be.false;
+      });
     });
   });
   describe("packageName and bundleId validations", () => {
```
