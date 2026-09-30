# [?] fix[lang]: fix panic on function named `address` (#5196)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2026-07-22
Source: https://github.com/vyperlang/vyper/commit/730a2d36f1fca90be059c75681de5c942560ce0b
Type: security-commit

## Details
fix[lang]: fix panic on function named `address` (#5196)

this commit fixes a panic on methods named 'address'. the panic occured
during the construction of the user-facing error message, and was due to
'_id' on 'InterfaceT' being set too late.

## Patch
### tests/functional/codegen/types/test_identifier_naming.py
```diff
@@ -3,6 +3,7 @@
 from vyper.ast.identifiers import RESERVED_KEYWORDS
 from vyper.builtins.functions import BUILTIN_FUNCTIONS
 from vyper.codegen.expr import ENVIRONMENT_VARIABLES
+from vyper.compiler import compile_code
 from vyper.exceptions import NamespaceCollision, StructureException, SyntaxException
 from vyper.semantics.types.primitives import AddressT
 
@@ -66,3 +67,14 @@ def {constant}(var: int128):
     assert_compile_failed(
         lambda: get_contract(code), (SyntaxException, StructureException, NamespaceCollision)
     )
+
+
+def test_function_named_address_collides():
+    code = """
+@external
+def address() -> uint256:
+    return 1
+    """
+    with pytest.raises(NamespaceCollision) as excinfo:
+        compile_code(code, contract_path="foo.vy")
+    assert excinfo.value.message == "Member 'address' already exists in foo.vy"
```

### tests/functional/syntax/test_custom_errors.py
```diff
@@ -34,3 +34,27 @@ def fail():
 def test_custom_error_bad_usage_diagnostics(code, exc_text):
     with pytest.raises(StructureException, match=exc_text):
         compile_code(code)
+
+
+def test_custom_error_with_address_member():
+    code = """
+error MyErr:
+    address: uint256
+
+@external
+def foo():
+    raise MyErr(address=1)
+    """
+    assert compile_code(code) is not None
+
+
+def test_custom_error_with_address_name_and_type():
+    code = """
+error MyErr:
+    address: address
+
+@external
+def foo():
+    raise MyErr(address=msg.sender)
+    """
+    assert compile_code(code) is not None
```

### tests/functional/syntax/test_event.py
```diff
@@ -18,3 +18,27 @@ def test_event_with_module_as_member_errors(make_input_bundle):
         compile_code(top, input_bundle=input_bundle)
 
     assert "not a valid event member" in str(e.value)
+
+
+def test_event_with_address_member():
+    code = """
+event E:
+    address: uint256
+
+@external
+def foo():
+    log E(address=1)
+    """
+    assert compile_code(code) is not None
+
+
+def test_event_with_address_name_and_type():
+    code = """
+event E:
+    address: address
+
+@external
+def foo():
+    log E(address=msg.sender)
+    """
+    assert compile_code(code) is not None
```

### tests/functional/syntax/test_flag.py
```diff
@@ -182,6 +182,20 @@ def run() -> Order:
 flag A:
     a
     """,
+    """
+flag F:
+    address
+    other
+    """,
+    """
+flag F:
+    address
+    other
+
+@external
+def run() -> F:
+    return F.address
+    """,
 ]
 
 
```

### vyper/semantics/types/module.py
```diff
@@ -58,11 +58,12 @@ def __init__(
         assert len(members) == len(functions) + len(events) + len(errors) + len(structs) + len(
             flags
         )
+        # super().__init__ uses self._id in errors
+        self._id = _id
 
         super().__init__(functions)
 
         self._helper = VyperType(events | errors | structs | flags)
-        self._id = _id
         self._helper._id = _id
         self.functions = functions
         self.events = events
```
