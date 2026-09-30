# [?] fix: return JSON-RPC error instead of crashing when eth_accounts returns non-array

## Summary
Severity: Unknown
Chain: Tooling
Component: NomicFoundation/hardhat
Published: 2026-05-24
Source: https://github.com/NomicFoundation/hardhat/commit/9c94c2737802af48e1e08702fea29ace4a7be814
Type: security-commit

## Details
fix: return JSON-RPC error instead of crashing when eth_accounts returns non-array

## Patch
### packages/hardhat/src/internal/builtin-plugins/network-manager/request-handlers/handlers/accounts/automatic-sender-handler.ts
```diff
@@ -1,4 +1,7 @@
-import { assertHardhatInvariant } from "@nomicfoundation/hardhat-errors";
+import type {
+  JsonRpcRequest,
+  JsonRpcResponse,
+} from "../../../../../../types/providers.js";
 
 import { SenderHandler } from "./sender.js";
 
@@ -11,22 +14,37 @@ export class AutomaticSenderHandler extends SenderHandler {
   #alreadyFetchedAccounts = false;
   #firstAccount: string | undefined;
 
-  protected async getSender(): Promise<string | undefined> {
+  public override async handle(
+    jsonRpcRequest: JsonRpcRequest,
+  ): Promise<JsonRpcRequest | JsonRpcResponse> {
+    if (!this.isSupportedMethod(jsonRpcRequest)) {
+      return jsonRpcRequest;
+    }
+
     if (this.#alreadyFetchedAccounts === false) {
       const accounts = await this.provider.request({
         method: "eth_accounts",
       });
 
-      // TODO: This shouldn't be an exception but a failed JSON response!
-      assertHardhatInvariant(
-        Array.isArray(accounts),
-        "eth_accounts response should be an array",
-      );
+      if (!Array.isArray(accounts)) {
+        return {
+          jsonrpc: "2.0",
+          id: jsonRpcRequest.id,
+          error: {
+            code: -32603,
+            message: "eth_accounts did not return an array of accounts",
+          },
+        };
+      }
 
       this.#firstAccount = accounts[0];
       this.#alreadyFetchedAccounts = true;
     }
 
+    return await super.handle(jsonRpcRequest);
+  }
+
+  protected async getSender(): Promise<string | undefined> {
     return this.#firstAccount;
   }
 }
```
