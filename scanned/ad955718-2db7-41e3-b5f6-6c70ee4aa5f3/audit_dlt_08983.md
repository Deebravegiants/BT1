# [?] Fixed Bug: sovrin-node.service randomly crashes or does not start at all after reboot

## Summary
Severity: Unknown
Chain: Hyperledger Indy
Component: hyperledger-indy/indy-node
Published: 2017-03-22
Source: https://github.com/hyperledger-indy/indy-node/commit/1a4642d67945129f2063d7959c08f648dd29e646
Type: security-commit

## Details
Fixed Bug: sovrin-node.service randomly crashes or does not start at all after reboot

## Patch
### sovrin_node/server/pool_manager.py
```diff
@@ -41,7 +41,7 @@ def authErrorWhileUpdatingNode(self, request):
         vals = []
         msgs = []
         for k in data:
-            oldVal = nodeInfo[DATA][k]
+            oldVal = (nodeInfo.get(DATA, {})).get(k, None) if nodeInfo else None
             newVal = data[k]
             if oldVal != newVal:
                 r, msg = Authoriser.authorised(typ, k, actorRole,
```
