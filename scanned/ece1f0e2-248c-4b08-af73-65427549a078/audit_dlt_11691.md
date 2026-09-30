# [?] wallet: fix race condition that inhibits proper call of set_up_to_date

## Summary
Severity: Unknown
Chain: Bitcoin
Component: spesmilo/electrum
Published: 2022-09-26
Source: https://github.com/spesmilo/electrum/commit/444dc7fb7f6792450ce2ad89df26cca89d46940e
Type: security-commit

## Details
wallet: fix race condition that inhibits proper call of set_up_to_date

## Patch
### electrum/wallet.py
```diff
@@ -353,6 +353,7 @@ def __init__(self, db: WalletDB, storage: Optional[WalletStorage], *, config: Si
         # true when synchronized. this is stricter than adb.is_up_to_date():
         # to-be-generated (HD) addresses are also considered here (gap-limit-roll-forward)
         self._up_to_date = False
+        self._adb_uptodate_just_changed = False
 
         self.test_addresses_sanity()
         self.register_callbacks()
@@ -385,8 +386,10 @@ async def do_synchronize_loop(self):
             #       have history that are mined and SPV-verified.
             num_new_addrs = await run_in_thread(self.synchronize)
             up_to_date = self.adb.is_up_to_date() and num_new_addrs == 0
-            if self.is_up_to_date() != up_to_date:
-                self.set_up_to_date(up_to_date)
+            if self.is_up_to_date() != up_to_date or self._adb_uptodate_just_changed:
+                 self.set_up_to_date(up_to_date)
+            if self._adb_uptodate_just_changed:
+                self._adb_uptodate_just_changed = False
 
     def save_db(self):
         if self.storage:
@@ -475,6 +478,12 @@ def set_up_to_date(self, up_to_date: bool) -> None:
         if status_changed:
             self.logger.info(f'set_up_to_date: {up_to_date}')
 
+    @event_listener
+    def on_event_adb_set_up_to_date(self, adb):
+        if self.adb != adb:
+            return
+        self._adb_uptodate_just_changed = True
+
     @event_listener
     def on_event_adb_added_tx(self, adb, tx_hash):
         if self.adb != adb:
```
