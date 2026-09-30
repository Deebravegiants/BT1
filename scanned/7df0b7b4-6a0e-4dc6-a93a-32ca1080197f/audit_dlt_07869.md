# [?] Fix syncqueue.nim crash in the end of forward syncing process. (#6910)

## Summary
Severity: Unknown
Chain: Ethereum
Component: status-im/nimbus-eth2
Published: 2025-02-09
Source: https://github.com/status-im/nimbus-eth2/commit/ca6ca8395c5f2049b14008935b290e9ced2a5678
Type: security-commit

## Details
Fix syncqueue.nim crash in the end of forward syncing process. (#6910)

## Patch
### beacon_chain/sync/sync_queue.nim
```diff
@@ -780,20 +780,21 @@ proc push*[T](
   ## Push successful result to queue ``sq``.
   mixin updateScore, updateStats, getStats
 
+  template findPosition(sq, sr: untyped): SyncPosition =
+    sq.find(sr).valueOr:
+      debug "Request is no more relevant",
+            request = sr, sync_ident = sq.ident, topics = "syncman"
+      # Request is not in queue anymore, probably reset happened.
+      return
+
   # This is backpressure handling algorithm, this algorithm is blocking
   # all pending `push` requests if `request` is not in range.
   var
     position =
       block:
         var pos: SyncPosition
         while true:
-          pos = sq.find(sr).valueOr:
-            debug "Request is no more relevant",
-                  request = sr,
-                  sync_ident = sq.ident,
-                  topics = "syncman"
-            # Request is not in queue anymore, probably reset happened.
-            return
+          pos = sq.findPosition(sr)
 
           if pos.qindex == 0:
             # Exiting loop when request is first in queue.
@@ -816,20 +817,18 @@ proc push*[T](
 
   await sq.lock.acquire()
   try:
-    block:
-      position = sq.find(sr).valueOr:
-        # Queue has advanced, the request is no longer relevant.
-        debug "Request is no more relevant",
-              request = sr,
-              sync_ident = sq.ident,
-              topics = "syncman"
-        return
+    position = sq.findPosition(sr)
 
     if not(isNil(processingCb)):
       processingCb()
 
     let pres = await sq.process(sr, data, blobs, maybeFinalized)
 
+    # We need to update position, because while we waiting for `process()` to
+    # complete - clearAndWakeup() could be invoked which could clean whole the
+    # queue (invalidating all the positions).
+    position = sq.findPosition(sr)
+
     case pres.code
     of SyncProcessError.Empty:
       # Empty responses does not affect failures count
```
