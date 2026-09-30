# [?] fix race condition causing initialize_swap_manager assert to fail by waiting for trigger_pairs_updated_threadsafe to set the is_initialized event befo

## Summary
Severity: Unknown
Chain: Bitcoin
Component: spesmilo/electrum
Published: 2025-04-08
Source: https://github.com/spesmilo/electrum/commit/216bfe3b50ce70948e7e62c5af143f6091737756
Type: security-commit

## Details
fix race condition causing initialize_swap_manager assert to fail by waiting for trigger_pairs_updated_threadsafe to set the is_initialized event before returning if it is not running on the aio loop

## Patch
### electrum/submarine_swaps.py
```diff
@@ -6,6 +6,7 @@
 from decimal import Decimal
 import math
 import time
+import concurrent.futures
 
 import attr
 import aiohttp
@@ -952,12 +953,19 @@ def update_pairs(self, pairs):
         self.trigger_pairs_updated_threadsafe()
 
     def trigger_pairs_updated_threadsafe(self):
+        future = concurrent.futures.Future()
         def trigger():
             self.is_initialized.set()
             self.pairs_updated.set()
             self.pairs_updated.clear()
-        loop = get_asyncio_loop()
-        loop.call_soon_threadsafe(trigger)
+            future.set_result(None)
+        asyncio_loop = get_asyncio_loop()
+        if get_running_loop() == asyncio_loop:
+            trigger()  # this is running on the asyncio event loop
+        else:
+            asyncio_loop.call_soon_threadsafe(trigger)
+            # block until the event loop has run the trigger function
+            _ = future.result()
 
     def server_maybe_trigger_liquidity_update(self) -> None:
         """
```
