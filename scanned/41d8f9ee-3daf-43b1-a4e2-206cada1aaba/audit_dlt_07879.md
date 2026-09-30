# [?] Fix assertion crash in pollForSyncCommitteeDuties() because forks schedule is not available yet. (#3791)

## Summary
Severity: Unknown
Chain: Ethereum
Component: status-im/nimbus-eth2
Published: 2022-06-23
Source: https://github.com/status-im/nimbus-eth2/commit/beaf05b8d1571d4b0e8ad6f788b36850c236f3b3
Type: security-commit

## Details
Fix assertion crash in pollForSyncCommitteeDuties() because forks schedule is not available yet. (#3791)

Fix syncCommitteeeDutiesLoop() not being restarted on crash.

## Patch
### beacon_chain/validator_client/duties_service.nim
```diff
@@ -463,6 +463,10 @@ proc validatorIndexLoop(service: DutiesServiceRef) {.async.} =
 
 proc syncCommitteeeDutiesLoop(service: DutiesServiceRef) {.async.} =
   let vc = service.client
+
+  debug "Sync committee duties loop waiting for fork schedule update"
+  await vc.forksAvailable.wait()
+  doAssert(len(vc.forks) > 0, "Fork schedule must not be empty at this point")
   while true:
     await vc.pollForSyncCommitteeDuties()
     await service.waitForNextSlot(SyncCommitteeLoop)
@@ -494,7 +498,7 @@ proc mainLoop(service: DutiesServiceRef) {.async.} =
     while true:
       var breakLoop = false
       try:
-        discard await race(fut1, fut2, fut3)
+        discard await race(fut1, fut2, fut3, fut4)
       except CancelledError:
         if not(fut1.finished()): fut1.cancel()
         if not(fut2.finished()): fut2.cancel()
```
