# [?] fix: `ConfigManager` would crash on attribute access and be un-recoverable when temporary poorly configured (#2627)

## Summary
Severity: Unknown
Chain: Tooling
Component: ApeWorX/ape
Published: 2025-05-29
Source: https://github.com/ApeWorX/ape/commit/2eef88a47f42bccfa4b5d898248a85865454f056
Type: security-commit

## Details
fix: `ConfigManager` would crash on attribute access and be un-recoverable when temporary poorly configured (#2627)

## Patch
### src/ape/_cli.py
```diff
@@ -13,7 +13,7 @@
 import yaml
 
 from ape.cli.options import ape_cli_context
-from ape.exceptions import Abort, ApeException, handle_ape_exception
+from ape.exceptions import Abort, ApeAttributeError, ApeException, handle_ape_exception
 from ape.logging import logger
 
 _DIFFLIB_CUT_OFF = 0.6
@@ -84,11 +84,25 @@ def format_commands(self, ctx, formatter) -> None:
     def invoke(self, ctx) -> Any:
         try:
             return super().invoke(ctx)
+
         except click.UsageError as err:
             self._suggest_cmd(err)
+
         except ApeException as err:
             path = ctx.obj.local_project.path
 
+            # Extract more interesting ApeException.
+            err_to_show = err
+            while isinstance(err_to_show, ApeException):
+                if (
+                    not isinstance(err_to_show, ApeAttributeError)
+                    or err_to_show.base_err is None
+                    or not isinstance(err_to_show.base_err, ApeException)
+                ):
+                    break
+
+                err_to_show = err_to_show.base_err
+
             # NOTE: isinstance check for type-checkers.
             if isinstance(path, Path) and handle_ape_exception(err, (path,)):
                 # All exc details already outputted.
```

### src/ape/api/config.py
```diff
@@ -472,7 +472,7 @@ def validate_file(cls, path: Path, **overrides) -> "ApeConfig":
         except ValidationError as err:
             if path.suffix == ".json":
                 # TODO: Support JSON configs here.
-                raise  # The validation error as-is
+                raise ConfigError(f"{err}") from err
 
             if final_msg := _get_problem_with_config(err.errors(), path):
                 raise ConfigError(final_msg)
```

### src/ape/api/networks.py
```diff
@@ -391,19 +391,20 @@ def default_network_name(self) -> str:
             # Was set programmatically.
             return network
 
-        elif network := self.config.get("default_network"):
+        networks = self.networks
+        if network := self.config.get("default_network"):
             # Default found in config. Ensure is an installed network.
-            if network in self.networks:
+            if network in networks:
                 return network
 
-        if LOCAL_NETWORK_NAME in self.networks:
+        if LOCAL_NETWORK_NAME in networks:
             # Default to the LOCAL_NETWORK_NAME, at last resort.
             return LOCAL_NETWORK_NAME
 
-        elif len(self.networks) >= 1:
+        elif len(networks) >= 1:
             # Use the first network.
-            key = next(iter(self.networks.keys()))
-            return self.networks[key].name
+            key = next(iter(networks.keys()))
+            return networks[key].name
 
         # Very unlikely scenario.
         raise NetworkError("No networks found.")
```

### src/ape/api/providers.py
```diff
@@ -1082,7 +1082,10 @@ def _disconnect_atexit(self):
         if self.background:
             return
 
-        self.disconnect()
+        try:
+            self.disconnect()
+        except Exception as err:
+            logger.error(f"Error while disconnecting: {err}")
 
     def disconnect(self):
         """
```

### src/ape/contracts/base.py
```diff
@@ -1136,7 +1136,7 @@ def _view_methods_(self) -> dict[str, ContractCallHandler]:
             }
         except Exception as err:
             # NOTE: Must raise AttributeError for __attr__ method or will seg fault
-            raise ApeAttributeError(str(err)) from err
+            raise ApeAttributeError(str(err), base_err=err) from err
 
     @cached_property
     def _mutable_methods_(self) -> dict[str, ContractTransactionHandler]:
@@ -1155,7 +1155,7 @@ def _mutable_methods_(self) -> dict[str, ContractTransactionHandler]:
             }
         except Exception as err:
             # NOTE: Must raise AttributeError for __attr__ method or will seg fault
-            raise ApeAttributeError(str(err)) from err
+            raise ApeAttributeError(str(err), base_err=err) from err
 
     def call_view_method(self, method_name: str, *args, **kwargs) -> Any:
         """
@@ -1295,7 +1295,7 @@ def _events_(self) -> dict[str, list[ContractEvent]]:
             }
         except Exception as err:
             # NOTE: Must raise AttributeError for __attr__ method or will seg fault
-            raise ApeAttributeError(str(err)) from err
+            raise ApeAttributeError(str(err), base_err=err) from err
 
     @cached_property
     def _errors_(self) -> dict[str, list[type[CustomError]]]:
@@ -1337,7 +1337,7 @@ def _errors_(self) -> dict[str, list[type[CustomError]]]:
 
         except Exception as err:
             # NOTE: Must raise AttributeError for __attr__ method or will seg fault
-            raise ApeAttributeError(str(err)) from err
+            raise ApeAttributeError(str(err), base_err=err) from err
 
     def __dir__(self) -> list[str]:
         """
```

### src/ape/exceptions.py
```diff
@@ -495,6 +495,10 @@ class ApeAttributeError(ProjectError, AttributeError):
     Raised when trying to access items via ``.`` access.
     """
 
+    def __init__(self, msg: str, base_err: Optional[Exception] = None):
+        self.base_err = base_err
+        super().__init__(msg)
+
 
 class UnknownVersionError(ProjectError):
     """
```

### src/ape/managers/config.py
```diff
@@ -89,6 +89,9 @@ def global_config(self) -> ApeConfig:
         """
         return self.load_global_config()
 
+    def get_config(self, name: str) -> ApeConfig:
+        return self.local_project.config.get_config(name)
+
     def load_global_config(self) -> ApeConfig:
         path = self.DATA_FOLDER / CONFIG_FILE_NAME
         return ApeConfig.validate_file(path) if path.is_file() else ApeConfig.model_validate({})
```

### src/ape/managers/project.py
```diff
@@ -2139,8 +2139,15 @@ def reconfigure(self, **overrides):
             # Delete cached property.
             del self.__dict__["config"]
 
+        original_override = self._config_override
         self._config_override = overrides
-        _ = self.config
+        try:
+            _ = self.config
+        except Exception:
+            # Ensure changes don't persist.
+            self._config_override = original_override
+            raise  # Whatever error it is
+
         self._invalidate_project_dependent_caches()
 
     def extract_manifest(self) -> PackageManifest:
@@ -2438,6 +2445,9 @@ def _contract_sources(self) -> list[ContractSource]:
     @cached_property
     def _deduced_contracts_folder(self) -> Path:
         # NOTE: This helper is only called if not configured and not ordinary.
+        return self._deduce_contracts_folder()
+
+    def _deduce_contracts_folder(self) -> Path:
         if not self.path.is_dir():
             # Not even able to try.
             return self.path
```

### src/ape/pytest/runners.py
```diff
@@ -7,7 +7,7 @@
 from rich import print as rich_print
 
 from ape.exceptions import ConfigError, ProviderNotConnectedError
-from ape.logging import LogLevel
+from ape.logging import LogLevel, logger
 from ape.pytest.utils import Scope
 from ape.utils.basemodel import ManagerAccessMixin
 
@@ -361,8 +361,12 @@ def _log_tracing_support(self, terminalreporter, extra_warning: str):
 
     def pytest_unconfigure(self):
         if self._provider_is_connected and self.config_wrapper.disconnect_providers_after:
-            self._provider_context.disconnect_all()
-            self._provider_is_connected = False
+            try:
+                self._provider_context.disconnect_all()
+            except Exception as err:
+                logger.error(f"Failed to disconnect {self}: {err}")
+            else:
+                self._provider_is_connected = False
 
         # NOTE: Clearing the state is helpful for pytester-based tests,
         #  which may run pytest many times in-process.
```

### src/ape/utils/basemodel.py
```diff
@@ -123,7 +123,7 @@ def wrapper(*args, **kwargs):
         except Exception as err:
             # Wrap the exception in AttributeError
             logger.log_debug_stack_trace()
-            raise ApeAttributeError(f"{err}") from err
+            raise ApeAttributeError(f"{err}", base_err=err) from err
 
     return wrapper
 
@@ -478,7 +478,7 @@ def __getitem__(self, name: Any) -> Any:
         return get_item_with_extras(self, name)
 
 
-def get_attribute_with_extras(obj: Any, name: str) -> Any:
+def get_attribute_with_extras(obj: Any, name: str, coerce_attr_error: bool = True) -> Any:
     _assert_not_ipython_check(name)
     if _recursion_checker.check(name):
         # Prevent segfaults.
@@ -530,7 +530,7 @@ def get_attribute_with_extras(obj: Any, name: str) -> Any:
 
         except Exception as err:
             _recursion_checker.reset(name)
-            raise ApeAttributeError(f"{name} - {err}") from err
+            raise ApeAttributeError(f"{name} - {err}", base_err=err) from err
 
     # The error message mentions the alternative mappings,
     # such as a contract-type map.
@@ -548,12 +548,18 @@ def get_attribute_with_extras(obj: Any, name: str) -> Any:
         if suffix not in message:
             if message and message[-1] not in (".", "?", "!"):
                 message = f"{message}."
+
             message = f"{message} {suffix}"
 
     _recursion_checker.reset(name)
     if message and message[-1] not in (".", "?", "!"):
         message = f"{message}."
 
+    if base_err and not coerce_attr_error:
+        raise base_err
+
+    # Coerce whatever error to automatically be an AttributeError
+    # (required for __getattr__ or must handle independently).
     attr_err = ApeAttributeError(message)
     if base_err:
         raise attr_err from base_err
```

### src/ape_ethereum/provider.py
```diff
@@ -1753,6 +1753,14 @@ def _create_web3(
         providers.append(lambda: WebsocketProvider(endpoint_uri=ws))
 
     provider = AutoProvider(potential_providers=providers)
+
+    # TODO: Getting attribute error without this. Figure out why and do proper fix.
+    class MockBatchingContext:
+        def get(self, *args, **kwargs):
+            return None
+
+    provider._batching_context = MockBatchingContext()  # type: ignore
+
     return Web3(provider, middleware=[])
 
 
```

### src/ape_test/provider.py
```diff
@@ -125,6 +125,16 @@ def ethereum_tester(self, value):
         self._ethereum_tester = value
         self._backend = value.backend
 
+    @property
+    def _batching_context(self):  # type: ignore
+        # TODO: Figure out correct way; remove this hack
+
+        class MockBatchingContext:
+            def get(self, *args, **kwargs):
+                return None
+
+        return MockBatchingContext()
+
     @property
     def backend(self) -> "ApeEVMBackend":
         if self._backend is None:
```
