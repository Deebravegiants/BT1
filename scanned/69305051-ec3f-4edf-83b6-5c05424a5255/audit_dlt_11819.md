# [?] Fix missing str conversion on reentrancy event

## Summary
Severity: Unknown
Chain: Tooling
Component: crytic/slither
Published: 2020-08-03
Source: https://github.com/crytic/slither/commit/7dd74dc887cb60769684770b119fff2c63f95f36
Type: security-commit

## Details
Fix missing str conversion on reentrancy event

## Patch
### slither/detectors/reentrancy/reentrancy_events.py
```diff
@@ -78,7 +78,7 @@ def _detect(self):
         for (func, calls, send_eth), events in result_sorted:
             calls = sorted(list(set(calls)), key=lambda x: x[0].node_id)
             send_eth = sorted(list(set(send_eth)), key=lambda x: x[0].node_id)
-            events = sorted(events, key=lambda x: (x.variable.name, x.node.node_id))
+            events = sorted(events, key=lambda x: (str(x.variable.name), x.node.node_id))
 
             info = ['Reentrancy in ', func, ':\n']
             info += ['\tExternal calls:\n']
```
