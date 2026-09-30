# [?] Fix potential deadlock in state_key::Entry::drop (#14670)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2024-09-20
Source: https://github.com/aptos-labs/aptos-core/commit/8eb8b52cc67d2b405c2d5c16ca98f3fa18db8797
Type: security-commit

## Details
Fix potential deadlock in state_key::Entry::drop (#14670)

## Patch
### types/src/state_store/state_key/registry.rs
```diff
@@ -152,13 +152,13 @@ where
         let mut locked = self.inner.write();
         if let Some(map2) = locked.get_mut(key1) {
             if let Some(entry) = map2.get(key2) {
-                if entry.upgrade().is_none() {
+                if entry.strong_count() == 0 {
                     map2.remove(key2);
+                    if map2.is_empty() {
+                        locked.remove(key1);
+                    }
                 }
             }
-            if map2.is_empty() {
-                locked.remove(key1);
-            }
         }
     }
 
```
