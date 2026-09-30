# [?] Fix failed lambda execution crashing coordinator (#1582)

## Summary
Severity: Unknown
Chain: API3
Component: api3dao/airnode
Published: 2022-12-05
Source: https://github.com/api3dao/airnode/commit/34f94258e48f8f1dfe7e7e836539effceb4dd576
Type: security-commit

## Details
Fix failed lambda execution crashing coordinator (#1582)

* Fix failed lambda execution crashing coordinator

* Add changeset

* Check for data payload explicitly

## Patch
### .changeset/dry-weeks-cough.md
```diff
@@ -0,0 +1,5 @@
+---
+'@api3/airnode-node': patch
+---
+
+Fix failed lambda execution crashing coordinator
```

### packages/airnode-node/src/workers/cloud-platforms/aws.ts
```diff
@@ -1,9 +1,11 @@
+import { logger } from '@api3/airnode-utilities';
+import { goSync } from '@api3/promise-utils';
 import AWS from 'aws-sdk';
 import { WorkerParameters, WorkerResponse } from '../../types';
 
 export function spawn(params: WorkerParameters): Promise<WorkerResponse> {
   // lambda.invoke is synchronous so we need to wrap this in a promise
-  return new Promise((resolve, reject) => {
+  return new Promise((spawnResolve, spawnReject) => {
     // Uses the current region by default
     const lambda = new AWS.Lambda();
 
@@ -15,12 +17,33 @@ export function spawn(params: WorkerParameters): Promise<WorkerResponse> {
       Payload: JSON.stringify(params.payload),
     };
 
+    const resolve: typeof spawnResolve = (value) => {
+      logger.debug(`Successful Lambda response: ${value}`);
+      spawnResolve(value);
+    };
+
+    const reject: typeof spawnReject = (error) => {
+      logger.debug(`Lambda invocation or execution failed. Response: ${error}`);
+      spawnReject(error);
+    };
+
+    // The Lambda invocation callback populates the error (first argument) only when the invocation fails (e.g. status
+    // code is 400) or the request is not parsed properly by the SDK and can't be invoked. For errors and timeouts that
+    // happen inside the invoked lambda have "data.FunctionError" and "data.Payload.errorMessage" populated instead.
+    // See: https://stackoverflow.com/q/42672023 and https://stackoverflow.com/q/48644093
     lambda.invoke(options, (err, data) => {
-      if (err) {
-        reject(err);
-        return;
-      }
-      resolve(JSON.parse(JSON.parse(data.Payload as string).body) as WorkerResponse);
+      if (err) return reject(err);
+
+      if (data.FunctionError) return reject(data.Payload);
+
+      if (!data.Payload) return reject(new Error('Missing payload in lambda response'));
+      const goPayload = goSync(() => JSON.parse(data.Payload!.toString()));
+      if (!goPayload.success) return reject(goPayload.error);
+
+      const goBody = goSync(() => JSON.parse(goPayload.data.body));
+      if (!goBody.success) return reject(goBody.error);
+
+      resolve(goBody.data as WorkerResponse);
     });
   });
 }
```
