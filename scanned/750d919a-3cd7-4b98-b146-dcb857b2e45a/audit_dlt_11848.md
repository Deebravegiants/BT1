# [?] fix: seconds metrics with crash recovery

## Summary
Severity: Unknown
Chain: Indexer
Component: ponder-sh/ponder
Published: 2025-02-14
Source: https://github.com/ponder-sh/ponder/commit/837e1849c53467a84d9a7e93a55f76b7c4820daf
Type: security-commit

## Details
fix: seconds metrics with crash recovery

## Patch
### packages/core/src/bin/utils/run.ts
```diff
@@ -171,7 +171,8 @@ export async function run({
                   { network: network.name },
                   Math.max(
                     checkpoint.blockTimestamp -
-                      sync.seconds[network.name]!.start,
+                      sync.seconds[network.name]!.start -
+                      sync.seconds[network.name]!.cached,
                     0,
                   ),
                 );
@@ -185,7 +186,8 @@ export async function run({
                     { network: network.name },
                     Math.max(
                       checkpoint.blockTimestamp -
-                        sync.seconds[network.name]!.start,
+                        sync.seconds[network.name]!.start -
+                        sync.seconds[network.name]!.cached,
                       0,
                     ),
                   );
@@ -265,7 +267,9 @@ export async function run({
     common.metrics.ponder_historical_completed_indexing_seconds.set(
       label,
       Math.max(
-        sync.seconds[network.name]!.end - sync.seconds[network.name]!.start,
+        sync.seconds[network.name]!.end -
+          sync.seconds[network.name]!.start -
+          sync.seconds[network.name]!.cached,
         0,
       ),
     );
```

### packages/core/src/sync/index.ts
```diff
@@ -806,7 +806,13 @@ export const createSync = async (params: {
             getOmnichainCheckpoint({ tag: "finalized" }),
           ),
         ).blockTimestamp,
-        cached: decodeCheckpoint(params.initialCheckpoint).blockTimestamp,
+        cached: decodeCheckpoint(
+          min(
+            getOmnichainCheckpoint({ tag: "end" }),
+            getOmnichainCheckpoint({ tag: "finalized" }),
+            params.initialCheckpoint,
+          ),
+        ).blockTimestamp,
       };
     }
   } else {
@@ -820,7 +826,13 @@ export const createSync = async (params: {
             getOmnichainCheckpoint({ tag: "finalized" }),
           ),
         ).blockTimestamp,
-        cached: decodeCheckpoint(params.initialCheckpoint).blockTimestamp,
+        cached: decodeCheckpoint(
+          min(
+            getOmnichainCheckpoint({ tag: "end" }),
+            getOmnichainCheckpoint({ tag: "finalized" }),
+            params.initialCheckpoint,
+          ),
+        ).blockTimestamp,
       };
     }
   }
```
