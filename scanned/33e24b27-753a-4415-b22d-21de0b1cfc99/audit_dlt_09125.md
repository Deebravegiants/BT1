# [?] fix: saves `session` object before sending `sessionSettle` request to avoid potential race condition

## Summary
Severity: Unknown
Chain: WalletConnect
Component: WalletConnect/walletconnect-monorepo
Published: 2024-01-05
Source: https://github.com/WalletConnect/walletconnect-monorepo/commit/0e2d87dfe038e23b9bbec768b002541165e8be53
Type: security-commit

## Details
fix: saves `session` object before sending `sessionSettle` request to avoid potential race condition

## Patch
### packages/sign-client/src/controllers/engine.ts
```diff
@@ -267,12 +267,6 @@ export class Engine extends IEngine {
       ...(sessionProperties && { sessionProperties }),
     };
     await this.client.core.relayer.subscribe(sessionTopic);
-    await this.sendRequest({
-      topic: sessionTopic,
-      method: "wc_sessionSettle",
-      params: sessionSettle,
-      throwOnFailedPublish: true,
-    });
     const session = {
       ...sessionSettle,
       topic: sessionTopic,
@@ -286,6 +280,20 @@ export class Engine extends IEngine {
       controller: selfPublicKey,
     };
     await this.client.session.set(sessionTopic, session);
+    try {
+      await this.sendRequest({
+        topic: sessionTopic,
+        method: "wc_sessionSettle",
+        params: sessionSettle,
+        throwOnFailedPublish: true,
+      });
+    } catch (error) {
+      this.client.logger.error(error);
+      // if the publish fails, delete the session and throw an error
+      this.client.session.delete(sessionTopic, getSdkError("USER_DISCONNECTED"));
+      throw error;
+    }
+
     await this.setExpiry(sessionTopic, calcExpiry(SESSION_EXPIRY));
     return {
       topic: sessionTopic,
```
