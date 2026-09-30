# [?] Fix reentrancy detector

## Summary
Severity: Unknown
Chain: Tooling
Component: crytic/slither
Published: 2019-08-16
Source: https://github.com/crytic/slither/commit/e2ed64c97bf8d42b89f860b95e5842d041b8a99e
Type: security-commit

## Details
Fix reentrancy detector

## Patch
### slither/slithir/operations/send.py
```diff
@@ -17,6 +17,9 @@ def __init__(self, destination, value, result):
 
         self._call_value = value
 
+    def can_send_eth(self):
+        return True
+
     @property
     def call_value(self):
         return self._call_value
```

### slither/slithir/operations/transfer.py
```diff
@@ -11,6 +11,8 @@ def __init__(self, destination, value):
 
         self._call_value = value
 
+    def can_send_eth(self):
+        return True
 
     @property
     def call_value(self):
```
