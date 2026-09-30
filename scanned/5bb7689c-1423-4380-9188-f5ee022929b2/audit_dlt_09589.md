# [?] Fix reentrancy test

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2021-07-03
Source: https://github.com/Conflux-Chain/conflux-rust/commit/c998d25030bb12040b8c1d582e40a9d2becf7dab
Type: security-commit

## Details
Fix reentrancy test

## Patch
### tests/reentrancy_test.py
```diff
@@ -28,6 +28,7 @@ def __init__(self):
 
     def set_test_params(self):
         self.num_nodes = 1
+        self.conf_parameters["unnamed_21autumn_cip71_deferred_transition"] = 1_000_000_000
 
     def setup_network(self):
         self.setup_nodes()
```
