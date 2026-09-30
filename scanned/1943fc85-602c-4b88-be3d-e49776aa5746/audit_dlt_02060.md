# [?] fix: session approval race condition (#2395)

## Summary
Severity: Unknown
Chain: WalletConnect
Component: WalletConnect/walletconnect-monorepo
Published: 2023-05-17
Source: https://github.com/WalletConnect/walletconnect-monorepo/commit/6ef2258ea039a9fb7b8162a47a6ed8cf6571b6c1
Type: security-commit

## Details
fix: session approval race condition (#2395)

* fix: adds 500ms delay on session approval to avoid race condition where the peer hasn't finished processing the proposal while receiving requests

* chore: log incoming payloads

* chore: log pairing pings

* chore: lint

* chore: log pairing ack

* chore: pairing event

* chore: log pairing event emit

* chore: remove logs

---------

Co-authored-by: Gancho Radkov <ganchoradkov@gmail.com>

## Patch
### packages/core/src/controllers/pairing.ts
```diff
@@ -187,8 +187,7 @@ export class Pairing implements IPairing {
     const message = await this.core.crypto.encode(topic, payload);
     const opts = PAIRING_RPC_OPTS[method].req;
     this.core.history.set(topic, payload);
-    await this.core.relayer.publish(topic, message, opts);
-
+    this.core.relayer.publish(topic, message, opts);
     return payload.id;
   };
 
```

### packages/sign-client/src/controllers/engine.ts
```diff
@@ -1,3 +1,4 @@
+/* eslint-disable no-console */
 import { EXPIRER_EVENTS, RELAYER_DEFAULT_PROTOCOL, RELAYER_EVENTS } from "@walletconnect/core";
 
 import {
@@ -234,7 +235,10 @@ export class Engine extends IEngine {
     await this.setExpiry(sessionTopic, calcExpiry(SESSION_EXPIRY));
     return {
       topic: sessionTopic,
-      acknowledged: () => new Promise((resolve) => resolve(this.client.session.get(sessionTopic))),
+      acknowledged: () =>
+        new Promise((resolve) =>
+          setTimeout(() => resolve(this.client.session.get(sessionTopic)), 5_00),
+        ), // artificial delay to allow for the session to be processed by the peer
     };
   };
 
```

### packages/sign-client/test/sdk/client.spec.ts
```diff
@@ -134,15 +134,15 @@ describe("Sign Client Integration", () => {
     describe("pairing", () => {
       describe("with existing pairing", () => {
         it("A pings B", async () => {
-          const clients = await initTwoClients();
+          const clients = await initTwoClients({ name: "dapp" }, { name: "wallet" });
           const {
             pairingA: { topic },
           } = await testConnectMethod(clients);
           await clients.A.ping({ topic });
           await deleteClients(clients);
         });
         it("B pings A", async () => {
-          const clients = await initTwoClients();
+          const clients = await initTwoClients({ name: "dapp" }, { name: "wallet" });
           const {
             pairingA: { topic },
           } = await testConnectMethod(clients);
```
