# [?] fix progress estimation after crash recovery

## Summary
Severity: Unknown
Chain: Indexer
Component: ponder-sh/ponder
Published: 2025-06-12
Source: https://github.com/ponder-sh/ponder/commit/7e3981ee5384895ff10716a302b84fdce86f0d66
Type: security-commit

## Details
fix progress estimation after crash recovery

## Patch
### packages/core/src/bin/utils/run.ts
```diff
@@ -244,8 +244,10 @@ export async function run({
                   { chain: chain.name },
                   Math.max(
                     Number(checkpoint.blockTimestamp) -
-                      sync.seconds[chain.name]!.start -
-                      sync.seconds[chain.name]!.cached,
+                      Math.max(
+                        sync.seconds[chain.name]!.cached,
+                        sync.seconds[chain.name]!.start,
+                      ),
                     0,
                   ),
                 );
@@ -260,8 +262,10 @@ export async function run({
                     Math.min(
                       Math.max(
                         Number(checkpoint.blockTimestamp) -
-                          sync.seconds[chain.name]!.start -
-                          sync.seconds[chain.name]!.cached,
+                          Math.max(
+                            sync.seconds[chain.name]!.cached,
+                            sync.seconds[chain.name]!.start,
+                          ),
                         0,
                       ),
                       Math.max(
```
