# [?] Fix crash.

## Summary
Severity: Unknown
Chain: EOS/Vaulta
Component: AntelopeIO/leap
Published: 2023-05-18
Source: https://github.com/AntelopeIO/leap/commit/2fe5079e3eddd31a1fbb1e7f9da3d0e4ec329039
Type: security-commit

## Details
Fix crash.

## Patch
### libraries/chain/include/eosio/chain/abi_serializer.hpp
```diff
@@ -1090,13 +1090,20 @@ class caching_resolver {
 
    std::optional<std::reference_wrapper<const abi_serializer>> operator()(const account_name& account) const {
       auto it = abi_serializers.find(account);
-      if (it != abi_serializers.end() && it->second)
-         return *it->second;
+      if (it != abi_serializers.end()) {
+         if (it->second)
+            return *it->second;
+         return {};
+      }
       try {
          auto serializer = resolver_(account);
-         auto& dest = abi_serializers[account];
-         dest = abi_serializer_cache_t::mapped_type{std::move(serializer)};
-         return *dest;
+         auto& dest = abi_serializers[account]; // add entry regardless
+         if (serializer) {
+            // we got a serializer, so move it into the cache
+            dest = abi_serializer_cache_t::mapped_type{std::move(*serializer)};
+            return *dest; // and return a reference to it
+         }
+         return {}; 
       } catch( ... ) {
          throw; // throw if embedded resolver throws
       }
```
