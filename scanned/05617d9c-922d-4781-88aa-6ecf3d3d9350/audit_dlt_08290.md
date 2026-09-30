# [?] asiegel/log-buffer-overflow: fixed log buffer size

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-05-06
Source: https://github.com/firedancer-io/firedancer/commit/2777f4911d4d3bcd97cd7b0c4965046ffb183455
Type: security-commit

## Details
asiegel/log-buffer-overflow: fixed log buffer size

## Patch
### src/disco/topo/fd_topo.c
```diff
@@ -317,7 +317,7 @@ fd_topo_mem_sz_string( ulong sz, char out[static 24] ) {
 void
 fd_topo_print_log( int         stdout,
                    fd_topo_t * topo ) {
-  char message[ 16UL*4096UL ] = {0}; /* Same as FD_LOG_BUF_SZ */
+  char message[ 32UL*4096UL ] = {0}; /* Same as FD_LOG_BUF_SZ */
 
   char * cur = message;
   ulong remaining = sizeof(message) - 1; /* Leave one character at the end to ensure NUL terminated */
```
