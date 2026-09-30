# [?] [move-vm] Fix a potential deadlock bug in transitive_dep_closure

## Summary
Severity: Unknown
Chain: Move
Component: move-language/move
Published: 2022-08-21
Source: https://github.com/move-language/move/commit/5de36da2dcd402332909aa35d0728555ec98c15f
Type: security-commit

## Details
[move-vm] Fix a potential deadlock bug in transitive_dep_closure

## Patch
### language/move-vm/runtime/src/loader.rs
```diff
@@ -507,14 +507,15 @@ impl Loader {
         if !visited.insert(id.clone()) {
             return;
         }
-        let entry = self.module_cache.read();
-        for dep in entry
+        let deps = self
+            .module_cache
+            .read()
             .modules
             .get(id)
             .unwrap()
             .module
-            .immediate_dependencies()
-        {
+            .immediate_dependencies();
+        for dep in deps {
             self.transitive_dep_closure(&dep, visited)
         }
     }
```
