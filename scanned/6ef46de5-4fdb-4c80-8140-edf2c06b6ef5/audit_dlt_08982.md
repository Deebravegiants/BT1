# [?] Fix crash in get_metrics

## Summary
Severity: Unknown
Chain: Hyperledger Indy
Component: hyperledger-indy/indy-node
Published: 2018-10-29
Source: https://github.com/hyperledger-indy/indy-node/commit/77e57b67102a08e516103d6c05459321730e4127
Type: security-commit

## Details
Fix crash in get_metrics

Signed-off-by: Sergey Khoroshavin <sergey.khoroshavin@dsr-corporation.com>

## Patch
### scripts/get_metrics
```diff
@@ -204,8 +204,9 @@ def process_storage(storage, args):
           .format(client_in.count / client_out.count, client_in.sum / client_out.sum))
     print("   Node incoming/outgoing traffic: {:.2f}".format(node_in.sum / node_out.sum))
     print("   Node/client traffic: {:.2f}".format(node_traffic / client_traffic))
-    print("   Node traffic per batch: {:.2f}".format(node_traffic / three_pc.count))
-    print("   Node traffic per request: {:.2f}".format(node_traffic / three_pc.sum))
+    if three_pc.count > 0:
+        print("   Node traffic per batch: {:.2f}".format(node_traffic / three_pc.count))
+        print("   Node traffic per request: {:.2f}".format(node_traffic / three_pc.sum))
     print("")
 
     print("Profiling info:")
```
