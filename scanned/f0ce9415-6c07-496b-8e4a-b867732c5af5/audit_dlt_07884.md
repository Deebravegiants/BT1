# [?] Fix assertion crash when posting block via REST API.

## Summary
Severity: Unknown
Chain: Ethereum
Component: status-im/nimbus-eth2
Published: 2021-05-27
Source: https://github.com/status-im/nimbus-eth2/commit/90e3fb246f1a71878cefee25d5dceac1677ce8e2
Type: security-commit

## Details
Fix assertion crash when posting block via REST API.

## Patch
### beacon_chain/rpc/beacon_rest_api.nim
```diff
@@ -614,7 +614,12 @@ proc installBeaconApiHandlers*(router: var RestRouter, node: BeaconNode) =
         if dres.isErr():
           return RestApiResponse.jsonError(Http400, InvalidBlockObjectError,
                                            $dres.error())
-        dres.get()
+        var res = dres.get()
+        # `SignedBeaconBlock` deserialization do not update `root` field, so we
+        # need to calculate it.
+        res.root = hash_tree_root(res.message)
+        res
+
     let head = node.chainDag.head
     if not(node.isSynced(head)):
       return RestApiResponse.jsonError(Http503, BeaconNodeInSyncError)
```
