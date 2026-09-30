# [?] fix[lang]: fix panic in call cycle detection (#4200)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2024-08-07
Source: https://github.com/vyperlang/vyper/commit/9b322d651cd5fb431e208b079382ce94fe82abd9
Type: security-commit

## Details
fix[lang]: fix panic in call cycle detection (#4200)

fix cycle detection in `_compute_reachable_set()` by adding a check for
subcycles in the current call path

the function was detecting cycles by checking for a cyclic call to the
*root* of the call path

if the cycle was within the call path (excluding the root) it could
fall into infinite recursion.

## Patch
### tests/unit/semantics/analysis/test_cyclic_function_calls.py
```diff
@@ -12,9 +12,28 @@ def foo():
     self.foo()
     """
     vyper_module = parse_to_ast(code)
-    with pytest.raises(CallViolation):
+    with pytest.raises(CallViolation) as e:
         analyze_module(vyper_module, dummy_input_bundle)
 
+    assert e.value.message == "Contract contains cyclic function call: foo -> foo"
+
+
+def test_self_function_call2(dummy_input_bundle):
+    code = """
+@external
+def foo():
+    self.bar()
+
+@internal
+def bar():
+    self.bar()
+    """
+    vyper_module = parse_to_ast(code)
+    with pytest.raises(CallViolation) as e:
+        analyze_module(vyper_module, dummy_input_bundle)
+
+    assert e.value.message == "Contract contains cyclic function call: foo -> bar -> bar"
+
 
 def test_cyclic_function_call(dummy_input_bundle):
     code = """
@@ -27,9 +46,11 @@ def bar():
     self.foo()
     """
     vyper_module = parse_to_ast(code)
-    with pytest.raises(CallViolation):
+    with pytest.raises(CallViolation) as e:
         analyze_module(vyper_module, dummy_input_bundle)
 
+    assert e.value.message == "Contract contains cyclic function call: foo -> bar -> foo"
+
 
 def test_multi_cyclic_function_call(dummy_input_bundle):
     code = """
@@ -50,9 +71,40 @@ def potato():
     self.foo()
     """
     vyper_module = parse_to_ast(code)
-    with pytest.raises(CallViolation):
+    with pytest.raises(CallViolation) as e:
+        analyze_module(vyper_module, dummy_input_bundle)
+
+    expected_message = "Contract contains cyclic function call: foo -> bar -> baz -> potato -> foo"
+
+    assert e.value.message == expected_message
+
+
+def test_multi_cyclic_function_call2(dummy_input_bundle):
+    code = """
+@internal
+def foo():
+    self.bar()
+
+@internal
+def bar():
+    self.baz()
+
+@internal
+def baz():
+    self.potato()
+
+@internal
+def potato():
+    self.bar()
+    """
+    vyper_module = parse_to_ast(code)
+    with pytest.raises(CallViolation) as e:
         analyze_module(vyper_module, dummy_input_bundle)
 
+    expected_message = "Contract contains cyclic function call: foo -> bar -> baz -> potato -> bar"
+
+    assert e.value.message == expected_message
+
 
 def test_global_ann_assign_callable_no_crash(dummy_input_bundle):
     code = """
```

### vyper/semantics/analysis/module.py
```diff
@@ -150,15 +150,15 @@ def _compute_reachable_set(fn_t: ContractFunctionT, path: list[ContractFunctionT
     path = path or []
 
     path.append(fn_t)
-    root = path[0]
 
     for g in fn_t.called_functions:
         if g in fn_t.reachable_internal_functions:
             # already seen
             continue
 
-        if g == root:
-            message = " -> ".join([f.name for f in path])
+        if g in path:
+            extended_path = path + [g]
+            message = " -> ".join([f.name for f in extended_path])
             raise CallViolation(f"Contract contains cyclic function call: {message}")
 
         _compute_reachable_set(g, path=path)
```
