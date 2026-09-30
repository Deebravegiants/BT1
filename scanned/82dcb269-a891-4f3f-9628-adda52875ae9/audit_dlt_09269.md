# [?] Merge pull request #2379 from iamdefinitelyahuman/fix/reentrancy-corruption

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2021-07-08
Source: https://github.com/vyperlang/vyper/commit/60f87671adb2b2289688128266b39d2ac3802426
Type: security-commit

## Details
Merge pull request #2379 from iamdefinitelyahuman/fix/reentrancy-corruption

Fix: storage corruption from re-entrancy locks

## Patch
### tests/functional/test_storage_slots.py
```diff
@@ -38,6 +38,17 @@ def __init__():
     ]
     self.foo[0] = [987, 654, 321]
     self.foo[1] = [123, 456, 789]
+
+@external
+@nonreentrant('lock')
+def with_lock():
+    pass
+
+
+@external
+@nonreentrant('otherlock')
+def with_other_lock():
+    pass
 """
 
 
@@ -57,3 +68,27 @@ def test_storage_slots(get_contract):
     ]
     assert [c.foo(0, i) for i in range(3)] == [987, 654, 321]
     assert [c.foo(1, i) for i in range(3)] == [123, 456, 789]
+
+
+def test_reentrancy_lock(get_contract):
+    c = get_contract(code)
+
+    # if re-entrancy locks are incorrectly placed within storage, these
+    # calls will either revert or correupt the data that we read later
+    c.with_lock()
+    c.with_other_lock()
+
+    assert c.a() == ["ok", [4, 5, 6]]
+    assert [c.b(i) for i in range(2)] == [7, 8]
+    assert c.c() == b"thisisthirtytwobytesokhowdoyoudo"
+    assert [c.d(i) for i in range(4)] == [-1, -2, -3, -4]
+    assert c.e() == "A realllllly long string but we wont use it all"
+    assert c.f(0) == 33
+    assert c.g(0) == [b"hello", [-66, 420], "another string"]
+    assert c.g(1) == [
+        b"gbye",
+        [1337, 888],
+        "whatifthisstringtakesuptheentirelengthwouldthatbesobadidothinkso",
+    ]
+    assert [c.foo(0, i) for i in range(3)] == [987, 654, 321]
+    assert [c.foo(1, i) for i in range(3)] == [123, 456, 789]
```

### vyper/parser/global_context.py
```diff
@@ -3,7 +3,7 @@
 from vyper import ast as vy_ast
 from vyper.exceptions import CompilerPanic, InvalidType, StructureException
 from vyper.signatures.function_signature import ContractRecord, VariableRecord
-from vyper.types import InterfaceType, parse_type
+from vyper.types import InterfaceType, MappingType, parse_type
 from vyper.typing import InterfaceImports
 
 
@@ -185,6 +185,9 @@ def add_globals_and_events(self, item):
 
         item_name, item_attributes = self.get_item_name_and_attributes(item, item_attributes)
 
+        # references to `len(self._globals)` are remnants of deprecated code, retained
+        # to preserve existing interfaces while we complete a larger refactor. location
+        # and size of storage vars is handled in `vyper.context.validation.data_positions`
         if item_name in self._contracts or item_name in self._interfaces:
             if self.get_call_func_name(item) == "address":
                 raise StructureException(
@@ -221,19 +224,20 @@ def get_nonrentrant_counter(self, key):
         """
         Nonrentrant locks use a prefix with a counter to minimise deployment cost of a contract.
 
-        All storage variables are allocated exactly one slot, incrementing from 0.
-        For types that require >1 slot the actual location is determined from a keccak
-        https://github.com/vyperlang/vyper/issues/769
-
-        We're able to set the initial re-entrant counter using `len(self._globals)`
-        because all storage slots are allocated while parsing the module-scope,
-        and re-entrancy locks aren't allocated until later when parsing individual
-        function scopes.
+        We're able to set the initial re-entrant counter using the sum of the sizes
+        of all the storage slots because all storage slots are allocated while parsing
+        the module-scope, and re-entrancy locks aren't allocated until later when parsing
+        individual function scopes. This relies on the deprecated _globals attribute
+        because the new way of doing things (set_data_positions) doesn't expose the
+        next unallocated storage location.
         """
         if key in self._nonrentrant_keys:
             return self._nonrentrant_keys[key]
         else:
-            counter = len(self._globals) + self._nonrentrant_counter
+            counter = (
+                sum(v.size for v in self._globals.values() if not isinstance(v.typ, MappingType))
+                + self._nonrentrant_counter
+            )
             self._nonrentrant_keys[key] = counter
             self._nonrentrant_counter += 1
             return counter
```
