# [?] Merge pull request #6965 from NomicFoundation/fix-node-crash

## Summary
Severity: Unknown
Chain: Tooling
Component: NomicFoundation/hardhat
Published: 2025-07-15
Source: https://github.com/NomicFoundation/hardhat/commit/546af5d5eca5bc9a9b93b62040c67b6636f2e400
Type: security-commit

## Details
Merge pull request #6965 from NomicFoundation/fix-node-crash

fix: node crash when sending tx with insufficient funds

## Patch
### .changeset/twenty-lies-destroy.md
```diff
@@ -0,0 +1,5 @@
+---
+"hardhat": patch
+---
+
+Fix node crash when sending a tx with insufficient funds
```

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
@@ -36,10 +39,11 @@ export class JsonRpcHandler {
       return;
     }
 
-    let jsonHttpRequest: any;
+    let jsonHttpRequest: unknown;
     try {
       jsonHttpRequest = await _readJsonHttpRequest(req);
     } catch (error) {
+      ensureError(error);
       this.#sendResponse(res, _handleError(error));
       return;
     }
@@ -48,7 +52,9 @@ export class JsonRpcHandler {
     // the following code block could be safely removed.
     if (Array.isArray(jsonHttpRequest)) {
       const responses = await Promise.all(
-        jsonHttpRequest.map((singleReq: any) => this.#handleRequest(singleReq)),
+        jsonHttpRequest.map((singleReq: unknown) =>
+          this.#handleRequest(singleReq),
+        ),
       );
 
       this.#sendResponse(res, responses);
@@ -80,6 +86,7 @@ export class JsonRpcHandler {
           }),
         );
       } catch (error) {
+        ensureError(error);
         _handleError(error);
       }
     };
@@ -100,6 +107,7 @@ export class JsonRpcHandler {
             )
           : await this.#handleWsRequest(rpcReq, subscriptions);
       } catch (error) {
+        ensureError(error);
         rpcResp = _handleError(error);
       }
 
@@ -142,28 +150,36 @@ export class JsonRpcHandler {
     res.end(JSON.stringify(rpcResp));
   }
 
-  async #handleRequest(req: JsonRpcRequest): Promise<JsonRpcResponse> {
-    req.params = req.params ?? [];
+  async #handleRequest(payload: unknown): Promise<JsonRpcResponse> {
+    if (!isObject(payload)) {
+      return _handleError(new InvalidRequestError());
+    }
+
+    const maybeReq = {
+      ...payload,
+      params: payload.params ?? [],
+    };
 
-    if (!isJsonRpcRequest(req)) {
+    if (!isJsonRpcRequest(maybeReq)) {
       return _handleError(new InvalidRequestError());
     }
 
-    const rpcReq: JsonRpcRequest = req;
+    const rpcReq: JsonRpcRequest = maybeReq;
     let rpcResp: JsonRpcResponse | undefined;
 
     try {
       const result = await this.#provider.request({
-        method: req.method,
-        params: req.params,
+        method: rpcReq.method,
+        params: rpcReq.params,
       });
 
       rpcResp = {
         jsonrpc: "2.0",
-        id: req.id,
+        id: rpcReq.id,
         result,
       };
     } catch (error) {
+      ensureError(error);
       rpcResp = _handleError(error);
     }
 
@@ -195,8 +211,8 @@ export class JsonRpcHandler {
   }
 }
 
-const _readJsonHttpRequest = async (req: IncomingMessage): Promise<any> => {
-  let json;
+const _readJsonHttpRequest = async (req: IncomingMessage): Promise<unknown> => {
+  let json: unknown;
 
   try {
     const bytes: number[] = [];
@@ -233,26 +249,7 @@ const _readWsRequest = (msg: string): JsonRpcRequest | JsonRpcRequest[] => {
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
@@ -262,24 +259,46 @@ const _handleError = (error: any): JsonRpcResponse => {
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
+  }
+
+  if (
+    "data" in error &&
+    isObject(error.data) &&
+    typeof error.data.transactionHash === "string"
+  ) {
+    return error.data.transactionHash;
   }
+}
 
-  if (returnData !== undefined) {
-    data.data = returnData;
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

### v-next/hardhat/test/internal/builtin-plugins/node/json-rpc/handler.ts
```diff
@@ -1,87 +1,336 @@
-import type { HardhatRuntimeEnvironment } from "../../../../../src/types/hre.js";
-import type { JsonRpcResponse } from "../../../../../src/types/providers.js";
+import type { JsonRpcRequest } from "../../../../../src/types/providers.js";
 
 import assert from "node:assert/strict";
 import http from "node:http";
-import { before, describe, it } from "node:test";
+import { after, before, describe, it } from "node:test";
 
 import { exists } from "@nomicfoundation/hardhat-utils/fs";
+import { isObject } from "@nomicfoundation/hardhat-utils/lang";
 
-import { createHardhatRuntimeEnvironment } from "../../../../../src/hre.js";
+import {
+  isFailedJsonRpcResponse,
+  isJsonRpcResponse,
+} from "../../../../../src/internal/builtin-plugins/network-manager/json-rpc.js";
+import {
+  InternalError,
+  InvalidJsonInputError,
+  InvalidRequestError,
+  MethodNotFoundError,
+} from "../../../../../src/internal/builtin-plugins/network-manager/provider-errors.js";
 import { JsonRpcServerImplementation } from "../../../../../src/internal/builtin-plugins/node/json-rpc/server.js";
+import { MockEthereumProvider } from "../../../../utils.js";
 
-describe("JSON-RPC handler", function () {
-  let hre: HardhatRuntimeEnvironment;
+describe("JSON-RPC handler", async function () {
+  const hostname = (await exists("/.dockerenv")) ? "0.0.0.0" : "127.0.0.1";
+  let port: number;
+  const provider = new MockEthereumProvider({
+    eth_chainId: "0x7a69", // 31337 in hex
+    plainError: () => {
+      throw new Error("plain JS error");
+    },
+    methodNotFound: () => {
+      throw new MethodNotFoundError();
+    },
+    topLevelTxHash: () => {
+      const err = new InternalError();
+      // eslint-disable-next-line @typescript-eslint/consistent-type-assertions -- allow in test
+      (err as any).transactionHash = "0xfeed";
+      throw err;
+    },
+    dataAsString: () => {
+      const err = new InternalError();
+      // eslint-disable-next-line @typescript-eslint/consistent-type-assertions -- allow in test
+      (err as any).data = "0xbadbeef";
+      throw err;
+    },
+    dataWithTxHash: () => {
+      const err = new InternalError();
+      // eslint-disable-next-line @typescript-eslint/consistent-type-assertions -- allow in test
+      (err as any).data = { data: null, transactionHash: "0xdead" };
+      throw err;
+    },
+    dataWithData: () => {
+      const err = new InternalError();
+      // eslint-disable-next-line @typescript-eslint/consistent-type-assertions -- allow in test
+      (err as any).data = { data: "0xc0ffee" };
+      throw err;
+    },
+    dataWithBoth: () => {
+      const err = new InternalError();
+      // eslint-disable-next-line @typescript-eslint/consistent-type-assertions -- allow in test
+      (err as any).data = {
+        transactionHash: "0xbeef",
+        data: "0xabad1dea",
+      };
+      throw err;
+    },
+  });
+  const server = new JsonRpcServerImplementation({
+    hostname,
+    port: 0, // use a random port
+    provider,
+  });
 
   before(async function () {
-    hre = await createHardhatRuntimeEnvironment({});
+    const connection = await server.listen();
+    port = connection.port;
+  });
+
+  after(async function () {
+    await server.close();
   });
 
   it("should respond to a request with undefined params", async function () {
-    const hostname = (await exists("/.dockerenv")) ? "0.0.0.0" : "127.0.0.1";
-    const port = 8546;
-
-    const connection = await hre.network.connect();
-    const server = new JsonRpcServerImplementation({
-      hostname,
-      port,
-      provider: connection.provider,
-    });
-
-    try {
-      await server.listen();
-
-      let resolve: (val?: any) => void;
-
-      const postData = JSON.stringify({
-        jsonrpc: "2.0",
-        method: "eth_chainId",
-        id: 1,
-      });
-
-      const promise = new Promise((resolveFunc) => {
-        resolve = resolveFunc;
-      });
-
-      const req = http.request(
-        {
-          hostname,
-          port,
-          method: "POST",
-          headers: {
-            "Content-Type": "application/json",
-            "Content-Length": Buffer.byteLength(postData),
-          },
-          timeout: 10_000,
-        },
-        (res) => {
-          res.on("data", (chunk) => {
-            const response = JSON.parse(chunk.toString());
-
-            resolve(response);
-          });
-        },
-      );
-
-      req.on("error", (error) => {
-        assert.fail(`Request failed: ${error.message}`);
-      });
-
-      req.write(postData);
-
-      // eslint-disable-next-line @typescript-eslint/consistent-type-assertions -- we know this is correct
-      const result = (await promise) as JsonRpcResponse;
-      req.end();
-
-      if ("error" in result) {
-        assert.fail(`Request failed: ${result.error.message}`);
-      }
-
-      assert.equal(result.jsonrpc, "2.0");
-      assert.equal(result.id, 1);
-      assert.equal(Number(result.result), 31337);
-    } finally {
-      await server.close();
+    const rpcReq: JsonRpcRequest = {
+      jsonrpc: "2.0",
+      method: "eth_chainId",
+      id: 1,
+      // no params provided
+    };
+
+    const rpcRes = await postRawJsonRpc(hostname, port, JSON.stringify(rpcReq));
+
+    assert.ok(isJsonRpcResponse(rpcRes), "Expected a valid JSON-RPC response");
+
+    if ("error" in rpcRes) {
+      assert.fail(`Request failed: ${rpcRes.error.message}`);
     }
+
+    assert.equal(rpcRes.jsonrpc, "2.0");
+    assert.equal(rpcRes.id, 1);
+    assert.equal(Number(rpcRes.result), 31337);
+  });
+
+  it("should return a parse error for an invalid JSON input", async function () {
+    const rpcReq = "{ not valid json }"; // not valid JSON
+
+    const rpcRes = await postRawJsonRpc(hostname, port, rpcReq);
+
+    assert.ok(
+      isJsonRpcResponse(rpcRes) && isFailedJsonRpcResponse(rpcRes),
+      "Expected a failed JSON-RPC response",
+    );
+    assert.equal(rpcRes.error.code, InvalidJsonInputError.CODE);
+    assert.match(rpcRes.error.message, /Parse error/);
+  });
+
+  it("should return an invalid request error for a non-object JSON input", async function () {
+    const rpcReq = "eth_chainId"; // not an object
+
+    const rpcRes = await postRawJsonRpc(hostname, port, JSON.stringify(rpcReq));
+
+    assert.ok(
+      isJsonRpcResponse(rpcRes) && isFailedJsonRpcResponse(rpcRes),
+      "Expected a failed JSON-RPC response",
+    );
+    assert.equal(rpcRes.error.code, InvalidRequestError.CODE);
+    assert.match(rpcRes.error.message, /Invalid request/);
+  });
+
+  it("should return an invalid request error for an invalid json rpc request", async function () {
+    const rpcReq = {
+      function: "eth_chainId", // wrong property
+    };
+
+    const rpcRes = await postRawJsonRpc(hostname, port, JSON.stringify(rpcReq));
+
+    assert.ok(
+      isJsonRpcResponse(rpcRes) && isFailedJsonRpcResponse(rpcRes),
+      "Expected a failed JSON-RPC response",
+    );
+    assert.equal(rpcRes.error.code, InvalidRequestError.CODE);
+    assert.match(rpcRes.error.message, /Invalid request/);
+  });
+
+  it("should wrap plain JS Error into InternalError", async function () {
+    const rpcReq: JsonRpcRequest = {
+      jsonrpc: "2.0",
+      method: "plainError",
+      id: 1,
+    };
+
+    const rpcRes = await postRawJsonRpc(hostname, port, JSON.stringify(rpcReq));
+
+    assert.ok(
+      isJsonRpcResponse(rpcRes) && isFailedJsonRpcResponse(rpcRes),
+      "Expected a failed JSON-RPC response",
+    );
+    assert.equal(rpcRes.error.code, InternalError.CODE);
+    assert.match(rpcRes.error.message, /Internal error/);
+    assert.ok(
+      isObject(rpcRes.error.data),
+      "Expected error data to be an object",
+    );
+    assert.ok(
+      typeof rpcRes.error.data.message === "string",
+      "Expected error data.message to be a string",
+    );
+    assert.match(rpcRes.error.data.message, /Internal error/);
+  });
+
+  it("should pass through ProviderError subclasses unwrapped", async function () {
+    const rpcReq: JsonRpcRequest = {
+      jsonrpc: "2.0",
+      method: "methodNotFound",
+      id: 1,
+    };
+
+    const rpcRes = await postRawJsonRpc(hostname, port, JSON.stringify(rpcReq));
+
+    assert.ok(
+      isJsonRpcResponse(rpcRes) && isFailedJsonRpcResponse(rpcRes),
+      "Expected a failed JSON-RPC response",
+    );
+    assert.equal(rpcRes.error.code, MethodNotFoundError.CODE);
+    assert.match(rpcRes.error.message, /Method not found/);
+    assert.ok(
+      isObject(rpcRes.error.data),
+      "Expected error data to be an object",
+    );
+    assert.ok(
+      typeof rpcRes.error.data.message === "string",
+      "Expected error data.message to be a string",
+    );
+    assert.match(rpcRes.error.data.message, /Method not found/);
+  });
+
+  it("should extract top-level transactionHash", async function () {
+    const rpcReq: JsonRpcRequest = {
+      jsonrpc: "2.0",
+      method: "topLevelTxHash",
+      id: 1,
+    };
+
+    const rpcRes = await postRawJsonRpc(hostname, port, JSON.stringify(rpcReq));
+
+    assert.ok(
+      isJsonRpcResponse(rpcRes) && isFailedJsonRpcResponse(rpcRes),
+      "Expected a failed JSON-RPC response",
+    );
+    assert.ok(
+      isObject(rpcRes.error.data),
+      "Expected error data to be an object",
+    );
+    assert.equal(rpcRes.error.data.txHash, "0xfeed");
+    assert.equal(rpcRes.error.data.data, undefined);
+  });
+
+  it("should extract data when error.data is a string", async function () {
+    const rpcReq: JsonRpcRequest = {
+      jsonrpc: "2.0",
+      method: "dataAsString",
+      id: 1,
+    };
+
+    const rpcRes = await postRawJsonRpc(hostname, port, JSON.stringify(rpcReq));
+
+    assert.ok(
+      isJsonRpcResponse(rpcRes) && isFailedJsonRpcResponse(rpcRes),
+      "Expected a failed JSON-RPC response",
+    );
+    assert.ok(
+      isObject(rpcRes.error.data),
+      "Expected error data to be an object",
+    );
+    assert.equal(rpcRes.error.data.txHash, undefined);
+    assert.equal(rpcRes.error.data.data, "0xbadbeef");
+  });
+
+  it("should extract data.transactionHash when present in error.data object", async function () {
+    const rpcReq: JsonRpcRequest = {
+      jsonrpc: "2.0",
+      method: "dataWithTxHash",
+      id: 1,
+    };
+
+    const rpcRes = await postRawJsonRpc(hostname, port, JSON.stringify(rpcReq));
+
+    assert.ok(
+      isJsonRpcResponse(rpcRes) && isFailedJsonRpcResponse(rpcRes),
+      "Expected a failed JSON-RPC response",
+    );
+    assert.ok(
+      isObject(rpcRes.error.data),
+      "Expected error data to be an object",
+    );
+    assert.equal(rpcRes.error.data.txHash, "0xdead");
+    assert.equal(rpcRes.error.data.data, undefined);
+  });
+
+  it("should extract error.data.data when present in error.data object", async function () {
+    const rpcReq: JsonRpcRequest = {
+      jsonrpc: "2.0",
+      method: "dataWithData",
+      id: 1,
+    };
+
+    const rpcRes = await postRawJsonRpc(hostname, port, JSON.stringify(rpcReq));
+
+    assert.ok(
+      isJsonRpcResponse(rpcRes) && isFailedJsonRpcResponse(rpcRes),
+      "Expected a failed JSON-RPC response",
+    );
+    assert.ok(
+      isObject(rpcRes.error.data),
+      "Expected error data to be an object",
+    );
+    assert.equal(rpcRes.error.data.txHash, undefined);
+    assert.equal(rpcRes.error.data.data, "0xc0ffee");
+  });
+
+  it("should extract both txHash and data when both are in error.data", async function () {
+    const rpcReq: JsonRpcRequest = {
+      jsonrpc: "2.0",
+      method: "dataWithBoth",
+      id: 1,
+    };
+
+    const rpcRes = await postRawJsonRpc(hostname, port, JSON.stringify(rpcReq));
+
+    assert.ok(
+      isJsonRpcResponse(rpcRes) && isFailedJsonRpcResponse(rpcRes),
+      "Expected a failed JSON-RPC response",
+    );
+    assert.ok(
+      isObject(rpcRes.error.data),
+      "Expected error data to be an object",
+    );
+    assert.equal(rpcRes.error.data.txHash, "0xbeef");
+    assert.equal(rpcRes.error.data.data, "0xabad1dea");
   });
 });
+
+async function postRawJsonRpc(
+  hostname: string,
+  port: number,
+  rawBody: string,
+): Promise<unknown> {
+  return new Promise((resolve, reject) => {
+    const req = http.request(
+      {
+        hostname,
+        port,
+        method: "POST",
+        headers: { "Content-Type": "application/json" },
+        timeout: 500,
+      },
+      (res) => {
+        res.setEncoding("utf8");
+        let data = "";
+        res.on("data", (chunk: string) => (data += chunk));
+        res.on("end", () => {
+          try {
+            const parsed = JSON.parse(data);
+            resolve(parsed);
+          } catch (err) {
+            reject(err);
+          }
+        });
+      },
+    );
+    req.once("error", reject);
+    req.once("timeout", reject);
+    req.write(rawBody);
+    req.end();
+  });
+}
```

### v-next/hardhat/test/utils.ts
```diff
@@ -1,9 +1,46 @@
+import type {
+  EthereumProvider,
+  RequestArguments,
+} from "../src/types/providers.js";
 import type { Interceptable } from "@nomicfoundation/hardhat-utils/request";
 
+import EventEmitter from "node:events";
 import { after, afterEach, before } from "node:test";
 
 import { getTestDispatcher } from "@nomicfoundation/hardhat-utils/request";
 
+export class MockEthereumProvider
+  extends EventEmitter
+  implements EthereumProvider
+{
+  public callCount = 0;
+
+  constructor(public returnValues: Record<string, any> = {}) {
+    super();
+  }
+
+  public async request(args: RequestArguments): Promise<any> {
+    const returnValue = this.returnValues[args.method];
+    if (returnValue !== undefined) {
+      this.callCount++;
+      return typeof returnValue === "function" ? returnValue() : returnValue;
+    }
+
+    throw new Error("Method not supported");
+  }
+
+  public close(): Promise<void> {
+    return Promise.resolve();
+  }
+
+  public send(): Promise<any> {
+    throw new Error("Method not implemented.");
+  }
+  public sendAsync(): void {
+    throw new Error("Method not implemented.");
+  }
+}
+
 export function createTestEnvManager() {
   const changes = new Set<string>();
   const originalValues = new Map<string, string | undefined>();
```
