# [?] fix buffer overrun in disco/topo

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-02-13
Source: https://github.com/firedancer-io/firedancer/commit/42c64284547448d5975d44fbe8b751386f0f43ef
Type: security-commit

## Details
fix buffer overrun in disco/topo

When printing tile layout information the macro PRINTOUT tries to
ensure that the buffer of size 256 is not overrun. Unfortunately
due to a copy-paste bug this check is not properly done and long
output will cause a buffer overflow.

## Patch
### src/disco/topo/fd_topo.c
```diff
@@ -447,7 +447,7 @@ fd_topo_print_log( int         stdout,
   } while( 0 )
 
 #define PRINTOUT( ... ) do {                                                            \
-    int n = snprintf( cur_out, remaining_in, __VA_ARGS__ );                             \
+    int n = snprintf( cur_out, remaining_out, __VA_ARGS__ );                            \
     if( FD_UNLIKELY( n < 0 ) ) FD_LOG_ERR(( "snprintf failed" ));                       \
     if( FD_UNLIKELY( (ulong)n >= remaining_out ) ) FD_LOG_ERR(( "snprintf overflow" )); \
     remaining_out -= (ulong)n;                                                          \
```
