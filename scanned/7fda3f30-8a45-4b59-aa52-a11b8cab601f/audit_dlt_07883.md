# [?] json-rpc: fix crashes on altair+ blocks in certain operations (#2983)

## Summary
Severity: Unknown
Chain: Ethereum
Component: status-im/nimbus-eth2
Published: 2021-10-13
Source: https://github.com/status-im/nimbus-eth2/commit/1da4192f3f787d0b4631987aef950c53795196ce
Type: security-commit

## Details
json-rpc: fix crashes on altair+ blocks in certain operations (#2983)

For the v2 interfaces, REST is recommeded instead

## Patch
### beacon_chain/rpc/rpc_beacon_api.nim
```diff
@@ -384,28 +384,28 @@ proc installBeaconApiHandlers*(rpcServer: RpcServer, node: BeaconNode) {.
       blockId: string) ->
       tuple[canonical: bool, header: SignedBeaconBlockHeader]:
     let bd = node.getBlockDataFromBlockId(blockId)
-    # TODO check for Altair blocks and fail, because /v1/
-    let tsbb = bd.data.phase0Block
-    static: doAssert tsbb.signature is TrustedSig and
-              sizeof(ValidatorSig) == sizeof(tsbb.signature)
-    result.header.signature = cast[ValidatorSig](tsbb.signature)
-
-    result.header.message.slot = tsbb.message.slot
-    result.header.message.proposer_index = tsbb.message.proposer_index
-    result.header.message.parent_root = tsbb.message.parent_root
-    result.header.message.state_root = tsbb.message.state_root
-    result.header.message.body_root = tsbb.message.body.hash_tree_root()
-
-    result.canonical = bd.refs.isAncestorOf(node.dag.head)
+    return withBlck(bd.data):
+      static: doAssert blck.signature is TrustedSig and
+                sizeof(ValidatorSig) == sizeof(blck.signature)
+      (
+        canonical: bd.refs.isAncestorOf(node.dag.head),
+        header: SignedBeaconBlockHeader(
+          message: BeaconBlockHeader(
+            slot: blck.message.slot,
+            proposer_index: blck.message.proposer_index,
+            parent_root: blck.message.parent_root,
+            state_root: blck.message.state_root,
+            body_root: blck.message.body.hash_tree_root()
+          )
+        )
+      )
 
   rpcServer.rpc("post_v1_beacon_blocks") do (blck: phase0.SignedBeaconBlock) -> int:
     if not(node.syncManager.inProgress):
       raise newException(CatchableError,
                          "Beacon node is currently syncing, try again later.")
     let head = node.dag.head
     if head.slot >= blck.message.slot:
-      # TODO altair-transition, but not immediate testnet-priority to detect
-      # Altair and fail, since /v1/ doesn't support Altair
       node.network.broadcastBeaconBlock(ForkedSignedBeaconBlock.init(blck))
       # The block failed validation, but was successfully broadcast anyway.
       # It was not integrated into the beacon node's database.
@@ -415,7 +415,6 @@ proc installBeaconApiHandlers*(rpcServer: RpcServer, node: BeaconNode) {.
         node, head, AttachedValidator(),
         ForkedSignedBeaconBlock.init(blck))
       if res == head:
-        # TODO altair-transition, but not immediate testnet-priority
         node.network.broadcastBeaconBlock(ForkedSignedBeaconBlock.init(blck))
         # The block failed validation, but was successfully broadcast anyway.
         # It was not integrated into the beacon node''s database.
@@ -427,18 +426,21 @@ proc installBeaconApiHandlers*(rpcServer: RpcServer, node: BeaconNode) {.
 
   rpcServer.rpc("get_v1_beacon_blocks_blockId") do (
       blockId: string) -> phase0.TrustedSignedBeaconBlock:
-    # TODO detect Altair and fail: /v1/ APIs don't support Altair
-    return node.getBlockDataFromBlockId(blockId).data.phase0Block
+    let blck = node.getBlockDataFromBlockId(blockId).data
+    if blck.kind == BeaconBlockFork.Phase0:
+      return blck.phase0Block
+    else:
+      raiseNoAltairSupport()
 
   rpcServer.rpc("get_v1_beacon_blocks_blockId_root") do (
       blockId: string) -> Eth2Digest:
-    # TODO detect Altair and fail: /v1/ APIs don't support Altair
-    return node.getBlockDataFromBlockId(blockId).data.phase0Block.message.state_root
+    return withBlck(node.getBlockDataFromBlockId(blockId).data):
+      blck.message.state_root
 
   rpcServer.rpc("get_v1_beacon_blocks_blockId_attestations") do (
       blockId: string) -> seq[TrustedAttestation]:
-    # TODO detect Altair and fail: /v1/ APIs don't support Altair
-    return node.getBlockDataFromBlockId(blockId).data.phase0Block.message.body.attestations.asSeq
+    return withBlck(node.getBlockDataFromBlockId(blockId).data):
+      blck.message.body.attestations.asSeq
 
   rpcServer.rpc("get_v1_beacon_pool_attestations") do (
       slot: Option[uint64], committee_index: Option[uint64]) ->
```

### beacon_chain/rpc/rpc_debug_api.nim
```diff
@@ -26,7 +26,10 @@ proc installDebugApiHandlers*(rpcServer: RpcServer, node: BeaconNode) {.
   rpcServer.rpc("get_v1_debug_beacon_states_stateId") do (
       stateId: string) -> phase0.BeaconState:
     withStateForStateId(stateId):
-      return stateData.data.hbsPhase0.data
+      if stateData.data.beaconStateFork == forkPhase0:
+        return stateData.data.hbsPhase0.data
+      else:
+        raiseNoAltairSupport()
 
   rpcServer.rpc("get_v1_debug_beacon_heads") do () -> seq[tuple[root: Eth2Digest, slot: Slot]]:
     return node.dag.heads.mapIt((it.root, it.slot))
```

### beacon_chain/rpc/rpc_utils.nim
```diff
@@ -16,7 +16,11 @@ import
   ../spec/[forks, helpers],
   ../spec/eth2_apis/[rpc_types, eth2_json_rpc_serialization]
 
-export rpc_types, eth2_json_rpc_serialization, blockchain_dag
+export forks, rpc_types, eth2_json_rpc_serialization, blockchain_dag
+
+template raiseNoAltairSupport*() =
+  raise (ref ValueError)(msg:
+    "The JSON-RPC interface does not support certain Altair operations due to changes in block structure - see https://nimbus.guide/rest-api.html for full altair support")
 
 template withStateForStateId*(stateId: string, body: untyped): untyped =
   let
```

### beacon_chain/rpc/rpc_validator_api.nim
```diff
@@ -50,9 +50,8 @@ proc installValidatorApiHandlers*(rpcServer: RpcServer, node: BeaconNode) {.
     case blck.kind
     of BeaconBlockFork.Phase0:
       return blck.phase0Block
-    of BeaconBlockFork.Altair, BeaconBlockFork.Merge:
-      raise newException(CatchableError,
-                         "could not retrieve block for altair or merge blocks")
+    else:
+      raiseNoAltairSupport()
 
   rpcServer.rpc("post_v1_validator_block") do (body: phase0.SignedBeaconBlock) -> bool:
     debug "post_v1_validator_block",
```

### beacon_chain/spec/datatypes/merge.nim
```diff
@@ -275,19 +275,19 @@ type
 
   TrustedBeaconBlockBody* = object
     ## A full verified block
-    randao_reveal*: ValidatorSig
+    randao_reveal*: TrustedSig
     eth1_data*: Eth1Data ##\
     ## Eth1 data vote
 
     graffiti*: GraffitiBytes ##\
     ## Arbitrary data
 
     # Operations
-    proposer_slashings*: List[ProposerSlashing, Limit MAX_PROPOSER_SLASHINGS]
-    attester_slashings*: List[AttesterSlashing, Limit MAX_ATTESTER_SLASHINGS]
-    attestations*: List[Attestation, Limit MAX_ATTESTATIONS]
+    proposer_slashings*: List[TrustedProposerSlashing, Limit MAX_PROPOSER_SLASHINGS]
+    attester_slashings*: List[TrustedAttesterSlashing, Limit MAX_ATTESTER_SLASHINGS]
+    attestations*: List[TrustedAttestation, Limit MAX_ATTESTATIONS]
     deposits*: List[Deposit, Limit MAX_DEPOSITS]
-    voluntary_exits*: List[SignedVoluntaryExit, Limit MAX_VOLUNTARY_EXITS]
+    voluntary_exits*: List[TrustedSignedVoluntaryExit, Limit MAX_VOLUNTARY_EXITS]
     sync_aggregate*: SyncAggregate
 
     # Execution
```
