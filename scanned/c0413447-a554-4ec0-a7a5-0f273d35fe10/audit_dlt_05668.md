# [?] Fix Gloas data column quarantine crash on non-custody columns (#8344)

## Summary
Severity: Unknown
Chain: Ethereum
Component: status-im/nimbus-eth2
Published: 2026-04-30
Source: https://github.com/status-im/nimbus-eth2/commit/1acfee6669c562eb9a3c6c854a591ed1db6ffee2
Type: security-commit

## Details
Fix Gloas data column quarantine crash on non-custody columns (#8344)

* Fix Gloas data column quarantine crash on non-custody columns

* extend non-custodied data column fix to fulu

* unsubscribe from stale custody groups

## Patch
### beacon_chain/gossip_processing/eth2_processor.nim
```diff
@@ -14,7 +14,7 @@ import
   kzg4844/kzg,
   ssz_serialization/types,
   ../el/el_manager,
-  ../spec/[helpers, forks],
+  ../spec/[column_map, helpers, forks],
   ../consensus_object_pools/[
     attestation_pool, blob_quarantine, block_clearance, block_quarantine,
     blockchain_dag, envelope_quarantine, execution_payload_pool,
@@ -454,6 +454,11 @@ proc processDataColumnSidecar*(
   let block_root = hash_tree_root(block_header)
 
   debug "Data column validated, putting data column in quarantine"
+  if dataColumnSidecar.index notin self.dataColumnQuarantine[].custodyMap:
+    data_column_sidecars_received.inc()
+    data_column_sidecar_delay.observe(delay.toFloatSeconds())
+    return v
+
   self.dataColumnQuarantine[].put(block_root, newClone(dataColumnSidecar))
 
   if block_root in self.quarantine[].sidecarless:
@@ -500,6 +505,10 @@ proc processDataColumnSidecar*(
     return v
 
   debug "Data column validated"
+  if dataColumnSidecar.index notin self.gloasColumnQuarantine[].custodyMap:
+    data_column_sidecars_received.inc()
+    return v
+
   self.gloasColumnQuarantine[].put(
     dataColumnSidecar.beacon_block_root, newClone(dataColumnSidecar))
   self.blockProcessor.enqueuePayload(dataColumnSidecar.beacon_block_root)
```

### beacon_chain/nimbus_beacon_node.nim
```diff
@@ -1358,8 +1358,12 @@ proc updateDataColumnSidecarHandlers(node: BeaconNode, gossipEpoch: Epoch) =
     node.network.subscribe(topic, basicParams())
     custody.add(i)
 
-  # Due to dynamic column changes, we need to maintain the set of columns we
-  # subscribe to, as the column set may change.
+  # Unsubscribe from custody groups we no longer have custody of.
+  for i in node.lastColumnCustodyIndices:
+    if i notin custody:
+      let topic = getDataColumnSidecarTopic(forkDigest, i)
+      node.network.unsubscribe(topic)
+
   node.lastColumnCustodyIndices = custody
 
 proc addAltairMessageHandlers(
@@ -1729,11 +1733,9 @@ proc updateGossipStatus(node: BeaconNode, slot: Slot) {.async.} =
   node.gossipState = targetGossipState
 
   # Validator custody can change in the middle of a fork/BPO interval; need to
-  # subscribe to potentially new column topics. Do this after node.gossipState
-  # is updated to avoid adding immediately unsubscribed subscriptions. Custody
-  # can only grow in a node's lifetime, so only address additive case. It can,
-  # therefore, overlap existing subscriptions, rather than separately tracking
-  # them.
+  # subscribe to potentially new column topics and unsubscribe from stale ones.
+  # Do this after node.gossipState is updated to avoid adding immediately
+  # unsubscribed subscriptions.
   for gossipEpoch in node.gossipState:
     if node.dag.cfg.consensusForkAtEpoch(gossipEpoch) >= ConsensusFork.Fulu:
       node.updateDataColumnSidecarHandlers(gossipEpoch)
```
