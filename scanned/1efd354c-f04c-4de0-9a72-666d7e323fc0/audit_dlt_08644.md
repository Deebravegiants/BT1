# [?] Fix negative plot sync durations not crashing the harvester (#17444)

## Summary
Severity: Unknown
Chain: Chia
Component: Chia-Network/chia-blockchain
Published: 2024-02-02
Source: https://github.com/Chia-Network/chia-blockchain/commit/23e003aaaee17b4c4f0972aaa1935b994d703e4e
Type: security-commit

## Details
Fix negative plot sync durations not crashing the harvester (#17444)

* Fix negative plot sync durations

* Remove unnecessary try/except

## Patch
### chia/plot_sync/sender.py
```diff
@@ -299,7 +299,7 @@ def sync_done(self, removed: List[Path], duration: float) -> None:
         self._add_list_batched(ProtocolMessageTypes.plot_sync_keys_missing, PlotSyncPathList, no_key_list)
         duplicates_list = self._plot_manager.get_duplicates().copy()
         self._add_list_batched(ProtocolMessageTypes.plot_sync_duplicates, PlotSyncPathList, duplicates_list)
-        self._add_message(ProtocolMessageTypes.plot_sync_done, PlotSyncDone, uint64(int(duration)))
+        self._add_message(ProtocolMessageTypes.plot_sync_done, PlotSyncDone, uint64(max(0, int(duration))))
 
     def _finalize_sync(self) -> None:
         log.debug(f"_finalize_sync {self}")
```

### tests/plot_sync/test_sender.py
```diff
@@ -107,3 +107,10 @@ def new_response_message(sync_id: int, message_id: int, message_type: ProtocolMe
     # Test invalid message-type
     sender._response = new_expected_response(3, 0, ProtocolMessageTypes.plot_sync_start)
     assert not sender.set_response(new_response_message(3, 0, ProtocolMessageTypes.plot_sync_loaded))
+
+
+def test_sync_done_with_negative_duration_does_not_crash(bt: BlockTools) -> None:
+    sender = Sender(bt.plot_manager, HarvestingMode.CPU)
+    sender.sync_start(0, True)
+
+    sender.sync_done([], -1)
```
