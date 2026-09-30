# [?] fix: issue where subprocess provider would crash in the background (#847)

## Summary
Severity: Unknown
Chain: Tooling
Component: ApeWorX/ape
Published: 2022-07-01
Source: https://github.com/ApeWorX/ape/commit/279200d0ff42ad365b7b0cee602cdb05abaf2efb
Type: security-commit

## Details
fix: issue where subprocess provider would crash in the background (#847)

## Patch
### src/ape/api/providers.py
```diff
@@ -1,14 +1,16 @@
 import atexit
 import ctypes
+import logging
 import platform
 import shutil
 import sys
 import time
 from abc import ABC
+from logging import FileHandler, Formatter, Logger, getLogger
 from pathlib import Path
 from signal import SIGINT, SIGTERM, signal
-from subprocess import PIPE, Popen, call
-from typing import Any, Callable, Dict, Iterator, List, Optional, Union
+from subprocess import PIPE, Popen
+from typing import Any, Dict, Iterator, List, Optional, Union
 
 from eth_abi.abi import encode_single
 from eth_typing import HexStr
@@ -41,11 +43,13 @@
 from ape.utils import (
     EMPTY_BYTES32,
     BaseInterfaceModel,
+    JoinableQueue,
     LogInputABICollection,
     abstractmethod,
     cached_property,
     gas_estimation_error_message,
     raises_not_implemented,
+    spawn,
 )
 
 
@@ -860,6 +864,9 @@ class SubprocessProvider(ProviderAPI):
     process: Optional[Popen] = None
     is_stopping: bool = False
 
+    stdout_queue: Optional[JoinableQueue] = None
+    stderr_queue: Optional[JoinableQueue] = None
+
     @property
     @abstractmethod
     def process_name(self) -> str:
@@ -883,6 +890,39 @@ def build_command(self) -> List[str]:
             List[str]: The command to pass to ``subprocess.Popen``.
         """
 
+    @property
+    def base_logs_path(self) -> Path:
+        return self.config_manager.DATA_FOLDER / self.name / "subprocess_output"
+
+    @property
+    def stdout_logs_path(self) -> Path:
+        return self.base_logs_path / "stdout.log"
+
+    @property
+    def stderr_logs_path(self) -> Path:
+        return self.base_logs_path / "stderr.log"
+
+    @cached_property
+    def _stdout_logger(self) -> Logger:
+        return self._make_logger("stdout", self.stdout_logs_path)
+
+    @cached_property
+    def _stderr_logger(self) -> Logger:
+        return self._make_logger("stderr", self.stderr_logs_path)
+
+    def _make_logger(self, name: str, path: Path):
+        logger = getLogger(f"{self.name}_{name}_subprocessProviderLogger")
+        path.parent.mkdir(parents=True, exist_ok=True)
+        if path.is_file():
+            path.unlink()
+
+        path.touch()
+        handler = FileHandler(str(path))
+        handler.setFormatter(Formatter("%(message)s"))
+        logger.addHandler(handler)
+        logger.setLevel(logging.INFO)
+        return logger
+
     def connect(self):
         """
         Start the process and connect to it.
@@ -921,7 +961,15 @@ def start(self, timeout: int = 20):
         else:
             logger.info(f"Starting '{self.process_name}' process.")
             pre_exec_fn = _linux_set_death_signal if platform.uname().system == "Linux" else None
-            self.process = _popen(*self.build_command(), preexec_fn=pre_exec_fn)
+            self.stderr_queue = JoinableQueue()
+            self.stdout_queue = JoinableQueue()
+            self.process = Popen(
+                self.build_command(), preexec_fn=pre_exec_fn, stdout=PIPE, stderr=PIPE
+            )
+            spawn(self.produce_stdout_queue)
+            spawn(self.produce_stderr_queue)
+            spawn(self.consume_stdout_queue)
+            spawn(self.consume_stderr_queue)
 
             with RPCTimeoutError(self, seconds=timeout) as _timeout:
                 while True:
@@ -931,6 +979,31 @@ def start(self, timeout: int = 20):
                     time.sleep(0.1)
                     _timeout.check()
 
+    def produce_stdout_queue(self):
+        for line in iter(self.process.stdout.readline, b""):
+            self.stdout_queue.put(line)
+            time.sleep(0)
+
+    def produce_stderr_queue(self):
+        for line in iter(self.process.stderr.readline, b""):
+            self.stderr_queue.put(line)
+            time.sleep(0)
+
+    def consume_stdout_queue(self):
+        for line in self.stdout_queue:
+            output = line.decode("utf8").strip()
+            logger.debug(output)
+            self._stdout_logger.info(output)
+            self.stdout_queue.task_done()
+            time.sleep(0)
+
+    def consume_stderr_queue(self):
+        for line in self.stderr_queue:
+            logger.debug(line.decode("utf8").strip())
+            self._stdout_logger.info(line)
+            self.stderr_queue.task_done()
+            time.sleep(0)
+
     def stop(self):
         """Kill the process."""
 
@@ -942,6 +1015,8 @@ def stop(self):
         self._kill_process()
         self.is_stopping = False
         self.process = None
+        self.stdout_queue = None
+        self.stderr_queue = None
 
     def _wait_for_popen(self, timeout: int = 30):
         if not self.process:
@@ -1010,21 +1085,6 @@ def _windows_taskkill(self) -> None:
         proc.wait(timeout=self.PROCESS_WAIT_TIMEOUT)
 
 
-pipe_kwargs = {"stdin": PIPE, "stdout": PIPE, "stderr": PIPE}
-
-
-def _popen(*cmd, preexec_fn: Optional[Callable] = None) -> Popen:
-    kwargs: Dict[str, Any] = {**pipe_kwargs}
-    if preexec_fn:
-        kwargs["preexec_fn"] = preexec_fn
-
-    return Popen([str(c) for c in [*cmd]], **kwargs)
-
-
-def _call(*args):
-    return call([*args], **pipe_kwargs)
-
-
 def _linux_set_death_signal():
     """
     Automatically sends SIGTERM to child subprocesses when parent process
```

### src/ape/utils/__init__.py
```diff
@@ -33,6 +33,7 @@
     stream_response,
 )
 from ape.utils.os import get_all_files_in_directory, get_relative_path, use_temp_sys_path
+from ape.utils.process import JoinableQueue, spawn
 from ape.utils.testing import (
     DEFAULT_NUMBER_OF_TEST_ACCOUNTS,
     DEFAULT_TEST_MNEMONIC,
@@ -65,13 +66,15 @@
     "is_array",
     "is_named_tuple",
     "is_struct",
+    "JoinableQueue",
     "load_config",
     "LogInputABICollection",
     "ManagerAccessMixin",
     "parse_type",
     "raises_not_implemented",
     "returns_array",
     "singledispatchmethod",
+    "spawn",
     "stream_response",
     "Struct",
     "StructParser",
```

### src/ape/utils/process.py
```diff
@@ -0,0 +1,49 @@
+import queue
+import threading
+import time
+
+from ape.exceptions import SubprocessTimeoutError
+
+
+class JoinableQueue(queue.Queue):
+    """
+    A queue that can be joined, useful for multi-processing.
+    Borrowed from the ``py-geth`` library.
+    """
+
+    def __iter__(self):
+        while True:
+            item = self.get()
+
+            is_stop_iteration_type = isinstance(item, type) and issubclass(item, StopIteration)
+            if isinstance(item, StopIteration) or is_stop_iteration_type:
+                return
+
+            elif isinstance(item, Exception):
+                raise item
+
+            elif isinstance(item, type) and issubclass(item, Exception):
+                raise item
+
+            yield item
+
+    def join(self, timeout=None):
+        with SubprocessTimeoutError(timeout) as _timeout:
+            while not self.empty():
+                time.sleep(0)
+                _timeout.check()
+
+
+def spawn(target, *args, **kwargs):
+    """
+    Spawn a new daemon thread. Borrowed from the ``py-geth`` library.
+    """
+
+    thread = threading.Thread(
+        target=target,
+        args=args,
+        kwargs=kwargs,
+    )
+    thread.daemon = True
+    thread.start()
+    return thread
```
