# [?] fix engine API crash when EL disconnected (#4027)

## Summary
Severity: Unknown
Chain: Ethereum
Component: status-im/nimbus-eth2
Published: 2022-08-25
Source: https://github.com/status-im/nimbus-eth2/commit/d619b539f3963fa2fdc1a733b0684d702dd827d3
Type: security-commit

## Details
fix engine API crash when EL disconnected (#4027)

When issuing an engine API call while the EL is disconnected, a `nil`
pointer is dereferenced. Fixed by correctly initializing futures.

```
Traceback (most recent call last, using override)
vendor/nim-libp2p/libp2p/protocols/pubsub/pubsub.nim(890) main
beacon_chain/nimbus_beacon_node.nim(2139) main
beacon_chain/nimbus_beacon_node.nim(0) handleStartUpCmd
beacon_chain/nimbus_beacon_node.nim(0) doRunBeaconNode
beacon_chain/nimbus_beacon_node.nim(0) start
beacon_chain/nimbus_beacon_node.nim(1589) run
vendor/nimbus-build-system/vendor/Nim/lib/system/iterators_1.nim(107) poll
vendor/nim-chronos/chronos/asyncfutures2.nim(365) futureContinue
beacon_chain/consensus_object_pools/consensus_manager.nim(297) updateHeadWithExecution
vendor/nim-chronos/chronos/asyncmacro2.nim(213) runProposalForkchoiceUpdated
vendor/nim-chronos/chronos/asyncfutures2.nim(365) futureContinue
beacon_chain/consensus_object_pools/consensus_manager.nim(259) runProposalForkchoiceUpdated
beacon_chain/eth1/eth1_monitor.nim(0) forkchoiceUpdated
vendor/nim-chronos/chronos/asyncfutures2.nim(219) complete
vendor/nim-chronos/chronos/asyncfutures2.nim(149) cancelled
vendor/nimbus-build-system/vendor/Nim/lib/system/excpt.nim(610) signalHandler
SIGSEGV: Illegal storage access. (Attempt to read from nil?)
```

## Patch
### beacon_chain/eth1/eth1_monitor.nim
```diff
@@ -478,7 +478,7 @@ proc getPayload*(p: Eth1Monitor,
   # Eth1 monitor can recycle connections without (external) warning; at least,
   # don't crash.
   if p.isNil or p.dataProvider.isNil:
-    var epr: Future[engine_api.ExecutionPayloadV1]
+    let epr = newFuture[engine_api.ExecutionPayloadV1]("getPayload")
     epr.complete(default(engine_api.ExecutionPayloadV1))
     return epr
 
@@ -489,7 +489,7 @@ proc newPayload*(p: Eth1Monitor, payload: engine_api.ExecutionPayloadV1):
   # Eth1 monitor can recycle connections without (external) warning; at least,
   # don't crash.
   if p.dataProvider.isNil:
-    var epr: Future[PayloadStatusV1]
+    let epr = newFuture[PayloadStatusV1]("newPayload")
     epr.complete(PayloadStatusV1(status: PayloadExecutionStatus.syncing))
     return epr
 
@@ -501,7 +501,8 @@ proc forkchoiceUpdated*(p: Eth1Monitor,
   # Eth1 monitor can recycle connections without (external) warning; at least,
   # don't crash.
   if p.isNil or p.dataProvider.isNil:
-    var fcuR: Future[engine_api.ForkchoiceUpdatedResponse]
+    let fcuR =
+      newFuture[engine_api.ForkchoiceUpdatedResponse]("forkchoiceUpdated")
     fcuR.complete(engine_api.ForkchoiceUpdatedResponse(
       payloadStatus: PayloadStatusV1(status: PayloadExecutionStatus.syncing)))
     return fcuR
@@ -527,7 +528,8 @@ proc forkchoiceUpdated*(p: Eth1Monitor,
   # Eth1 monitor can recycle connections without (external) warning; at least,
   # don't crash.
   if p.isNil or p.dataProvider.isNil:
-    var fcuR: Future[engine_api.ForkchoiceUpdatedResponse]
+    let fcuR =
+      newFuture[engine_api.ForkchoiceUpdatedResponse]("forkchoiceUpdated")
     fcuR.complete(engine_api.ForkchoiceUpdatedResponse(
       payloadStatus: PayloadStatusV1(status: PayloadExecutionStatus.syncing)))
     return fcuR
```
