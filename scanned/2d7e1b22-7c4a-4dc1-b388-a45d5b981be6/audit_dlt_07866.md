# [?] avoid gloas crash when no grandparent block (#8333)

## Summary
Severity: Unknown
Chain: Ethereum
Component: status-im/nimbus-eth2
Published: 2026-04-25
Source: https://github.com/status-im/nimbus-eth2/commit/49e80823638e2af33fb9aca1d79008c52b770928
Type: security-commit

## Details
avoid gloas crash when no grandparent block (#8333)

## Patch
### beacon_chain/gossip_processing/gossip_validation.nim
```diff
@@ -426,8 +426,10 @@ template validateBeaconBlockGloas(
   let parent = dag.getBlockRef(bid.parent_block_root).valueOr:
     return dag.checkedReject("validateBeaconBlockGloas: invalid execution parent")
   debugGloasComment("request missing envelope if not found in db")
+  debugGloasComment("revisit the naive parent.parent.isNil guard")
   if not (
       isParentBlockFull(dag, signed_beacon_block, parent) or
+      parent.parent.isNil or
       isParentBlockFull(dag, signed_beacon_block, parent.parent)
   ):
     return dag.checkedReject("validateBeaconBlockGloas: invalid execution parent")
```
