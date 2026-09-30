# [?] Fix incorrect fixpoint computation in reentrancy detector

## Summary
Severity: Unknown
Chain: Tooling
Component: crytic/slither
Published: 2018-10-15
Source: https://github.com/crytic/slither/commit/58121ce24d3f5f5934acb8fc28d40861463ea6a1
Type: security-commit

## Details
Fix incorrect fixpoint computation in reentrancy detector

## Patch
### slither/detectors/reentrancy/reentrancy.py
```diff
@@ -96,10 +96,10 @@ def _explore(self, node, visited):
                 fathers_context['read'] += father.context[self.key]['read']
 
         # Exclude path that dont bring further information
-        if self.key in self.visited_all_paths:
-            if all(f_c['calls'] in self.visited_all_paths[node]['calls'] for f_c in fathers_context):
-                if all(f_c['send_eth'] in self.visited_all_paths[node]['send_eth'] for f_c in fathers_context):
-                    if all(f_c['read'] in self.visited_all_paths[node]['read'] for f_c in fathers_context):
+        if node in self.visited_all_paths:
+            if all(call in self.visited_all_paths[node]['calls'] for call in fathers_context['calls']):
+                if all(send in self.visited_all_paths[node]['send_eth'] for send in fathers_context['send_eth']):
+                    if all(read in self.visited_all_paths[node]['read'] for read in fathers_context['read']):
                         return
         else:
             self.visited_all_paths[node] = {'send_eth':[], 'calls':[], 'read':[]}
```
