# [?] Merge pull request #2211 from crytic/fix-vyper-is-reentrant

## Summary
Severity: Unknown
Chain: Tooling
Component: crytic/slither
Published: 2023-12-04
Source: https://github.com/crytic/slither/commit/deebe3640cf76afbadc6bf81cc0e0ea80a06e0f3
Type: security-commit

## Details
Merge pull request #2211 from crytic/fix-vyper-is-reentrant

fix is_reentrant for internal vyper functions

## Patch
### slither/core/declarations/function.py
```diff
@@ -1500,10 +1500,13 @@ def is_reentrant(self) -> bool:
         """
         Determine if the function can be re-entered
         """
+        reentrancy_modifier = "nonReentrant"
+
+        if self.function_language == FunctionLanguage.Vyper:
+            reentrancy_modifier = "nonreentrant(lock)"
+
         # TODO: compare with hash of known nonReentrant modifier instead of the name
-        if "nonReentrant" in [m.name for m in self.modifiers] or "nonreentrant(lock)" in [
-            m.name for m in self.modifiers
-        ]:
+        if reentrancy_modifier in [m.name for m in self.modifiers]:
             return False
 
         if self.visibility in ["public", "external"]:
@@ -1515,7 +1518,9 @@ def is_reentrant(self) -> bool:
         ]
         if not all_entry_points:
             return True
-        return not all(("nonReentrant" in [m.name for m in f.modifiers] for f in all_entry_points))
+        return not all(
+            (reentrancy_modifier in [m.name for m in f.modifiers] for f in all_entry_points)
+        )
 
     # endregion
     ###################################################################################
```

### tests/unit/core/test_function_declaration.py
```diff
@@ -324,6 +324,9 @@ def withdraw():
 @external
 @nonreentrant("lock")
 def withdraw_locked():
+    self.withdraw_locked_internal()
+@internal
+def withdraw_locked_internal():
     raw_call(msg.sender, b"", value= self.balances[msg.sender])
 @payable
 @external
@@ -376,10 +379,14 @@ def __default__():
         assert not f.is_empty
 
         f = functions["withdraw_locked()"]
-        assert not f.is_reentrant
+        assert f.is_reentrant is False
         assert f.is_implemented
         assert not f.is_empty
 
+        f = functions["withdraw_locked_internal()"]
+        assert f.is_reentrant is False
+        assert f.visibility == "internal"
+
         var = contract.get_state_variable_from_name("balances")
         assert var
         assert var.solidity_signature == "balances(address)"
```
