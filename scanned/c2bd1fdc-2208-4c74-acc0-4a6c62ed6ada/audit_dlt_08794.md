# [?] fix(rlprcpt): index overflows if many topics (#834)

## Summary
Severity: Unknown
Chain: Linea
Component: LFDT-Lineth/lineth-monorepo
Published: 2024-07-15
Source: https://github.com/LFDT-Lineth/lineth-monorepo/commit/8955c6b8a469102ee56e76238e848a6a22eb8789
Type: security-commit

## Details
fix(rlprcpt): index overflows if many topics (#834)

## Patch
### tracer/arithmetization/src/test/java/net/consensys/linea/zktracer/ReplayTests.java
```diff
@@ -89,4 +89,9 @@ void failingMmuModexp() {
   void failRlpAddress() {
     replay("5995097.json.gz");
   }
+
+  @Test
+  void rlprcptManyTopicsWoLogData() {
+    replay("6569423.json.gz");
+  }
 }
```

### tracer/zkevm-constraints
```diff
@@ -1 +1 @@
-Subproject commit ceb6511578461474dcdb3c2b2d5c07196d243d47
+Subproject commit 8c596d138414e52248610433af94631bb66372f0
```
