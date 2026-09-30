# [?] [Tolk] Fix potential overflow on parsing `obj.index_at`

## Summary
Severity: Unknown
Chain: TON
Component: ton-blockchain/ton
Published: 2025-05-29
Source: https://github.com/ton-blockchain/ton/commit/49729a1de9089549c30aa21c4cfee8602ef514d7
Type: security-commit

## Details
[Tolk] Fix potential overflow on parsing `obj.index_at`

## Patch
### tolk-tester/tests/invalid-semantics/err-4208.tolk
```diff
@@ -0,0 +1,6 @@
+const flyp = 9999999.77777777777777;
+
+/**
+@compilation_should_fail
+@stderr invalid numeric index
+ */
```

### tolk/pipe-infer-types-and-calls.cpp
```diff
@@ -21,6 +21,7 @@
 #include "generics-helpers.h"
 #include "type-system.h"
 #include "smart-casts-cfg.h"
+#include <charconv>
 
 /*
  *   This is a complicated and crucial part of the pipeline. It simultaneously does the following:
@@ -168,6 +169,12 @@ static void fire_error_method_not_found(FunctionPtr cur_f, SrcLocation loc, Type
   fire(cur_f, loc, "method `" + to_string(method_name) + "` not found");
 }
 
+// safe version of std::stoi that does not crash on long numbers
+static bool try_parse_string_to_int(std::string_view str, int& out) {
+  auto result = std::from_chars(str.data(), str.data() + str.size(), out);
+  return result.ec == std::errc() && result.ptr == str.data() + str.size();
+}
+
 // helper function: given hint = `Ok<int> | Err<slice>` and struct `Ok`, return `Ok<int>`
 // example: `match (...) { Ok => ... }` we need to deduce `Ok<T>` based on subject
 static TypePtr try_pick_instantiated_generic_from_hint(TypePtr hint, StructPtr lookup_ref) {
@@ -970,7 +977,10 @@ class InferTypesAndCallsAndFieldsVisitor final {
 
     // check for indexed access (`tensorVar.0` / `tupleVar.1`)
     if (!fun_ref && field_name[0] >= '0' && field_name[0] <= '9') {
-      int index_at = std::stoi(std::string(field_name));
+      int index_at;
+      if (!try_parse_string_to_int(field_name, index_at)) {
+        fire(cur_f, v_ident->loc, "invalid numeric index");
+      }
       if (const auto* t_tensor = obj_type->try_as<TypeDataTensor>()) {
         if (index_at >= t_tensor->size()) {
           fire(cur_f, v_ident->loc, "invalid tensor index, expected 0.." + std::to_string(t_tensor->items.size() - 1));
```
