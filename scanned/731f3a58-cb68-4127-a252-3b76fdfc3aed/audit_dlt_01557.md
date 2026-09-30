# [?] fix memory corruption in geyser plugin manager tests with recent toolchains (#33097)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana
Published: 2023-08-31
Source: https://github.com/solana-labs/solana/commit/7e5cd11b340b3c80285481cc3276a7b002486ef0
Type: security-commit

## Details
fix memory corruption in geyser plugin manager tests with recent toolchains (#33097)

* geyser: genericize manager test dummy plugin generators

* geyser: dlopen self the safe way in test dummy plugin generator

fixes memory corruption

## Patch
### geyser-plugin-manager/src/geyser_plugin_manager.rs
```diff
@@ -333,7 +333,7 @@ pub(crate) fn load_plugin_from_config(
 pub(crate) fn load_plugin_from_config(
     _geyser_plugin_config_file: &Path,
 ) -> Result<(Box<dyn GeyserPlugin>, Library, &str), GeyserPluginManagerError> {
-    Ok(tests::dummy_plugin_and_library())
+    Ok(tests::dummy_plugin_and_library(tests::TestPlugin))
 }
 
 #[cfg(test)]
@@ -345,33 +345,21 @@ mod tests {
         std::sync::{Arc, RwLock},
     };
 
-    pub(super) fn dummy_plugin_and_library() -> (Box<dyn GeyserPlugin>, Library, &'static str) {
-        let plugin = Box::new(TestPlugin);
-        let lib = {
-            let handle: *mut std::os::raw::c_void = &mut () as *mut _ as *mut std::os::raw::c_void;
-            // SAFETY: all calls to get Symbols should fail, so this is actually safe
-            let inner_lib = unsafe { libloading::os::unix::Library::from_raw(handle) };
-            Library::from(inner_lib)
-        };
-        (plugin, lib, DUMMY_CONFIG)
-    }
-
-    pub(super) fn dummy_plugin_and_library2() -> (Box<dyn GeyserPlugin>, Library, &'static str) {
-        let plugin = Box::new(TestPlugin2);
-        let lib = {
-            let handle: *mut std::os::raw::c_void = &mut () as *mut _ as *mut std::os::raw::c_void;
-            // SAFETY: all calls to get Symbols should fail, so this is actually safe
-            let inner_lib = unsafe { libloading::os::unix::Library::from_raw(handle) };
-            Library::from(inner_lib)
-        };
-        (plugin, lib, DUMMY_CONFIG)
+    pub(super) fn dummy_plugin_and_library<P: GeyserPlugin>(
+        plugin: P,
+    ) -> (Box<dyn GeyserPlugin>, Library, &'static str) {
+        (
+            Box::new(plugin),
+            Library::from(libloading::os::unix::Library::this()),
+            DUMMY_CONFIG,
+        )
     }
 
     const DUMMY_NAME: &str = "dummy";
     pub(super) const DUMMY_CONFIG: &str = "dummy_config";
     const ANOTHER_DUMMY_NAME: &str = "another_dummy";
 
-    #[derive(Debug)]
+    #[derive(Clone, Copy, Debug)]
     pub(super) struct TestPlugin;
 
     impl GeyserPlugin for TestPlugin {
@@ -380,7 +368,7 @@ mod tests {
         }
     }
 
-    #[derive(Debug)]
+    #[derive(Clone, Copy, Debug)]
     pub(super) struct TestPlugin2;
 
     impl GeyserPlugin for TestPlugin2 {
@@ -403,7 +391,7 @@ mod tests {
         );
 
         // Mock having loaded plugin (TestPlugin)
-        let (mut plugin, lib, config) = dummy_plugin_and_library();
+        let (mut plugin, lib, config) = dummy_plugin_and_library(TestPlugin);
         plugin.on_load(config).unwrap();
         plugin_manager_lock.plugins.push(plugin);
         plugin_manager_lock.libs.push(lib);
@@ -432,12 +420,12 @@ mod tests {
 
         // Load two plugins
         // First
-        let (mut plugin, lib, config) = dummy_plugin_and_library();
+        let (mut plugin, lib, config) = dummy_plugin_and_library(TestPlugin);
         plugin.on_load(config).unwrap();
         plugin_manager_lock.plugins.push(plugin);
         plugin_manager_lock.libs.push(lib);
         // Second
-        let (mut plugin, lib, config) = dummy_plugin_and_library2();
+        let (mut plugin, lib, config) = dummy_plugin_and_library(TestPlugin2);
         plugin.on_load(config).unwrap();
         plugin_manager_lock.plugins.push(plugin);
         plugin_manager_lock.libs.push(lib);
```
