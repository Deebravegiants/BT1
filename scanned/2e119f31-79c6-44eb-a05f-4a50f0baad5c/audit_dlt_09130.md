# [?] Fix race condition in get_free_port by binding to localhost

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin-core/HWI
Published: 2026-02-11
Source: https://github.com/bitcoin-core/HWI/commit/38f55ebd0551fa6e2957289d7df0b3987150ffe0
Type: security-commit

## Details
Fix race condition in get_free_port by binding to localhost

## Patch
### test/test_device.py
```diff
@@ -68,7 +68,7 @@ def start(self):
 
         def get_free_port():
             s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
-            s.bind(("", 0))
+            s.bind(("127.0.0.1", 0))
             s.listen(1)
             port = s.getsockname()[1]
             s.close()
```
