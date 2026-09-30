# [?] fix: node crash when sending tx with insufficient funds

## Summary
Severity: Unknown
Chain: Tooling
Component: NomicFoundation/hardhat
Published: 2025-07-03
Source: https://github.com/NomicFoundation/hardhat/commit/8594d51efcb82edc3d64f4a54e7eec78b31ff1c0
Type: security-commit

## Details
fix: node crash when sending tx with insufficient funds

## Patch
### v-next/hardhat/src/internal/builtin-plugins/node/json-rpc/handler.ts
```diff
@@ -7,6 +7,9 @@ import type {
 import type { IncomingMessage, ServerResponse } from "node:http";
 import type WebSocket from "ws";
 
+import { ensureError } from "@nomicfoundation/hardhat-utils/error";
+import { isObject } from "@nomicfoundation/hardhat-utils/lang";
+
 import {
   isJsonRpcRequest,
   isJsonRpcResponse,
@@ -40,6 +43,7 @@ export class JsonRpcHandler {
     try {
       jsonHttpRequest = await _readJsonHttpRequest(req);
     } catch (error) {
+      ensureError(error);
       this.#sendResponse(res, _handleError(error));
       return;
     }
@@ -80,6 +84,7 @@ export class JsonRpcHandler {
           }),
         );
       } catch (error) {
+        ensureError(error);
         _handleError(error);
       }
     };
@@ -100,6 +105,7 @@ export class JsonRpcHandler {
             )
           : await this.#handleWsRequest(rpcReq, subscriptions);
       } catch (error) {
+        ensureError(error);
         rpcResp = _handleError(error);
       }
 
@@ -164,6 +170,7 @@ export class JsonRpcHandler {
         result,
       };
     } catch (error) {
+      ensureError(error);
       rpcResp = _handleError(error);
     }
 
@@ -233,26 +240,7 @@ const _readWsRequest = (msg: string): JsonRpcRequest | JsonRpcRequest[] => {
   return json;
 };
 
-const _handleError = (error: any): JsonRpcResponse => {
-  // extract the relevant fields from the error before wrapping it
-  let txHash: string | undefined;
-  let returnData: string | undefined;
-
-  if (error.transactionHash !== undefined) {
-    txHash = error.transactionHash;
-  }
-  if (error.data !== undefined) {
-    if (error.data.data !== undefined) {
-      returnData = error.data.data;
-    } else {
-      returnData = error.data;
-    }
-
-    if (txHash === undefined && error.data.transactionHash !== undefined) {
-      txHash = error.data.transactionHash;
-    }
-  }
-
+const _handleError = (error: Error): JsonRpcResponse => {
   // In case of non-hardhat error, treat it as internal and associate the appropriate error code.
   if (!ProviderError.isProviderError(error)) {
     error = new InternalError(undefined, error);
@@ -262,24 +250,45 @@ const _handleError = (error: any): JsonRpcResponse => {
     jsonrpc: "2.0",
     id: null,
     error: {
-      code: error.code,
+      code:
+        "code" in error && typeof error.code === "number"
+          ? error.code
+          : InternalError.CODE,
       message: error.message,
+      data: {
+        message: error.message,
+        txHash: extractTxHash(error),
+        data: extractReturnData(error),
+      },
     },
   };
 
-  const data: any = {
-    message: error.message,
-  };
+  return response;
+};
 
-  if (txHash !== undefined) {
-    data.txHash = txHash;
+function extractTxHash(error: Error): string | undefined {
+  if ("transactionHash" in error && typeof error.transactionHash === "string") {
+    return error.transactionHash;
   }
 
-  if (returnData !== undefined) {
-    data.data = returnData;
+  if (
+    "data" in error &&
+    isObject(error.data) &&
+    typeof error.data.transactionHash === "string"
+  ) {
+    return error.data.transactionHash;
+  }
+}
+function extractReturnData(error: Error): string | undefined {
+  if (!("data" in error)) {
+    return undefined;
   }
 
-  response.error.data = data;
+  if (typeof error.data === "string") {
+    return error.data;
+  }
 
-  return response;
-};
+  if (isObject(error.data) && typeof error.data.data === "string") {
+    return error.data.data;
+  }
+}
```
