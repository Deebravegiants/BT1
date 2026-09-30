# [?] Speedup reentrancy detection through fixpoint

## Summary
Severity: Unknown
Chain: Tooling
Component: crytic/slither
Published: 2018-09-13
Source: https://github.com/crytic/slither/commit/e1fedcacbf6cb944df760557f8110b64b0dd5dfa
Type: security-commit

## Details
Speedup reentrancy detection through fixpoint

## Patch
### slither/detectors/reentrancy/reentrancy.py
```diff
@@ -2,6 +2,7 @@
     Re-entrancy detection
 
     Based on heuristics, it may lead to FP and FN
+    Iterate over all the nodes of the graph until reaching a fixpoint
 """
 
 from slither.core.declarations.function import Function
@@ -66,13 +67,28 @@ def _explore(self, node, visited):
         """
         if node in visited:
             return
+
         visited = visited + [node]
 
         # First we add the external calls executed in previous nodes
         node.context[self.key] = []
+
+        fathers_context = []
+
         for father in node.fathers:
             if self.key in father.context:
-                node.context[self.key] += father.context[self.key]
+                fathers_context += father.context[self.key]
+
+        # Exclude path that dont bring further information
+        if node in self.visited_all_paths:
+            if all(f_c in self.visited_all_paths[node] for f_c in fathers_context):
+                return
+        else:
+            self.visited_all_paths[node] = []
+
+        self.visited_all_paths[node] = list(set(self.visited_all_paths[node] + fathers_context))
+
+        node.context[self.key] = fathers_context
 
         # Get all the new external calls
         for call in node.external_calls:
@@ -88,6 +104,7 @@ def _explore(self, node, visited):
             if isinstance(internal_call, Function):
                 state_vars_written += internal_call.all_state_variables_written()
 
+
         # If a state variables is written, and there was an external call
         # We found a potential re-entrancy bug
         if state_vars_written and node.context[self.key]:
@@ -119,6 +136,14 @@ def detect(self):
         """
         """
         self.result = {}
+
+        # if a node was already visited by another path
+        # we will only explore it if the traversal brings
+        # new variables written
+        # This speedup the exploration through a light fixpoint
+        # Its particular useful on 'complex' functions with several loops and conditions
+        self.visited_all_paths = {}
+
         for c in self.contracts:
             self.detect_reentrancy(c)
 
```
