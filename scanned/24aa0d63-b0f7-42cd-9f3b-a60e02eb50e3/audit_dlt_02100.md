# [?] fix memory corruption with calls inside events

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2021-08-04
Source: https://github.com/vyperlang/vyper/commit/cea5dd89dab17031b7c508bc5b9feaa47ff2e7db
Type: security-commit

## Details
fix memory corruption with calls inside events

The key is to make sure the memory is allocated and registered with the
context variable BEFORE evaluating the expressions inside the event (in
case any of them make internal calls)

fixes #1476

## Patch
### vyper/ast/folding.py
```diff
@@ -177,6 +177,9 @@ def replace_user_defined_constants(vyper_module: vy_ast.Module) -> int:
     return changed_nodes
 
 
+# TODO constant folding on log events
+
+
 def _replace(old_node, new_node):
     if isinstance(new_node, vy_ast.Constant):
         return new_node.from_node(old_node, value=new_node.value)
```

### vyper/old_codegen/events.py
```diff
@@ -1,13 +1,24 @@
+from typing import List, Tuple
+
+import vyper.ast as vy_ast
 from vyper.exceptions import TypeMismatch
-from vyper.old_codegen.abi import abi_encode, abi_type_of, lll_tuple_from_args
+from vyper.old_codegen.abi import (
+    ABI_Tuple,
+    abi_encode,
+    abi_type_of,
+    abi_type_of2,
+    lll_tuple_from_args,
+)
+from vyper.old_codegen.context import Context
 from vyper.old_codegen.keccak256_helper import keccak256_helper
 from vyper.old_codegen.lll_node import LLLnode
-from vyper.old_codegen.parser_utils import unwrap_location
+from vyper.old_codegen.parser_utils import getpos, unwrap_location
 from vyper.old_codegen.types.types import (
     BaseType,
     ByteArrayLike,
-    ByteArrayType,
+    get_type_for_exact_size,
 )
+from vyper.semantics.types import Event
 
 
 # docs.soliditylang.org/en/v0.8.6/abi-spec.html#indexed-event-encoding
@@ -36,27 +47,62 @@ def _gas_bound(num_topics, data_maxlen):
     return LOG_BASE_GAS + GAS_PER_TOPIC * num_topics + GAS_PER_LOG_BYTE * data_maxlen
 
 
+def allocate_buffer_for_log(
+    event: Event, args: List[vy_ast.VyperNode], context: Context
+) -> Tuple[int, int]:
+    """Allocate a buffer to ABI-encode the non-indexed (data) arguments into
+
+    This must be done BEFORE compiling the event arguments to LLL,
+    registering the buffer with the `context` variable (otherwise any
+    function calls inside the event literal will clobber the buffer).
+    """
+    # remove non-data args, as those don't go into the buffer
+    arg_types = [
+        arg._metadata["type"] for arg, is_index in zip(args, event.indexed) if not is_index
+    ]
+    # all args get encoded as one big tuple
+    abi_t = ABI_Tuple([abi_type_of2(arg_t) for arg_t in arg_types])
+
+    # make a buffer for the encoded data output
+    buf_maxlen = abi_t.size_bound()
+    t = get_type_for_exact_size(buf_maxlen)
+    return context.new_internal_variable(t), buf_maxlen
+
+
 # docs.soliditylang.org/en/v0.8.6/abi-spec.html#events
-def lll_node_for_log(expr, event, topic_nodes, data_nodes, pos, context):
+def lll_node_for_log(expr, buf, _maxlen, event, topic_nodes, data_nodes, context):
+    """Taking LLL nodes as arguments, create the LLL node for a Log statement.
+
+    Arguments:
+      expr: The original Log expression
+      buf: A pre-allocated buffer for the output
+      _maxlen: The length of the buffer, for sanity checking
+      event: The Event type
+      topic_nodes: list of LLLnodes which calculate the event topics
+      data_nodes: list of LLLnodes which calculate the event data
+      context: current memory/frame context
+    """
+    _pos = getpos(expr)
+
     topics = _encode_log_topics(expr, event.event_id, topic_nodes, context)
 
     data = lll_tuple_from_args(data_nodes)
 
-    # make a buffer for the encoded data output
-    buf_maxlen = abi_type_of(data.typ).size_bound()
-    buf = context.new_internal_variable(ByteArrayType(maxlen=buf_maxlen))
+    # sanity check, abi size_bound is the same calculated both ways
+    print(data.typ, type(data.typ))
+    assert abi_type_of(data.typ).size_bound() == _maxlen, "bad buffer size"
 
     # encode_data is an LLLnode which, cleverly, both encodes the data
     # and returns the length of the encoded data as a stack item.
-    encode_data = abi_encode(buf, data, pos=pos, returns_len=True)
+    encode_data = abi_encode(buf, data, pos=_pos, returns_len=True)
 
     assert len(topics) <= 4, "too many topics"  # sanity check
     log_opcode = "log" + str(len(topics))
 
     return LLLnode.from_list(
         [log_opcode, buf, encode_data] + topics,
-        add_gas_estimate=_gas_bound(len(topics), buf_maxlen),
+        add_gas_estimate=_gas_bound(len(topics), _maxlen),
         typ=None,
-        pos=pos,
+        pos=_pos,
         annotation=f"LOG event {event.signature}",
     )
```

### vyper/old_codegen/stmt.py
```diff
@@ -108,18 +108,22 @@ def parse_If(self):
     def parse_Log(self):
         event = self.stmt._metadata["type"]
 
+        # do this BEFORE evaluating args to LLL to protect the buffer
+        # from internal call clobbering
+        buf, _len = events.allocate_buffer_for_log(event, self.stmt.value.args, self.context)
+
         args = [Expr(arg, self.context).lll_node for arg in self.stmt.value.args]
 
-        topic_nodes = []
-        data_nodes = []
+        topic_lll = []
+        data_lll = []
         for arg, is_indexed in zip(args, event.indexed):
             if is_indexed:
-                topic_nodes.append(arg)
+                topic_lll.append(arg)
             else:
-                data_nodes.append(arg)
+                data_lll.append(arg)
 
         return events.lll_node_for_log(
-            self.stmt, event, topic_nodes, data_nodes, getpos(self.stmt), self.context
+            self.stmt, buf, _len, event, topic_lll, data_lll, self.context
         )
 
     def parse_Call(self):
```

### vyper/old_codegen/types/types.py
```diff
@@ -269,6 +269,11 @@ def parse_type(item, location, sigs=None, custom_structs=None):
         raise InvalidType("Invalid type", item)
 
 
+# byte array overhead, in words. (it should really be 1, but there are
+# some places in our calling convention where the layout expects 2)
+BYTE_ARRAY_OVERHEAD = 2
+
+
 # Gets the maximum number of memory or storage keys needed to ABI-encode
 # a given type
 def get_size_of_type(typ):
@@ -277,7 +282,7 @@ def get_size_of_type(typ):
     elif isinstance(typ, ByteArrayLike):
         # 1 word for offset (in static section), 1 word for length,
         # up to maxlen words for actual data.
-        return ceil32(typ.maxlen) // 32 + 2
+        return ceil32(typ.maxlen) // 32 + BYTE_ARRAY_OVERHEAD
     elif isinstance(typ, ListType):
         return get_size_of_type(typ.subtype) * typ.count
     elif isinstance(typ, MappingType):
@@ -288,6 +293,17 @@ def get_size_of_type(typ):
         raise InvalidType(f"Can not get size of type, Unexpected type: {repr(typ)}")
 
 
+def get_type_for_exact_size(n_bytes):
+    """Create a type which will take up exactly n_bytes. Used for allocating internal buffers.
+
+    Parameters:
+      n_bytes: the number of bytes to allocate
+    Returns:
+      type: A type which can be passed to context.new_variable
+    """
+    return ByteArrayType(n_bytes - 32 * BYTE_ARRAY_OVERHEAD)
+
+
 # amount of space a type takes in the static section of its ABI encoding
 def get_static_size_of_type(typ):
     if isinstance(typ, BaseType):
```

### vyper/semantics/types/__init__.py
```diff
@@ -2,6 +2,7 @@
 from .abstract import SignedIntegerAbstractType, UnsignedIntegerAbstractType
 from .bases import BasePrimitive
 from .indexable.sequence import ArrayDefinition, TupleDefinition
+from .user.event import Event
 from .user.struct import StructDefinition
 from .value.address import AddressDefinition
 from .value.array_value import BytesArrayDefinition, StringDefinition
```
