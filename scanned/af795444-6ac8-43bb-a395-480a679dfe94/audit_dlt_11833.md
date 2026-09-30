# [?] fix: log level default value race condition (#437)

## Summary
Severity: Unknown
Chain: Tooling
Component: ApeWorX/ape
Published: 2022-01-27
Source: https://github.com/ApeWorX/ape/commit/31412082a08bdf65b6ef09193bca96731daf069c
Type: security-commit

## Details
fix: log level default value race condition (#437)

## Patch
### src/ape/cli/options.py
```diff
@@ -12,7 +12,7 @@
 )
 from ape.cli.utils import Abort
 from ape.exceptions import ContractError
-from ape.logging import LogLevel, logger
+from ape.logging import DEFAULT_LOG_LEVEL, LogLevel, logger
 from ape.managers.project import ProjectManager
 
 
@@ -82,7 +82,7 @@ def _set_level(ctx, param, value):
             "--verbosity",
             "-v",
             callback=_set_level,
-            default=LogLevel.INFO.name,
+            default=DEFAULT_LOG_LEVEL,
             metavar="LVL",
             expose_value=False,
             help=f"One of {names_str}",
```

### src/ape/logging.py
```diff
@@ -18,6 +18,7 @@ class LogLevel(Enum):
 
 logging.addLevelName(LogLevel.SUCCESS.value, LogLevel.SUCCESS.name)
 logging.SUCCESS = LogLevel.SUCCESS.value  # type: ignore
+DEFAULT_LOG_LEVEL = LogLevel.INFO.name
 
 
 def success(self, message, *args, **kws):
@@ -102,6 +103,7 @@ def __init__(self):
         self._logger = _logger
         self._web3_request_manager_logger = _get_logger("web3.RequestManager")
         self._web3_http_provider_logger = _get_logger("web3.providers.HTTPProvider")
+        self.set_level(DEFAULT_LOG_LEVEL)
 
     @property
     def level(self) -> int:
@@ -166,4 +168,4 @@ def _get_logger(name: str) -> logging.Logger:
 logger = CliLogger()
 
 
-__all__ = ["logger", "LogLevel"]
+__all__ = ["DEFAULT_LOG_LEVEL", "logger", "LogLevel"]
```
