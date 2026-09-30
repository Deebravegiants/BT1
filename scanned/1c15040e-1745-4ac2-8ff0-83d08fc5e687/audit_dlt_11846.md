# [?] bug fix: remove onError reentrancy check

## Summary
Severity: Unknown
Chain: Indexer
Component: ponder-sh/ponder
Published: 2025-06-12
Source: https://github.com/ponder-sh/ponder/commit/cab17f73b80ee9e1c6274530f4b1a4fe5505548e
Type: security-commit

## Details
bug fix: remove onError reentrancy check

## Patch
### packages/core/src/rpc/index.ts
```diff
@@ -462,10 +462,8 @@ export const createRpc = ({
 
   let interval: NodeJS.Timeout | undefined;
   let webSocketErrorCount = 0;
-  let isWebSocketClosing = false;
   const disconnect = async () => {
     const conn = await wsTransport!.value!.getRpcClient();
-    isWebSocketClosing = true;
     conn.close();
   };
 
@@ -494,7 +492,7 @@ export const createRpc = ({
                 if (webSocketErrorCount === RETRY_COUNT) {
                   common.logger.warn({
                     service: "rpc",
-                    msg: `subscribe onData: Failed '${chain.name}' eth_subscribe after ${webSocketErrorCount + 1} consecutive errors. Switching to polling.`,
+                    msg: `Failed '${chain.name}' newHeads subscription after ${webSocketErrorCount + 1} consecutive errors. Switching to polling`,
                     error,
                   });
 
@@ -506,34 +504,28 @@ export const createRpc = ({
                 } else {
                   common.logger.debug({
                     service: "rpc",
-                    msg: `subscribe onData: Failed '${chain.name}' eth_subscribe request`,
+                    msg: `Received failed '${chain.name}' newHeads subscription data`,
                     error,
                   });
                 }
               } else {
                 common.logger.debug({
                   service: "rpc",
-                  msg: `subscribe onData: result for '${chain.name}': \n ${data.result}`,
+                  msg: `Received successful '${chain.name}' newHeads subscription data`,
                 });
 
                 onBlock(data.result);
                 webSocketErrorCount = 0;
               }
             },
             onError: async (_error) => {
-              // Note: `disconnect` causes `onError` to be called again.
-              if (isWebSocketClosing) {
-                isWebSocketClosing = false;
-                return;
-              }
-
               const error = _error as Error;
               webSocketErrorCount += 1;
 
               if (webSocketErrorCount === RETRY_COUNT) {
                 common.logger.warn({
                   service: "rpc",
-                  msg: `subscribe onError: Failed '${chain.name}' eth_subscribe request after ${webSocketErrorCount + 1} consecutive errors. Switching to polling.`,
+                  msg: `Failed '${chain.name}' newHeads subscription after ${webSocketErrorCount + 1} consecutive errors. Switching to polling`,
                   error,
                 });
 
@@ -543,7 +535,7 @@ export const createRpc = ({
               } else {
                 common.logger.debug({
                   service: "rpc",
-                  msg: `subscribe onError: Failed '${chain.name}' eth_subscribe request`,
+                  msg: `Failed '${chain.name}' newHeads subscription`,
                   error,
                 });
 
@@ -563,15 +555,15 @@ export const createRpc = ({
             if (webSocketErrorCount === RETRY_COUNT) {
               common.logger.warn({
                 service: "rpc",
-                msg: `Failed initial '${chain.name}' eth_subscribe after ${webSocketErrorCount + 1} consecutive errors. Switching to polling.`,
+                msg: `Failed '${chain.name}' eth_subscribe request after ${webSocketErrorCount + 1} consecutive errors. Switching to polling`,
                 error,
               });
               wsTransport = undefined;
             } else {
               const duration = BASE_DURATION * 2 ** webSocketErrorCount;
               common.logger.debug({
                 service: "rpc",
-                msg: `Failed initial '${chain.name}' eth_subscribe request, retrying after ${duration} milliseconds.`,
+                msg: `Failed '${chain.name}' eth_subscribe request, retrying after ${duration} milliseconds`,
                 error,
               });
               await wait(duration);
```
