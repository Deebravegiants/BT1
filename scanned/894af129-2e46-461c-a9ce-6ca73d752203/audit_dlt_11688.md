# [?] fix crash when trying to display channel backup details

## Summary
Severity: Unknown
Chain: Bitcoin
Component: spesmilo/electrum
Published: 2023-01-25
Source: https://github.com/spesmilo/electrum/commit/23adb53572a078dbb7f9fb5d51183130463fee03
Type: security-commit

## Details
fix crash when trying to display channel backup details

## Patch
### electrum/lnchannel.py
```diff
@@ -509,6 +509,9 @@ def get_capacity(self):
     def is_backup(self):
         return True
 
+    def get_remote_alias(self) -> Optional[bytes]:
+        return None
+
     def create_sweeptxs_for_their_ctx(self, ctx):
         return {}
 
```
