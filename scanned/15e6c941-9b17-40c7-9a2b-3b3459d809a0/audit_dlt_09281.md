# [?] Fixes overflow.

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2017-10-03
Source: https://github.com/vyperlang/vyper/commit/1db7af99a26338822df290970e3405e290b09a85
Type: security-commit

## Details
Fixes overflow.

## Patch
### tests/parser/types/numbers/test_num256.py
```diff
@@ -80,17 +80,20 @@ def built_in_conversion(x: num256) -> num:
     """
 
     c = get_contract(code)
+
+    # Ensure uint256 function signature.
+    assert c.translator.function_data['_num256_to_num']['encode_types'] == ['uint256']
+
     assert c._num256_to_num(1) == 1
     assert c._num256_to_num((2**127) - 1) == 2**127 - 1
     t.s = s
     assert_tx_failed(t, lambda: c._num256_to_num((2**128)) == 0)
     assert c._num256_to_num_call(1) == 1
-    # Make sure it has int128 overflow
-    assert c._num256_to_num_call(2**127) == -170141183460469231731687303715884105728
+
     # Check that casting matches manual conversion
     assert c._num256_to_num_call(2**127 - 1) == c.built_in_conversion(2**127 - 1)
 
     # Pass in negative int.
     assert_tx_failed(t, lambda: c._num256_to_num(-1) != -1, ValueOutOfBounds)
-    # Ensure uint256 function signature.
-    assert c.translator.function_data['_num256_to_num']['encode_types'] == ['uint256']
+    # Make sure it can't be coherced into a negative number.
+    assert_tx_failed(t, lambda: c._num256_to_num_call(2**127))
```

### viper/parser.py
```diff
@@ -230,10 +230,10 @@ def get_contracts_and_defs_and_globals(code):
 initializer_lll = LLLnode.from_list(['seq',
                                         ['mstore', 28, ['calldataload', 0]],
                                         ['mstore', ADDRSIZE_POS, 2**160],
-                                        ['mstore', MAXNUM_POS, 2**128 - 1],
-                                        ['mstore', MINNUM_POS, -2**128 + 1],
-                                        ['mstore', MAXDECIMAL_POS, (2**128 - 1) * DECIMAL_DIVISOR],
-                                        ['mstore', MINDECIMAL_POS, (-2**128 + 1) * DECIMAL_DIVISOR],
+                                        ['mstore', MAXNUM_POS, 2**127 - 1],
+                                        ['mstore', MINNUM_POS, -2**127],
+                                        ['mstore', MAXDECIMAL_POS, (2**127 - 1) * DECIMAL_DIVISOR],
+                                        ['mstore', MINDECIMAL_POS, (-2**127 + 1) * DECIMAL_DIVISOR],
                                     ], typ=None)
 
 
```

### viper/parser_utils.py
```diff
@@ -409,7 +409,7 @@ def base_type_conversion(orig, frm, to):
     elif is_base_type(frm, 'num') and is_base_type(to, 'decimal') and are_units_compatible(frm, to):
         return LLLnode.from_list(['mul', orig, DECIMAL_DIVISOR], typ=BaseType('decimal', to.unit, to.positional))
     elif is_base_type(frm, 'num256') and is_base_type(to, 'num') and are_units_compatible(frm, to):
-        return LLLnode.from_list(['clamp', 0, orig, ['mload', MAXNUM_POS]], typ=BaseType("num"))
+        return LLLnode.from_list(['uclample', orig, ['mload', MAXNUM_POS]], typ=BaseType("num"))
     elif isinstance(frm, NullType):
         if to.typ not in ('num', 'bool', 'num256', 'address', 'bytes32', 'decimal'):
             raise TypeMismatchException("Cannot convert null-type object to type %r" % to)
```

### viper/types.py
```diff
@@ -48,10 +48,12 @@ class NodeType():
 
 # Data structure for a type that representsa 32-byte object
 class BaseType(NodeType):
-    def __init__(self, typ, unit=False, positional=False):
+
+    def __init__(self, typ, unit=False, positional=False, override_signature=False):
         self.typ = typ
         self.unit = {} if unit is False else unit
         self.positional = positional
+        self.override_signature = override_signature
 
     def __eq__(self, other):
         return other.__class__ == BaseType and self.typ == other.typ and self.unit == other.unit and self.positional == other.positional
@@ -156,7 +158,7 @@ def canonicalize_type(t, is_event=False):
     if not isinstance(t, BaseType):
         raise Exception("Cannot canonicalize non-base type: %r" % t)
 
-    num256_override = True if getattr(t, 'num256_signature', False) else False
+    num256_override = True if t.override_signature == 'num256' else False
 
     t = t.typ
     if t == 'num' and not num256_override:
@@ -260,10 +262,8 @@ def parse_type(item, location):
         if len(argz) != 1:
             raise InvalidTypeException("Malformed unit type", item)
         # Check for num256 to num casting
-        if item.func.id == 'num' and item.args[0].id == 'num256':
-            _typ = BaseType('num')
-            setattr(_typ, 'num256_signature', True)
-            return _typ
+        if item.func.id == 'num' and getattr(item.args[0], 'id', '') == 'num256':
+            return BaseType('num', override_signature='num256')
         unit = parse_unit(argz[0])
         return BaseType(base_type, unit, positional)
     # Subscripts
```
