# [?] fix: resolve race condition in wallet_getCapabilities cache test

## Summary
Severity: Unknown
Chain: WalletConnect
Component: WalletConnect/walletconnect-monorepo
Published: 2026-01-09
Source: https://github.com/WalletConnect/walletconnect-monorepo/commit/0323c1b832c72a589d1b45d3a6770062f85fba5c
Type: security-commit

## Details
fix: resolve race condition in wallet_getCapabilities cache test

## Patch
### providers/universal-provider/test/5792.spec.ts
```diff
@@ -488,27 +488,25 @@ describe("UniversalProvider 5792 utils", function () {
     };
 
     let walletRequestCount = 0;
-    await Promise.all([
-      new Promise<void>((resolve) => {
-        wallet.client.once("session_request", async (event) => {
-          walletRequestCount++;
-          await wallet.client.respond({
-            topic: event.topic,
-            response: formatJsonRpcResult(event.id, chain1Capabilities),
-          });
-          resolve();
-        });
-      }),
-      new Promise<void>(async (resolve) => {
-        const result = await dapp.request({
-          method: "wallet_getCapabilities",
-          params: [walletAddress], // NO explicit chainIds
+
+    // Set up listener BEFORE making request to avoid race condition
+    const responsePromise1 = new Promise<void>((resolve) => {
+      wallet.client.once("session_request", async (event) => {
+        walletRequestCount++;
+        await wallet.client.respond({
+          topic: event.topic,
+          response: formatJsonRpcResult(event.id, chain1Capabilities),
         });
-        expect(result).to.eql(chain1Capabilities);
         resolve();
-      }),
-    ]);
+      });
+    });
 
+    const result1 = await dapp.request({
+      method: "wallet_getCapabilities",
+      params: [walletAddress], // NO explicit chainIds
+    });
+    await responsePromise1;
+    expect(result1).to.eql(chain1Capabilities);
     expect(walletRequestCount).to.eql(1);
 
     // Second call with same params should return cached (no new request to wallet)
@@ -543,26 +541,24 @@ describe("UniversalProvider 5792 utils", function () {
       },
     };
 
-    await Promise.all([
-      new Promise<void>((resolve) => {
-        wallet.client.once("session_request", async (event) => {
-          walletRequestCount++;
-          await wallet.client.respond({
-            topic: event.topic,
-            response: formatJsonRpcResult(event.id, chain137Capabilities),
-          });
-          resolve();
-        });
-      }),
-      new Promise<void>(async (resolve) => {
-        const result = await dapp.request({
-          method: "wallet_getCapabilities",
-          params: [walletAddress], // NO explicit chainIds - should NOT use cache after chain switch
+    // Set up listener BEFORE making request to avoid race condition
+    const responsePromise2 = new Promise<void>((resolve) => {
+      wallet.client.once("session_request", async (event) => {
+        walletRequestCount++;
+        await wallet.client.respond({
+          topic: event.topic,
+          response: formatJsonRpcResult(event.id, chain137Capabilities),
         });
-        expect(result).to.eql(chain137Capabilities);
         resolve();
-      }),
-    ]);
+      });
+    });
+
+    const result2 = await dapp.request({
+      method: "wallet_getCapabilities",
+      params: [walletAddress], // NO explicit chainIds - should NOT use cache after chain switch
+    });
+    await responsePromise2;
+    expect(result2).to.eql(chain137Capabilities);
 
     // Verify a new request was made to the wallet
     expect(walletRequestCount).to.eql(2);
```
