# [?] fix(pos-client): resolve flaky test race condition

## Summary
Severity: Unknown
Chain: WalletConnect
Component: WalletConnect/walletconnect-monorepo
Published: 2026-01-14
Source: https://github.com/WalletConnect/walletconnect-monorepo/commit/1cbe5bb2f5b10b2615e5c4a5c071c85f87c251da
Type: security-commit

## Details
fix(pos-client): resolve flaky test race condition

Register all event listeners before triggering createPaymentIntent
to prevent race conditions where events could fire before handlers
were attached. Also increased test timeout to 90s to accommodate
RPC polling delays in CI.

## Patch
### packages/pos-client/test/pos.spec.ts
```diff
@@ -290,69 +290,88 @@ describe("Sign Integration", () => {
       },
     ];
 
-    await Promise.all([
-      new Promise<void>((resolve) => {
-        pos.once("payment_successful", () => {
-          console.log("payment_successful");
-          resolve();
-        });
-      }),
-      new Promise<void>((resolve) => {
-        pos.once("payment_requested", () => {
-          console.log("payment_requested");
-          resolve();
-        });
-      }),
-      new Promise<void>((resolve) => {
-        pos.once("payment_broadcasted", (result) => {
-          console.log("payment_broadcasted", JSON.stringify(result, null, 2));
-          resolve();
-        });
-      }),
-      new Promise<void>((resolve) => {
-        wallet.events.once("session_request", async (sessionRequest) => {
-          console.log("session_request", JSON.stringify(sessionRequest, null, 2));
-          await wallet.respond({
-            topic: sessionRequest.topic,
-            response: formatJsonRpcResult(
-              sessionRequest.id,
-              "0xff16b7197277088039a45f9e23ccbb32077ebeec1e56e49b24b2f3731e1bd452",
-            ),
-          });
-          resolve();
+    // #given - Register all event listeners BEFORE triggering the flow
+    const paymentSuccessful = new Promise<void>((resolve) => {
+      pos.once("payment_successful", () => {
+        console.log("payment_successful");
+        resolve();
+      });
+    });
+
+    const paymentRequested = new Promise<void>((resolve) => {
+      pos.once("payment_requested", () => {
+        console.log("payment_requested");
+        resolve();
+      });
+    });
+
+    const paymentBroadcasted = new Promise<void>((resolve) => {
+      pos.once("payment_broadcasted", (result) => {
+        console.log("payment_broadcasted", JSON.stringify(result, null, 2));
+        resolve();
+      });
+    });
+
+    const sessionRequest = new Promise<void>((resolve) => {
+      wallet.events.once("session_request", async (sessionRequest) => {
+        console.log("session_request", JSON.stringify(sessionRequest, null, 2));
+        await wallet.respond({
+          topic: sessionRequest.topic,
+          response: formatJsonRpcResult(
+            sessionRequest.id,
+            "0xff16b7197277088039a45f9e23ccbb32077ebeec1e56e49b24b2f3731e1bd452",
+          ),
         });
-      }),
-      new Promise<void>((resolve) => {
-        wallet.events.once("session_proposal", async (sessionProposal) => {
-          console.log("session_proposal", JSON.stringify(sessionProposal, null, 2));
-          await wallet.approve({
-            id: sessionProposal.id,
-            namespaces: {
-              eip155: {
-                ...sessionProposal.params.optionalNamespaces.eip155,
-                accounts: [`${tokenChainId}:0x13A2Ff792037AA2cd77fE1f4B522921ac59a9C52`],
-              },
+        resolve();
+      });
+    });
+
+    const sessionProposal = new Promise<void>((resolve) => {
+      wallet.events.once("session_proposal", async (sessionProposal) => {
+        console.log("session_proposal", JSON.stringify(sessionProposal, null, 2));
+        await wallet.approve({
+          id: sessionProposal.id,
+          namespaces: {
+            eip155: {
+              ...sessionProposal.params.optionalNamespaces.eip155,
+              accounts: [`${tokenChainId}:0x13A2Ff792037AA2cd77fE1f4B522921ac59a9C52`],
             },
-          });
-          resolve();
-        });
-      }),
-      new Promise<void>((resolve) => {
-        pos.once("connected", () => {
-          console.log("connected");
-          resolve();
-        });
-      }),
-      new Promise<void>((resolve) => {
-        pos.once("qr_ready", async ({ uri }) => {
-          console.log("qr_ready", uri);
-          await wallet.pair({ uri });
-          resolve();
+          },
         });
-      }),
-      pos.createPaymentIntent({ paymentIntents }),
+        resolve();
+      });
+    });
+
+    const connected = new Promise<void>((resolve) => {
+      pos.once("connected", () => {
+        console.log("connected");
+        resolve();
+      });
+    });
+
+    const qrReady = new Promise<void>((resolve) => {
+      pos.once("qr_ready", async ({ uri }) => {
+        console.log("qr_ready", uri);
+        await wallet.pair({ uri });
+        resolve();
+      });
+    });
+
+    // #when - Trigger the payment flow
+    const paymentIntent = pos.createPaymentIntent({ paymentIntents });
+
+    // #then - Wait for all events to complete
+    await Promise.all([
+      paymentSuccessful,
+      paymentRequested,
+      paymentBroadcasted,
+      sessionRequest,
+      sessionProposal,
+      connected,
+      qrReady,
+      paymentIntent,
     ]);
-  });
+  }, 90_000);
 
   it("should accept multiple payment intents, establish a session, prepare transactions, send all requests to wallet, receive responses and await confirmations", async () => {
     const evmChainId = "eip155:8453";
```
