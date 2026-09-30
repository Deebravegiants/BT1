# [?] hw wallets: fix crashes on macOS

## Summary
Severity: Unknown
Chain: Bitcoin
Component: spesmilo/electrum
Published: 2023-12-17
Source: https://github.com/spesmilo/electrum/commit/740016e0d5b77d68d4006e12235ead3c043a6b6a
Type: security-commit

## Details
hw wallets: fix crashes on macOS

related https://github.com/trezor/cython-hidapi/pull/150#issuecomment-1542391087

## Patch
### electrum/plugin.py
```diff
@@ -140,7 +140,7 @@ def load_plugin(self, name) -> 'BasePlugin':
                                % (self.gui_name, name))
         try:
             module = importlib.util.module_from_spec(spec)
-            spec.loader.exec_module(module)
+            spec.loader.exec_module(module)  # note: imports the plugin code in a *different* thread
             plugin = module.Plugin(self, self.config, name)
         except Exception as e:
             raise Exception(f"Error loading {name} plugin: {repr(e)}") from e
@@ -374,6 +374,16 @@ class HardwarePluginToScan(NamedTuple):
     thread_name_prefix='hwd_comms_thread'
 )
 
+# hidapi needs to be imported from the main thread. Otherwise, at least on macOS,
+# segfaults will follow. (see https://github.com/trezor/cython-hidapi/pull/150#issuecomment-1542391087)
+# To keep it simple, let's just import it now, as we are likely in the main thread here.
+if threading.current_thread() is not threading.main_thread():
+    _logger.warning("expected to be in main thread... hidapi will not be safe to use now!")
+try:
+    import hid
+except ImportError:
+    pass
+
 
 T = TypeVar('T')
 
```
