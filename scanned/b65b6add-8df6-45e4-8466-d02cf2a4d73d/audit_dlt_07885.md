# [?] Fix integer overflow issue in sync_manager. (#2564)

## Summary
Severity: Unknown
Chain: Ethereum
Component: status-im/nimbus-eth2
Published: 2021-05-18
Source: https://github.com/status-im/nimbus-eth2/commit/5b5ea2e813d2066d37b936f8394d80c64ecf58a5
Type: security-commit

## Details
Fix integer overflow issue in sync_manager. (#2564)

* Make Refactor rewind point assignment more concrete.

* Fix overflow issue in getRewindPoint().
Add tests.

## Patch
### beacon_chain/sync/sync_manager.nim
```diff
@@ -15,7 +15,8 @@ import ../spec/[datatypes, digest, helpers, eth2_apis/callsigs_types],
 
 import ../gossip_processing/gossip_to_consensus
 import ../consensus_object_pools/block_pools_types
-export datatypes, digest, chronos, chronicles, results, block_pools_types
+export datatypes, digest, chronos, chronicles, results, block_pools_types,
+       helpers
 
 logScope:
   topics = "syncman"
@@ -432,40 +433,86 @@ proc toDebtsQueue[T](sq: SyncQueue[T], sr: SyncRequest[T]) =
 
 proc getRewindPoint*[T](sq: SyncQueue[T], failSlot: Slot,
                         finalizedSlot: Slot): Slot =
+  # Calculate the latest finalized epoch.
+  let finalizedEpoch = compute_epoch_at_slot(finalizedSlot)
+
+  # Calculate failure epoch.
+  let failEpoch = compute_epoch_at_slot(failSlot)
+
   # Calculate exponential rewind point in number of epochs.
   let epochCount =
     if sq.rewind.isSome():
       let rewind = sq.rewind.get()
       if failSlot == rewind.failSlot:
         # `MissingParent` happened at same slot so we increase rewind point by
         # factor of 2.
-        let epochs = rewind.epochCount * 2
-        sq.rewind = some(RewindPoint(failSlot: failSlot, epochCount: epochs))
-        epochs
+        if failEpoch > finalizedEpoch:
+          let rewindPoint = rewind.epochCount shl 1
+          if rewindPoint < rewind.epochCount:
+            # If exponential rewind point produces `uint64` overflow we will
+            # make rewind to latest finalized epoch.
+            failEpoch - finalizedEpoch
+          else:
+            if (failEpoch < rewindPoint) or
+               (failEpoch - rewindPoint < finalizedEpoch):
+              # If exponential rewind point points to position which is far
+              # behind latest finalized epoch.
+              failEpoch - finalizedEpoch
+            else:
+              rewindPoint
+        else:
+          warn "Trying to rewind over the last finalized epoch",
+               finalized_slot = finalizedSlot, fail_slot = failSlot,
+               finalized_epoch = finalizedEpoch, fail_epoch = failEpoch,
+               rewind_epoch_count = rewind.epochCount,
+               finalized_epoch = finalizedEpoch
+          0'u64
       else:
         # `MissingParent` happened at different slot so we going to rewind for
         # 1 epoch only.
-        sq.rewind = some(RewindPoint(failSlot: failSlot, epochCount: 1'u64))
-        1'u64
+        if (failEpoch < 1'u64) or (failEpoch - 1'u64 < finalizedEpoch):
+          warn "Сould not rewind further than the last finalized epoch",
+               finalized_slot = finalizedSlot, fail_slot = failSlot,
+               finalized_epoch = finalizedEpoch, fail_epoch = failEpoch,
+               rewind_epoch_count = rewind.epochCount,
+               finalized_epoch = finalizedEpoch
+          0'u64
+        else:
+          1'u64
     else:
       # `MissingParent` happened first time.
-      sq.rewind = some(RewindPoint(failSlot: failSlot, epochCount: 1'u64))
-      1'u64
-
-  # Calculate the latest finalized epoch.
-  let finalizedEpoch = compute_epoch_at_slot(finalizedSlot)
+      if (failEpoch < 1'u64) or (failEpoch - 1'u64 < finalizedEpoch):
+        warn "Сould not rewind further than the last finalized epoch",
+             finalized_slot = finalizedSlot, fail_slot = failSlot,
+             finalized_epoch = finalizedEpoch, fail_epoch = failEpoch,
+             finalized_epoch = finalizedEpoch
+        0'u64
+      else:
+        1'u64
 
-  # Calculate the rewind epoch, which should not be less than the latest
-  # finalized epoch.
-  let rewindEpoch =
-    block:
-      let failEpoch = compute_epoch_at_slot(failSlot)
-      if failEpoch < finalizedEpoch + epochCount:
+  # echo "epochCount = ", epochCount
+
+  if epochCount == 0'u64:
+    warn "Unable to continue syncing, please restart the node",
+         finalized_slot = finalizedSlot, fail_slot = failSlot,
+         finalized_epoch = finalizedEpoch, fail_epoch = failEpoch,
+         finalized_epoch = finalizedEpoch
+    # Calculate the rewind epoch, which will be equal to last rewind point or
+    # finalizedEpoch
+    let rewindEpoch =
+      if sq.rewind.isNone():
         finalizedEpoch
       else:
-        failEpoch - epochCount
-
-  compute_start_slot_at_epoch(rewindEpoch)
+        compute_epoch_at_slot(sq.rewind.get().failSlot) -
+          sq.rewind.get().epochCount
+    compute_start_slot_at_epoch(rewindEpoch)
+  else:
+    # Calculate the rewind epoch, which should not be less than the latest
+    # finalized epoch.
+    let rewindEpoch = failEpoch - epochCount
+    # Update and save new rewind point in SyncQueue.
+    sq.rewind = some(RewindPoint(failSlot: failSlot, epochCount: epochCount))
+    compute_start_slot_at_epoch(rewindEpoch)
 
 proc push*[T](sq: SyncQueue[T], sr: SyncRequest[T],
               data: seq[SignedBeaconBlock]) {.async, gcsafe.} =
```

### tests/test_sync_manager.nim
```diff
@@ -1,5 +1,6 @@
 {.used.}
 
+import std/strutils
 import unittest2
 import chronos
 import ../beacon_chain/gossip_processing/gossip_to_consensus,
@@ -515,3 +516,60 @@ suite "SyncManager test suite":
       checkResponse(r22, @[chain[4], chain[5]]) == false
       checkResponse(r22, @[chain[4]]) == false
       checkResponse(r22, @[chain[3], chain[1]]) == false
+
+  test "[SyncQueue] getRewindPoint() test":
+    let aq = newVerifQueues()
+    block:
+      var queue = SyncQueue.init(SomeTPeer,
+                                 Slot(0), Slot(0xFFFF_FFFF_FFFF_FFFFF'u64),
+                                 1'u64, getFirstSlotAtFinalizedEpoch, aq, 2)
+      let finalizedSlot = compute_start_slot_at_epoch(Epoch(0'u64))
+      let startSlot = compute_start_slot_at_epoch(Epoch(0'u64)) + 1'u64
+      let finishSlot = compute_start_slot_at_epoch(Epoch(2'u64))
+
+      for i in uint64(startSlot) ..< uint64(finishSlot):
+        check queue.getRewindPoint(Slot(i), finalizedSlot) == finalizedSlot
+
+    block:
+      var queue = SyncQueue.init(SomeTPeer,
+                                 Slot(0), Slot(0xFFFF_FFFF_FFFF_FFFFF'u64),
+                                 1'u64, getFirstSlotAtFinalizedEpoch, aq, 2)
+      let finalizedSlot = compute_start_slot_at_epoch(Epoch(1'u64))
+      let startSlot = compute_start_slot_at_epoch(Epoch(1'u64)) + 1'u64
+      let finishSlot = compute_start_slot_at_epoch(Epoch(3'u64))
+
+      for i in uint64(startSlot) ..< uint64(finishSlot) :
+        check queue.getRewindPoint(Slot(i), finalizedSlot) == finalizedSlot
+
+    block:
+      var queue = SyncQueue.init(SomeTPeer,
+                                 Slot(0), Slot(0xFFFF_FFFF_FFFF_FFFFF'u64),
+                                 1'u64, getFirstSlotAtFinalizedEpoch, aq, 2)
+      let finalizedSlot = compute_start_slot_at_epoch(Epoch(0'u64))
+      let failSlot = Slot(0xFFFF_FFFF_FFFF_FFFFF'u64)
+      let failEpoch = compute_epoch_at_slot(failSlot)
+
+      var counter = 1'u64
+      for i in 0 ..< 64:
+        if counter >= failEpoch:
+          break
+        let rewindEpoch = failEpoch - counter
+        let rewindSlot = compute_start_slot_at_epoch(rewindEpoch)
+        check queue.getRewindPoint(failSlot, finalizedSlot) == rewindSlot
+        counter = counter shl 1
+
+    block:
+      var queue = SyncQueue.init(SomeTPeer,
+                                 Slot(0), Slot(0xFFFF_FFFF_FFFF_FFFFF'u64),
+                                 1'u64, getFirstSlotAtFinalizedEpoch, aq, 2)
+      let finalizedSlot = compute_start_slot_at_epoch(Epoch(1'u64))
+      let failSlot = Slot(0xFFFF_FFFF_FFFF_FFFFF'u64)
+      let failEpoch = compute_epoch_at_slot(failSlot)
+      var counter = 1'u64
+      for i in 0 ..< 64:
+        if counter >= failEpoch:
+          break
+        let rewindEpoch = failEpoch - counter
+        let rewindSlot = compute_start_slot_at_epoch(rewindEpoch)
+        check queue.getRewindPoint(failSlot, finalizedSlot) == rewindSlot
+        counter = counter shl 1
```
