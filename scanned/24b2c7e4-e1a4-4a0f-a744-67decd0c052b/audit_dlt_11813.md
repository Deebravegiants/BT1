# [?] Fix crash when variable is initialized

## Summary
Severity: Unknown
Chain: Tooling
Component: crytic/slither
Published: 2023-05-14
Source: https://github.com/crytic/slither/commit/408c863bbff164e3a20c838ff07dc077371a7ae3
Type: security-commit

## Details
Fix crash when variable is initialized

## Patch
### slither/detectors/variables/uninitialized_local_variables.py
```diff
@@ -70,7 +70,8 @@ def _detect_uninitialized(
             and len(node.sons) == 1  # Should always be true for a node that has a STARTLOOP son
             and node.sons[0].type == NodeType.STARTLOOP
         ):
-            fathers_context.remove(node.variable_declaration)
+            if node.variable_declaration in fathers_context:
+                fathers_context.remove(node.variable_declaration)
 
         if self.key in node.context:
             fathers_context += node.context[self.key]
```

### tests/e2e/detectors/test_data/uninitialized-local/0.4.25/uninitialized_local_variable.sol
```diff
@@ -10,6 +10,11 @@ contract Uninitialized{
         for(uint i; i < 6; i++) { 
             uint a = i;
         }
+
+        for(uint j = 0; j < 6; j++) { 
+            uint b = j;
+        }
+
     }
 
 }
```

### tests/e2e/detectors/test_data/uninitialized-local/0.5.16/uninitialized_local_variable.sol
```diff
@@ -10,6 +10,11 @@ contract Uninitialized{
         for(uint i; i < 6; i++) { 
             uint a = i;
         }
+
+        for(uint j = 0; j < 6; j++) { 
+            uint b = j;
+        }
+
     }
 
 }
```

### tests/e2e/detectors/test_data/uninitialized-local/0.6.11/uninitialized_local_variable.sol
```diff
@@ -10,6 +10,11 @@ contract Uninitialized{
         for(uint i; i < 6; i++) { 
             uint a = i;
         }
+
+        for(uint j = 0; j < 6; j++) { 
+            uint b = j;
+        }
+
     }
 
 }
```

### tests/e2e/detectors/test_data/uninitialized-local/0.7.6/uninitialized_local_variable.sol
```diff
@@ -10,6 +10,11 @@ contract Uninitialized{
         for(uint i; i < 6; i++) { 
             uint a = i;
         }
+
+        for(uint j = 0; j < 6; j++) { 
+            uint b = j;
+        }
+
     }
 
 }
```
