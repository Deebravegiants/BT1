# [?] util.CallbackManager: follow-up prev: fix deadlock

## Summary
Severity: Unknown
Chain: Bitcoin
Component: spesmilo/electrum
Published: 2026-01-21
Source: https://github.com/spesmilo/electrum/commit/cc4611f43d726ba61acbc9e8d83989405709b574
Type: security-commit

## Details
util.CallbackManager: follow-up prev: fix deadlock

## Patch
### electrum/util.py
```diff
@@ -1954,7 +1954,7 @@ class CallbackManager(Logger):
 
     def __init__(self):
         Logger.__init__(self)
-        self.callback_lock = threading.Lock()
+        self.callback_lock = threading.RLock()
         self._wcallbacks = defaultdict(set)  # type: Dict[str, Set[weakref.ref[Callable]]]  # note: needs self.callback_lock
 
     @staticmethod
@@ -1976,6 +1976,7 @@ def register_callback(self, cb: Callable, events: Sequence[str]) -> None:
     def unregister_callback(self, cb: Callable) -> None:
         wcb = self._wcb_from_any_callback(cb)
         with self.callback_lock:
+            # note: ^ callback_lock needs to be re-entrant, as we can now trigger __del__, which also takes the lock
             for callbacks in self._wcallbacks.values():
                 if wcb in callbacks:
                     callbacks.remove(wcb)
```
