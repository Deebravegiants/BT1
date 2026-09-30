# [?] Fix overflow bug

## Summary
Severity: Unknown
Chain: Monad
Component: category-labs/monad
Published: 2025-03-06
Source: https://github.com/category-labs/monad/commit/d375f64e238fa4ea70fa8645713fe5bf8ebd04d3
Type: security-commit

## Details
Fix overflow bug

## Patch
### libs/vm/libs/interpreter/src/monad/interpreter/call_runtime.hpp
```diff
@@ -65,8 +65,10 @@ namespace monad::interpreter
 
         std::apply(f, all_args);
 
-        constexpr auto stack_adjustment =
-            stack_arg_count - (use_result ? 1 : 0);
+        static_assert(
+            stack_arg_count <= std::numeric_limits<std::ptrdiff_t>::max());
+        constexpr std::ptrdiff_t stack_adjustment =
+            static_cast<std::ptrdiff_t>(stack_arg_count) - (use_result ? 1 : 0);
         state.stack_top -= stack_adjustment;
     }
 }
```
