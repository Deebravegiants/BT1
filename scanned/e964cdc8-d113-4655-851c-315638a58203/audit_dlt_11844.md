# [?] fix crash recovery checkpoint

## Summary
Severity: Unknown
Chain: Indexer
Component: ponder-sh/ponder
Published: 2025-07-02
Source: https://github.com/ponder-sh/ponder/commit/a1f05e83f7126d60e3c430c12fa60b78c7a4ca12
Type: security-commit

## Details
fix crash recovery checkpoint

## Patch
### packages/core/src/bin/utils/run.ts
```diff
@@ -158,18 +158,18 @@ export async function run({
         }
       });
     });
-  }
 
-  // Note: `_ponder_checkpoint` must be updated after the setup events are processed.
-  await database.setCheckpoints({
-    checkpoints: indexingBuild.chains.map((chain) => ({
-      chainName: chain.name,
-      chainId: chain.id,
-      latestCheckpoint: sync.getStartCheckpoint(chain),
-      safeCheckpoint: sync.getStartCheckpoint(chain),
-    })),
-    db: database.qb.drizzle,
-  });
+    // Note: `_ponder_checkpoint` must be updated after the setup events are processed.
+    await database.setCheckpoints({
+      checkpoints: indexingBuild.chains.map((chain) => ({
+        chainName: chain.name,
+        chainId: chain.id,
+        latestCheckpoint: sync.getStartCheckpoint(chain),
+        safeCheckpoint: sync.getStartCheckpoint(chain),
+      })),
+      db: database.qb.drizzle,
+    });
+  }
 
   // Run historical indexing until complete.
   for await (const events of recordAsyncGenerator(
```
