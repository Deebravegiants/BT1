# [?] fix: use clamp to limit maximum size of cache to avoid signed integer overflow

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2026-08-25
Source: https://github.com/dashpay/dash/commit/c87bc456f461c5f9ea5409b7aee8c550ae2bcbb5
Type: security-commit

## Details
fix: use clamp to limit maximum size of cache to avoid signed integer overflow

## Patch
### src/node/validation_cache_args.cpp
```diff
@@ -11,6 +11,7 @@
 #include <algorithm>
 #include <cstddef>
 #include <cstdint>
+#include <limits>
 #include <memory>
 #include <optional>
 
@@ -24,7 +25,8 @@ void ApplyArgsManOptions(const ArgsManager& argsman, ValidationCacheSizes& cache
         //    InitScriptExecutionCache create the minimum possible cache (2
         //    elements). Therefore, we can use 0 as a floor here.
         // 2. Multiply first, divide after to avoid integer truncation.
-        size_t clamped_size_each = std::max<int64_t>(*max_size, 0) * (1 << 20) / 2;
+        int64_t upper_limit = std::numeric_limits<int64_t>::max() / (1 << 20);
+        size_t clamped_size_each = std::clamp<int64_t>(*max_size, 0, upper_limit) * (1 << 20) / 2;
         cache_sizes = {
             .signature_cache_bytes = clamped_size_each,
             .script_execution_cache_bytes = clamped_size_each,
```
