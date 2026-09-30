# [?] Fix geyser plugin unload crash (#34026)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana
Published: 2023-11-15
Source: https://github.com/solana-labs/solana/commit/b5659af54629d112ef316db5867c0cb8f52a388e
Type: security-commit

## Details
Fix geyser plugin unload crash (#34026)

Explicit ordering of the drop of Library and Boxed<dyn GeyserPlugin>: drop the latter explicitly first to avoid crash.

## Patch
### geyser-plugin-manager/src/geyser_plugin_manager.rs
```diff
@@ -217,9 +217,13 @@ impl GeyserPluginManager {
     }
 
     fn _drop_plugin(&mut self, idx: usize) {
+        let current_lib = self.libs.remove(idx);
         let mut current_plugin = self.plugins.remove(idx);
-        let _current_lib = self.libs.remove(idx);
+        let name = current_plugin.name().to_string();
         current_plugin.on_unload();
+        drop(current_plugin);
+        drop(current_lib);
+        info!("Unloaded plugin {name} at idx {idx}");
     }
 }
 
```
