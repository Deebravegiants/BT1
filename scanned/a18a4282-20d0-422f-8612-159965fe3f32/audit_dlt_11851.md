# [?] fix: build race condition (#952)

## Summary
Severity: Unknown
Chain: Indexer
Component: ponder-sh/ponder
Published: 2024-07-01
Source: https://github.com/ponder-sh/ponder/commit/a3f30201f9d123b76b39abcc331f71a01f26c7f8
Type: security-commit

## Details
fix: build race condition (#952)

## Patch
### .changeset/nine-rice-argue.md
```diff
@@ -0,0 +1,5 @@
+---
+"@ponder/core": patch
+---
+
+Fixed a bug where circular imports between files (like `ponder.config.ts` and `src/index.ts`) would sometimes return `undefined` during the initial build.
```

### packages/core/src/build/service.ts
```diff
@@ -153,12 +153,11 @@ export const start = async (
 ): Promise<BuildResult> => {
   const { common } = buildService;
 
-  const [configResult, schemaResult, indexingFunctionsResult] =
-    await Promise.all([
-      executeConfig(buildService),
-      executeSchema(buildService),
-      executeIndexingFunctions(buildService),
-    ]);
+  // Note: Don't run these in parallel. If there are circular imports in user code,
+  // it's possible for ViteNodeRunner to return exports as undefined (a race condition).
+  const configResult = await executeConfig(buildService);
+  const schemaResult = await executeSchema(buildService);
+  const indexingFunctionsResult = await executeIndexingFunctions(buildService);
 
   if (configResult.status === "error") {
     return { status: "error", error: configResult.error };
```
