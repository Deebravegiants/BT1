# [?] fix: prevent infinite loop and memory exhaustion in relayer reconnection

## Summary
Severity: Unknown
Chain: WalletConnect
Component: WalletConnect/walletconnect-monorepo
Published: 2026-03-26
Source: https://github.com/WalletConnect/walletconnect-monorepo/commit/e9eaeabfe814086f4aafff820767757e2d54c495
Type: security-commit

## Details
fix: prevent infinite loop and memory exhaustion in relayer reconnection

Fixes multiple interacting bugs in the relayer reconnect logic that
combine to create exponential growth of concurrent connect() calls
when the network is unreachable but isOnline() returns true.

- Eliminate `new Promise(async executor)` antipattern in connect() so
  subscriber.start() no longer runs as an unsupervised background task
  after WebSocket connection failure
- Move connectionAttemptInProgress reset to after the retry loop exits
  so restartTransport() stays blocked during all retry attempts
- Reset reconnectInProgress on early returns in onProviderDisconnect()
  to prevent the flag from getting permanently stuck
- Close old WebSocket in createProvider() before creating a new one
  to prevent leaked connections from accumulating on each retry
- Route toEstablishConnection() through transportOpen() for proper
  connectPromise serialization

Closes #7131

Made-with: Cursor

## Patch
### packages/core/src/controllers/relayer.ts
```diff
@@ -294,13 +294,8 @@ export class Relayer extends IRelayer {
       await this.connectPromise;
       this.logger.debug({}, `Existing connection attempt resolved`);
     } else {
-      this.connectPromise = new Promise(async (resolve, reject) => {
-        await this.connect(relayUrl)
-          .then(resolve)
-          .catch(reject)
-          .finally(() => {
-            this.connectPromise = undefined;
-          });
+      this.connectPromise = this.connect(relayUrl).finally(() => {
+        this.connectPromise = undefined;
       });
       await this.connectPromise;
     }
@@ -380,68 +375,72 @@ export class Relayer extends IRelayer {
     this.connectionAttemptInProgress = true;
     this.transportExplicitlyClosed = false;
     let attempt = 1;
-    while (attempt < 6) {
-      try {
-        if (this.transportExplicitlyClosed) {
-          break;
-        }
-        this.logger.debug({}, `Connecting to ${this.relayUrl}, attempt: ${attempt}...`);
-        // Always create new socket instance when trying to connect because if the socket was dropped due to `socket hang up` exception
-        // It wont be able to reconnect
-        await this.createProvider();
-
-        await new Promise<void>(async (resolve, reject) => {
-          const onDisconnect = () => {
-            reject(new Error(`Connection interrupted while trying to connect`));
-          };
-          this.provider.once(RELAYER_PROVIDER_EVENTS.disconnect, onDisconnect);
-
-          await createExpiringPromise(
-            new Promise((resolve, reject) => {
-              this.provider.connect().then(resolve).catch(reject);
-            }),
-            this.connectTimeout,
-            `Socket stalled when trying to connect to ${this.relayUrl}`,
-          )
-            .catch((e) => {
-              reject(e);
-            })
-            .finally(() => {
-              this.provider.off(RELAYER_PROVIDER_EVENTS.disconnect, onDisconnect);
-              clearTimeout(this.reconnectTimeout);
-            });
-          await new Promise(async (_resolve, _reject) => {
+    try {
+      while (attempt < 6) {
+        try {
+          if (this.transportExplicitlyClosed) {
+            break;
+          }
+          this.logger.debug({}, `Connecting to ${this.relayUrl}, attempt: ${attempt}...`);
+          await this.createProvider();
+
+          // Step A: establish WebSocket connection
+          await new Promise<void>((resolve, reject) => {
+            const onDisconnect = () => {
+              reject(new Error(`Connection interrupted while trying to connect`));
+            };
+            this.provider.once(RELAYER_PROVIDER_EVENTS.disconnect, onDisconnect);
+            createExpiringPromise(
+              new Promise((resolve, reject) => {
+                this.provider.connect().then(resolve).catch(reject);
+              }),
+              this.connectTimeout,
+              `Socket stalled when trying to connect to ${this.relayUrl}`,
+            )
+              .then(() => resolve())
+              .catch(reject)
+              .finally(() => {
+                this.provider.off(RELAYER_PROVIDER_EVENTS.disconnect, onDisconnect);
+                clearTimeout(this.reconnectTimeout);
+              });
+          });
+
+          // Step B: re-subscribe (only reached if Step A resolved)
+          await new Promise<void>((resolve, reject) => {
             const onDisconnect = () => {
               reject(new Error(`Connection interrupted while trying to subscribe`));
             };
             this.provider.once(RELAYER_PROVIDER_EVENTS.disconnect, onDisconnect);
-            await this.subscriber
+            this.subscriber
               .start()
-              .then(_resolve)
-              .catch(_reject)
+              .then(resolve)
+              .catch(reject)
               .finally(() => {
                 this.provider.off(RELAYER_PROVIDER_EVENTS.disconnect, onDisconnect);
               });
           });
+
           this.hasExperiencedNetworkDisruption = false;
-          resolve();
-        });
-      } catch (e) {
-        await this.subscriber.stop();
-        const error = e as Error;
-        this.logger.warn({}, error.message);
-        this.hasExperiencedNetworkDisruption = true;
-      } finally {
-        this.connectionAttemptInProgress = false;
-      }
+        } catch (e) {
+          await this.subscriber.stop();
+          const error = e as Error;
+          this.logger.warn({}, error.message);
+          this.hasExperiencedNetworkDisruption = true;
+        }
 
-      if (this.connected) {
-        this.logger.debug({}, `Connected to ${this.relayUrl} successfully on attempt: ${attempt}`);
-        break;
-      }
+        if (this.connected) {
+          this.logger.debug(
+            {},
+            `Connected to ${this.relayUrl} successfully on attempt: ${attempt}`,
+          );
+          break;
+        }
 
-      await new Promise((resolve) => setTimeout(resolve, toMiliseconds(attempt * 1)));
-      attempt++;
+        await new Promise((resolve) => setTimeout(resolve, toMiliseconds(attempt * 1)));
+        attempt++;
+      }
+    } finally {
+      this.connectionAttemptInProgress = false;
     }
   }
 
@@ -485,6 +484,11 @@ export class Relayer extends IRelayer {
   private async createProvider() {
     if (this.provider.connection) {
       this.unregisterProviderListeners();
+      try {
+        await createExpiringPromise(this.provider.disconnect(), 1000, "Closing previous provider");
+      } catch {
+        // best-effort cleanup of old socket
+      }
     }
     const auth = await this.core.crypto.signJWT(this.relayUrl);
 
@@ -690,8 +694,10 @@ export class Relayer extends IRelayer {
     this.reconnectInProgress = true;
     await this.subscriber.stop();
 
-    if (!this.subscriber.hasAnyTopics) return;
-    if (this.transportExplicitlyClosed) return;
+    if (!this.subscriber.hasAnyTopics || this.transportExplicitlyClosed) {
+      this.reconnectInProgress = false;
+      return;
+    }
 
     this.reconnectTimeout = setTimeout(async () => {
       await this.transportOpen().catch((error) =>
@@ -716,6 +722,6 @@ export class Relayer extends IRelayer {
       await this.connectPromise;
       return;
     }
-    await this.connect();
+    await this.transportOpen();
   }
 }
```

### packages/core/test/relayer.spec.ts
```diff
@@ -716,6 +716,113 @@ describe("Relayer", () => {
     },
   );
 
+  describe("reconnectInProgress guard", () => {
+    beforeEach(async () => {
+      core = new Core(TEST_CORE_OPTIONS);
+      relayer = core.relayer;
+      await core.start();
+      relayer.subscriber.subscriptions.set(randomTopic, {
+        topic: randomTopic,
+        id: randomTopic,
+        relay: { protocol: "irn" },
+      });
+      await relayer.transportOpen();
+    });
+
+    it("should reset reconnectInProgress when no topics exist on disconnect", async () => {
+      // #given - clear all topics so onProviderDisconnect hits the early return
+      expect(relayer.connected).to.be.true;
+      relayer.subscriber.subscriptions.clear();
+      relayer.subscriber.topicMap.clear();
+      relayer.subscriber.pending.clear();
+
+      // #when
+      // @ts-expect-error - private method
+      await relayer.onProviderDisconnect();
+
+      // #then - flag must be reset to allow future reconnection
+      // @ts-expect-error - private property
+      expect(relayer.reconnectInProgress).to.be.false;
+    });
+
+    it("should reset reconnectInProgress when transportExplicitlyClosed on disconnect", async () => {
+      // #given
+      expect(relayer.connected).to.be.true;
+      relayer.transportExplicitlyClosed = true;
+
+      // #when
+      // @ts-expect-error - private method
+      await relayer.onProviderDisconnect();
+
+      // #then
+      // @ts-expect-error - private property
+      expect(relayer.reconnectInProgress).to.be.false;
+    });
+
+    it("should allow reconnection after early return from onProviderDisconnect", async () => {
+      // #given - trigger early return (no topics)
+      relayer.subscriber.subscriptions.clear();
+      relayer.subscriber.topicMap.clear();
+      relayer.subscriber.pending.clear();
+      // @ts-expect-error - private method
+      await relayer.onProviderDisconnect();
+      // @ts-expect-error - private property
+      expect(relayer.reconnectInProgress).to.be.false;
+
+      // #when - re-add topics and trigger another disconnect
+      relayer.subscriber.subscriptions.set(randomTopic, {
+        topic: randomTopic,
+        id: randomTopic,
+        relay: { protocol: "irn" },
+      });
+      // @ts-expect-error - private method
+      await relayer.onProviderDisconnect();
+
+      // #then - should NOT be blocked by a stuck flag — reconnect timeout should be scheduled
+      // @ts-expect-error - private property
+      expect(relayer.reconnectTimeout).to.not.be.undefined;
+      // @ts-expect-error - private property
+      expect(relayer.reconnectInProgress).to.be.true;
+
+      await relayer.transportClose();
+    });
+  });
+
+  describe("connectionAttemptInProgress guard", () => {
+    beforeEach(async () => {
+      core = new Core(TEST_CORE_OPTIONS);
+      relayer = core.relayer;
+      await core.start();
+      relayer.subscriber.subscriptions.set(randomTopic, {
+        topic: randomTopic,
+        id: randomTopic,
+        relay: { protocol: "irn" },
+      });
+    });
+
+    it("should block restartTransport during active connection attempts", async () => {
+      // #given
+      const restartSpy = vi.fn();
+      const originalRestart = relayer.restartTransport.bind(relayer);
+
+      await relayer.transportOpen();
+      expect(relayer.connected).to.be.true;
+
+      // #when - simulate connectionAttemptInProgress being true
+      // @ts-expect-error - private property
+      relayer.connectionAttemptInProgress = true;
+
+      // #then - restartTransport should return early
+      await relayer.restartTransport();
+      // If restartTransport didn't return early, it would have disconnected us
+      expect(relayer.connected).to.be.true;
+
+      // @ts-expect-error - private property
+      relayer.connectionAttemptInProgress = false;
+      await relayer.transportClose();
+    });
+  });
+
   describe("connection_stalled", () => {
     let restartStub: Sinon.SinonStub;
 
```
