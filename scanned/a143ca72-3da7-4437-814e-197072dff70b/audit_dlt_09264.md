# [?] fix: add missing test for memory allocation overflow (#3650)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2023-10-20
Source: https://github.com/vyperlang/vyper/commit/ed0b1e0ac8ddb47019efcff4b692ff6470fc6a04
Type: security-commit

## Details
fix: add missing test for memory allocation overflow (#3650)

should have been added in 68da04b2e9e0 but the file was not committed

## Patch
### tests/parser/features/test_memory_alloc.py
```diff
@@ -0,0 +1,16 @@
+import pytest
+
+from vyper.compiler import compile_code
+from vyper.exceptions import MemoryAllocationException
+
+
+def test_memory_overflow():
+    code = """
+@external
+def zzz(x: DynArray[uint256, 2**59]):  # 2**64 / 32 bytes per word == 2**59
+    y: uint256[7] = [0,0,0,0,0,0,0]
+
+    y[6] = y[5]
+    """
+    with pytest.raises(MemoryAllocationException):
+        compile_code(code)
```
