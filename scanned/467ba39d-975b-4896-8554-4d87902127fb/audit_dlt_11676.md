# [?] hw_wallet: fix crash on exit if device unpairing fails

## Summary
Severity: Unknown
Chain: Bitcoin
Component: spesmilo/electrum
Published: 2026-07-03
Source: https://github.com/spesmilo/electrum/commit/b0ae14a5b41164f98a4e1685541f084e71fdecfe
Type: security-commit

## Details
hw_wallet: fix crash on exit if device unpairing fails

On wallet close, the close_wallet hook unpaired the device before
stopping the keystore TaskThread. Unpairing does device I/O and can
raise, e.g. if the device was unplugged while the wallet was open:

    Plugin error. plugin: trezor, hook: close_wallet
    Traceback (most recent call last):
      File "electrum/plugin.py", line 833, in run_hook
        r = f(*args)
      File "electrum/hw_wallet/plugin.py", line 89, in close_wallet
        self.device_manager().unpair_pairing_code(keystore.pairing_code())
      File "electrum/plugin.py", line 1118, in unpair_pairing_code
        self._close_client(_id)
      File "electrum/plugin.py", line 1134, in _close_client
        client.close()
      ...
      File "electrum/plugins/trezor/clientbase.py", line 286, in close
        self.client.lock()
      ...
    trezorlib.transport.bridge.BridgeException: trezord: acquire/62/null failed with code 400: device not found

run_hook() swallows the exception, so the thread was never stopped.
A still-running QThread (child of the wallet window) at interpreter
shutdown then makes Qt abort the process:

    QThread: Destroyed while thread '' is still running

Stop the thread before unpairing, and make DeviceMgr._close_client
treat client.close() as best-effort, as closing a missing device is
a normal condition during cleanup.

## Patch
### electrum/hw_wallet/plugin.py
```diff
@@ -86,9 +86,11 @@ def create_device_from_hid_enumeration(self, d: dict, *, product_key) -> Optiona
     def close_wallet(self, wallet: 'Abstract_Wallet'):
         for keystore in wallet.get_keystores():
             if isinstance(keystore, self.keystore_class):
-                self.device_manager().unpair_pairing_code(keystore.pairing_code())
+                # stop the thread first: if unpairing raises, the thread must not be leaked,
+                # as a still-running QThread would make Qt abort() the process at shutdown
                 if keystore.thread:
                     keystore.thread.stop()
+                self.device_manager().unpair_pairing_code(keystore.pairing_code())
 
     def get_client(self, keystore: 'Hardware_KeyStore', force_pair: bool = True, *,
                    devices: Sequence['Device'] = None,
```

### electrum/plugin.py
```diff
@@ -1131,7 +1131,12 @@ def _close_client(self, id_):
             if fut := self._ongoing_timeout_checks.pop(id_, None):
                 fut.cancel()
         if client:
-            client.close()
+            try:
+                client.close()
+            except Exception as e:
+                # closing is best-effort: it does device I/O, which can fail,
+                # e.g. if the device was unplugged
+                self.logger.info(f"failed to close hardware client cleanly: {e!r}")
 
     def _client_by_id(self, id_) -> Optional['HardwareClientBase']:
         with self.lock:
```
