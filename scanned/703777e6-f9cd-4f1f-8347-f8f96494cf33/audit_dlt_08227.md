# [?] topo: fix crash with only one CPU

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-09-15
Source: https://github.com/firedancer-io/firedancer/commit/0a41d5e8686732e873bdb92cc5bfad772b8cc501
Type: security-commit

## Details
topo: fix crash with only one CPU

## Patch
### src/disco/topo/fd_cpu_topo.c
```diff
@@ -43,7 +43,7 @@ fd_topo_cpu_cnt( void ) {
   char * saveptr;
   char * token = strtok_r( line, "-", &saveptr );
   token = strtok_r( NULL, "-", &saveptr );
-  ulong end = fd_cstr_to_ulong( token );
+  ulong end = fd_cstr_to_ulong( token ? token : line );
 
   return end+1UL;
 }
```
