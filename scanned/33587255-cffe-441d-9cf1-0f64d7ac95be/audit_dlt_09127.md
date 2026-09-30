# [?] fix: adds timeout on `session_ping` & `pairing_ping` to avoid race condition where the listeners for these events aren't yet initialized

## Summary
Severity: Unknown
Chain: WalletConnect
Component: WalletConnect/walletconnect-monorepo
Published: 2022-09-27
Source: https://github.com/WalletConnect/walletconnect-monorepo/commit/f360f883b14061672955f42cbdd99e383f090fc6
Type: security-commit

## Details
fix: adds timeout on `session_ping` & `pairing_ping` to avoid race condition where the listeners for these events aren't yet initialized

## Patch
### packages/sign-client/src/controllers/engine.ts
```diff
@@ -697,11 +697,15 @@ export class Engine extends IEngine {
 
   private onSessionPingResponse: EnginePrivate["onSessionPingResponse"] = (_topic, payload) => {
     const { id } = payload;
-    if (isJsonRpcResult(payload)) {
-      this.events.emit(engineEvent("session_ping", id), {});
-    } else if (isJsonRpcError(payload)) {
-      this.events.emit(engineEvent("session_ping", id), { error: payload.error });
-    }
+    // put at the end of the stack to avoid a race condition
+    // where session_ping listener is not yet initialized
+    setTimeout(() => {
+      if (isJsonRpcResult(payload)) {
+        this.events.emit(engineEvent("session_ping", id), {});
+      } else if (isJsonRpcError(payload)) {
+        this.events.emit(engineEvent("session_ping", id), { error: payload.error });
+      }
+    }, 200);
   };
 
   private onPairingPingRequest: EnginePrivate["onPairingPingRequest"] = async (topic, payload) => {
@@ -718,11 +722,15 @@ export class Engine extends IEngine {
 
   private onPairingPingResponse: EnginePrivate["onPairingPingResponse"] = (_topic, payload) => {
     const { id } = payload;
-    if (isJsonRpcResult(payload)) {
-      this.events.emit(engineEvent("pairing_ping", id), {});
-    } else if (isJsonRpcError(payload)) {
-      this.events.emit(engineEvent("pairing_ping", id), { error: payload.error });
-    }
+    // put at the end of the stack to avoid a race condition
+    // where pairing_ping listener is not yet initialized
+    setTimeout(() => {
+      if (isJsonRpcResult(payload)) {
+        this.events.emit(engineEvent("pairing_ping", id), {});
+      } else if (isJsonRpcError(payload)) {
+        this.events.emit(engineEvent("pairing_ping", id), { error: payload.error });
+      }
+    }, 200);
   };
 
   private onSessionDeleteRequest: EnginePrivate["onSessionDeleteRequest"] = async (
```
