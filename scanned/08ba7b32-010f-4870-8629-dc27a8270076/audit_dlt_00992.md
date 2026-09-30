# [?] fix[ux]: fix relpath compiler panic on windows (#4228)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2024-10-04
Source: https://github.com/vyperlang/vyper/commit/c7669bd2ebe2c405aa5572b58311b51517568143
Type: security-commit

## Details
fix[ux]: fix relpath compiler panic on windows (#4228)

fix a bug where `os.path.relpath()` raises an exception on window
- when the source path and the destination path are on different
drives. this commit introduces the helper function `safe_relpath()`,
which tries hard to construct a relpath (using `os.path.relpath()`),
but falls back to the original path (which might be an absolute path)
instead of raising an exception.

references:
- https://docs.python.org/3/library/os.path.html#os.path.relpath

## Patch
### vyper/compiler/output_bundle.py
```diff
@@ -1,7 +1,6 @@
 import importlib
 import io
 import json
-import os
 import zipfile
 from dataclasses import dataclass
 from functools import cached_property
@@ -13,7 +12,7 @@
 from vyper.compiler.settings import Settings
 from vyper.exceptions import CompilerPanic
 from vyper.semantics.analysis.module import _is_builtin
-from vyper.utils import get_long_version
+from vyper.utils import get_long_version, safe_relpath
 
 # data structures and routines for constructing "output bundles",
 # basically reproducible builds of a vyper contract, with varying
@@ -62,7 +61,7 @@ def compiler_inputs(self) -> dict[str, CompilerInput]:
 
         sources = {}
         for c in inputs:
-            path = os.path.relpath(c.resolved_path)
+            path = safe_relpath(c.resolved_path)
             # note: there should be a 1:1 correspondence between
             # resolved_path and source_id, but for clarity use resolved_path
             # since it corresponds more directly to search path semantics.
@@ -73,7 +72,7 @@ def compiler_inputs(self) -> dict[str, CompilerInput]:
     @cached_property
     def compilation_target_path(self):
         p = PurePath(self.compiler_data.file_input.resolved_path)
-        p = os.path.relpath(p)
+        p = safe_relpath(p)
         return _anonymize(p)
 
     @cached_property
@@ -121,7 +120,7 @@ def used_search_paths(self) -> list[str]:
         sps = [sp for sp, count in tmp.items() if count > 0]
         assert len(sps) > 0
 
-        return [_anonymize(os.path.relpath(sp)) for sp in sps]
+        return [_anonymize(safe_relpath(sp)) for sp in sps]
 
 
 class OutputBundleWriter:
```

### vyper/semantics/analysis/module.py
```diff
@@ -1,4 +1,3 @@
-import os
 from pathlib import Path, PurePath
 from typing import Any, Optional
 
@@ -58,7 +57,7 @@
 from vyper.semantics.types.function import ContractFunctionT
 from vyper.semantics.types.module import ModuleT
 from vyper.semantics.types.utils import type_from_annotation
-from vyper.utils import OrderedSet
+from vyper.utils import OrderedSet, safe_relpath
 
 
 def analyze_module(
@@ -921,7 +920,7 @@ def _load_builtin_import(level: int, module_str: str) -> tuple[CompilerInput, In
     # hygiene: convert to relpath to avoid leaking user directory info
     # (note Path.relative_to cannot handle absolute to relative path
     # conversion, so we must use the `os` module).
-    builtins_path = os.path.relpath(builtins_path)
+    builtins_path = safe_relpath(builtins_path)
 
     search_path = Path(builtins_path).parent.parent.parent
     # generate an input bundle just because it knows how to build paths.
```

### vyper/utils.py
```diff
@@ -4,6 +4,7 @@
 import enum
 import functools
 import hashlib
+import os
 import sys
 import time
 import traceback
@@ -599,3 +600,12 @@ def annotate_source_code(
     cleanup_lines += [""] * (num_lines - len(cleanup_lines))
 
     return "\n".join(cleanup_lines)
+
+
+def safe_relpath(path):
+    try:
+        return os.path.relpath(path)
+    except ValueError:
+        # on Windows, if path and curdir are on different drives, an exception
+        # can be thrown
+        return path
```
