# [?] GH-395 Avoid overflow

## Summary
Severity: Unknown
Chain: EOS/Vaulta
Component: AntelopeIO/leap
Published: 2023-02-10
Source: https://github.com/AntelopeIO/leap/commit/305f41b7c6745d907fd5887d1c3f36f2f7c80c2c
Type: security-commit

## Details
GH-395 Avoid overflow

## Patch
### plugins/resource_monitor_plugin/include/eosio/resource_monitor_plugin/file_space_handler.hpp
```diff
@@ -189,7 +189,7 @@ namespace eosio::resource_monitor {
       bool     output_threshold_warning {true};
 
    private:
-      uint32_t to_gib(uint64_t bytes) {
+      uint64_t to_gib(uint64_t bytes) {
          return bytes/1024/1024/1024;
       }
 
```
