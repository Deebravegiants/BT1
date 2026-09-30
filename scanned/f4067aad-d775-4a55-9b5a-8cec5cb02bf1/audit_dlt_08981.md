# [?] Fix crash in get_metrics script

## Summary
Severity: Unknown
Chain: Hyperledger Indy
Component: hyperledger-indy/indy-node
Published: 2018-11-22
Source: https://github.com/hyperledger-indy/indy-node/commit/a53630c89b9b66b30f256f0d4371d078f98d27ad
Type: security-commit

## Details
Fix crash in get_metrics script

Signed-off-by: Sergey Khoroshavin <sergey.khoroshavin@dsr-corporation.com>

## Patch
### scripts/get_metrics
```diff
@@ -201,8 +201,8 @@ def process_storage(storage, args):
     node_traffic = node_in.sum + node_out.sum
     client_traffic = (client_in.sum + client_out.sum)
     print("   Client incoming/outgoing: {:.2f} messages, {:.2f} traffic"
-          .format(client_in.count / client_out.count, client_in.sum / client_out.sum))
-    print("   Node incoming/outgoing traffic: {:.2f}".format(node_in.sum / node_out.sum))
+          .format(client_in.count / client_out.count, client_in.sum / client_out.sum if client_out.sum > 0 else 0))
+    print("   Node incoming/outgoing traffic: {:.2f}".format(node_in.sum / node_out.sum if node_out.sum > 0 else 0))
     print("   Node/client traffic: {:.2f}".format(node_traffic / client_traffic))
     if three_pc.count > 0:
         print("   Node traffic per batch: {:.2f}".format(node_traffic / three_pc.count))
@@ -215,7 +215,10 @@ def process_storage(storage, args):
             break
         if m < MetricsName.NODE_PROD_TIME and \
                 m not in {MetricsName.REQUEST_PROCESSING_TIME,
-                          MetricsName.BACKUP_REQUEST_PROCESSING_TIME}:
+                          MetricsName.BACKUP_REQUEST_PROCESSING_TIME,
+                          MetricsName.GC_GEN0_TIME,
+                          MetricsName.GC_GEN1_TIME,
+                          MetricsName.GC_GEN2_TIME}:
             continue
         acc = total.get(m)
         print("   {} : {}".format(str(m).split('.')[-1],
```
