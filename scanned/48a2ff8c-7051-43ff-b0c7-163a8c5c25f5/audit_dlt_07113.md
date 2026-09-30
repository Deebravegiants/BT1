# [?] avoid potential database inconsistency after fcU `INVALID`+crash (#4192)

## Summary
Severity: Unknown
Chain: Ethereum
Component: status-im/nimbus-eth2
Published: 2022-09-28
Source: https://github.com/status-im/nimbus-eth2/commit/1819d79e07181ef1c5ad167c13fd09354f37ac46
Type: security-commit

## Details
avoid potential database inconsistency after fcU `INVALID`+crash (#4192)

* avoid database race-condition inconsistency after fcU `INVALID` then crash

* ensure head doesn't fall behind finalized; add more tests for head movement/reloading DAG

## Patch
### beacon_chain/consensus_object_pools/blockchain_dag.nim
```diff
@@ -1516,37 +1516,10 @@ proc pruneBlocksDAG(dag: ChainDAGRef) =
     prunedHeads = hlen - dag.heads.len,
     dagPruneDur = Moment.now() - startTick
 
-# https://github.com/ethereum/consensus-specs/blob/v1.2.0-rc.3/sync/optimistic.md#helpers
+# https://github.com/ethereum/consensus-specs/blob/v1.2.0/sync/optimistic.md#helpers
 template is_optimistic*(dag: ChainDAGRef, root: Eth2Digest): bool =
   root in dag.optimisticRoots
 
-proc markBlockInvalid*(dag: ChainDAGRef, root: Eth2Digest) =
-  let blck = dag.getBlockRef(root).valueOr:
-    return
-  logScope: blck = shortLog(blck)
-
-  if not dag.is_optimistic(root):
-    # https://github.com/ethereum/consensus-specs/blob/v1.2.0-rc.3/sync/optimistic.md#transitioning-from-valid---invalidated-or-invalidated---valid
-    # "These operations are purposefully omitted. It is outside of the scope of
-    # the specification since it's only possible with a faulty EE."
-    warn "markBlockInvalid: attempt to invalidate valid block"
-    doAssert strictVerification notin dag.updateFlags
-    return
-
-  if blck.slot <= dag.finalizedHead.slot:
-    # https://github.com/ethereum/consensus-specs/blob/v1.2.0-rc.3/sync/optimistic.md#re-orgs
-    # "If the justified checkpoint transitions from `NOT_VALIDATED` ->
-    # `INVALIDATED`, a consensus engine MAY choose to alert the user and force
-    # the application to exit."
-    #
-    # But be slightly less aggressive, and only check finalized.
-    warn "markBlockInvalid: attempted to mark finalized block invalidated"
-    doAssert strictVerification notin dag.updateFlags
-    return
-
-  debug "markBlockInvalid"
-  dag.pruneBlockSlot(blck.atSlot())
-
 proc markBlockVerified*(
     dag: ChainDAGRef, quarantine: var Quarantine, root: Eth2Digest) =
   # Might be called when block was not optimistic to begin with, or had been
@@ -1741,6 +1714,9 @@ proc updateHead*(
   ## now fall from grace, or no longer be considered resolved.
   doAssert not newHead.isNil()
 
+  # Could happen if enough blocks get invalidated and would corrupt database
+  doAssert newHead.slot >= dag.finalizedHead.slot
+
   let
     lastHead = dag.head
 
```

### beacon_chain/consensus_object_pools/consensus_manager.nim
```diff
@@ -248,7 +248,6 @@ proc updateExecutionClientHead(
         newHead.blck.root
 
     self.attestationPool[].forkChoice.mark_root_invalid(newHead.blck.root)
-    self.dag.markBlockInvalid(newHead.blck.root)
     self.quarantine[].addUnviable(newHead.blck.root)
     return Opt.none(void)
   of PayloadExecutionStatus.accepted, PayloadExecutionStatus.syncing:
```

### beacon_chain/gossip_processing/block_processor.nim
```diff
@@ -190,7 +190,7 @@ proc expectValidForkchoiceUpdated(
 from ../consensus_object_pools/attestation_pool import
   addForkChoice, selectOptimisticHead, BeaconHead
 from ../consensus_object_pools/blockchain_dag import
-  is_optimistic, loadExecutionBlockRoot, markBlockInvalid, markBlockVerified
+  is_optimistic, loadExecutionBlockRoot, markBlockVerified
 from ../consensus_object_pools/block_dag import shortLog
 from ../consensus_object_pools/spec_cache import get_attesting_indices
 from ../spec/datatypes/phase0 import TrustedSignedBeaconBlock
@@ -555,7 +555,6 @@ proc runQueueProcessingLoop*(self: ref BlockProcessor) {.async.} =
       debug "runQueueProcessingLoop: execution payload invalid",
         executionPayloadStatus,
         blck = shortLog(blck.blck)
-      self.consensusManager.dag.markBlockInvalid(blck.blck.root)
       self.consensusManager.quarantine[].addUnviable(blck.blck.root)
       # Every loop iteration ends with some version of blck.resfut.complete(),
       # including processBlock(), otherwise the sync manager stalls.
```

### tests/test_blockchain_dag.nim
```diff
@@ -564,6 +564,11 @@ suite "chain DAG finalization tests" & preset():
         db.getStateRoot(finalizedCheckpoint.bid.root, finalizedCheckpoint.slot).isSome
         db.getStateRoot(prunedCheckpoint.bid.root, prunedCheckpoint.slot).isNone
 
+    # Roll back head block (e.g., because it was declared INVALID)
+    let parentRoot = dag.head.parent.root
+    dag.updateHead(dag.head.parent, quarantine)
+    check: dag.head.root == parentRoot
+
     let
       validatorMonitor2 = newClone(ValidatorMonitor.init())
       dag2 = init(ChainDAGRef, defaultRuntimeConfig, db, validatorMonitor2, {})
@@ -572,6 +577,7 @@ suite "chain DAG finalization tests" & preset():
     check:
       dag2.tail.root == dag.tail.root
       dag2.head.root == dag.head.root
+      dag2.head.root == parentRoot
       dag2.finalizedHead.blck.root == dag.finalizedHead.blck.root
       dag2.finalizedHead.slot == dag.finalizedHead.slot
       getStateRoot(dag2.headState) == getStateRoot(dag.headState)
@@ -964,6 +970,14 @@ suite "Latest valid hash" & preset():
       b3Add = dag.addHeadBlock(verifier, b3, nilBellatrixCallback)
 
     dag.updateHead(b3Add[], quarantine[])
+    check: dag.head.root == b3.root
+
+    # Ensure that head can go backwards in case of head being marked invalid
+    dag.updateHead(b2Add[], quarantine[])
+    check: dag.head.root == b2.root
+
+    dag.updateHead(b1Add[], quarantine[])
+    check: dag.head.root == b1.root
 
     const fallbackEarliestInvalid =
       Eth2Digest.fromHex("0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef")
```
