# [?] hww: fix crash when disabling keystore for hww (was unimplemented for Hardware_Keystore)

## Summary
Severity: Unknown
Chain: Bitcoin
Component: spesmilo/electrum
Published: 2025-08-13
Source: https://github.com/spesmilo/electrum/commit/0a2cd5fdadf20a11ad0325ebcc13879b12ada1dc
Type: security-commit

## Details
hww: fix crash when disabling keystore for hww (was unimplemented for Hardware_Keystore)
also preserve derivation path and root fingerprint for watch-only keystore.

## Patch
### electrum/keystore.py
```diff
@@ -640,7 +640,11 @@ def __init__(self, d: dict):
         self.xprv = d.get('xprv')
 
     def watching_only_keystore(self):
-        return BIP32_KeyStore({'xpub':self.xpub})
+        return BIP32_KeyStore({
+            'xpub': self.xpub,
+            'root_fingerprint': self.get_root_fingerprint(),
+            'derivation_prefix': self.get_derivation_prefix(),
+        })
 
     def format_seed(self, seed):
         return ' '.join(seed.split())
@@ -895,6 +899,13 @@ def __init__(self, d):
         self.handler = None  # type: Optional[HardwareHandlerBase]
         run_hook('init_keystore', self)
 
+    def watching_only_keystore(self):
+        return BIP32_KeyStore({
+            'xpub': self.xpub,
+            'root_fingerprint': self.get_root_fingerprint(),
+            'derivation_prefix': self.get_derivation_prefix(),
+        })
+
     def set_label(self, label: Optional[str]) -> None:
         self.label = label
 
@@ -914,13 +925,13 @@ def dump(self):
             'xpub': self.xpub,
             'derivation': self.get_derivation_prefix(),
             'root_fingerprint': self.get_root_fingerprint(),
-            'label':self.label,
+            'label': self.label,
             'soft_device_id': self.soft_device_id,
         }
 
     def is_watching_only(self):
-        '''The wallet is not watching-only; the user will be prompted for
-        pin and passphrase as appropriate when needed.'''
+        """The wallet is not watching-only; the user will be prompted for
+        pin and passphrase as appropriate when needed."""
         assert not self.has_seed()
         return False
 
```
