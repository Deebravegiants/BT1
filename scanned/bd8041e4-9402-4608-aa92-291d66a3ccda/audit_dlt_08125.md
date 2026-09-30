# [?] GCC: Fix -Wstringop-overflow= warnings

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2022-05-17
Source: https://github.com/monero-project/monero/commit/5858f05f9bbbcfeca77cda249d26fe05bca5cc38
Type: security-commit

## Details
GCC: Fix -Wstringop-overflow= warnings

Resolves #8320

## Patch
### external/boost/archive/portable_binary_archive.hpp
```diff
@@ -44,9 +44,12 @@ reverse_bytes(signed char size, char *address){
     char * first = address;
     char * last = first + size - 1;
     for(;first < last;++first, --last){
+#pragma GCC diagnostic push
+#pragma GCC diagnostic ignored "-Wstringop-overflow="
         char x = *last;
         *last = *first;
         *first = x;
+#pragma GCC diagnostic pop
     }
 }
 
```
