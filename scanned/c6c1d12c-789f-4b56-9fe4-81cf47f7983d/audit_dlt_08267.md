# [?] quic: fix overflow in max_idle_timeout_ms

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-12-23
Source: https://github.com/firedancer-io/firedancer/commit/98e8295664900c828551a832895970abfc3f33ef
Type: security-commit

## Details
quic: fix overflow in max_idle_timeout_ms

## Patch
### src/util/bits/fd_sat.h
```diff
@@ -78,7 +78,12 @@ fd_long_sat_sub( long x, long y ) {
   return fd_long_if( cf, (long)((ulong)x >> 63) + LONG_MAX, res );
 }
 
-/* fd_long_sat_mul is left as an exercise to the reader */
+FD_FN_CONST static inline long
+fd_long_sat_mul( long x, long y ) {
+  long res;
+  int cf = __builtin_smull_overflow ( x, y, &res );
+  return fd_long_if( cf, (long)((ulong)((x ^ y) >> 63)) + LONG_MAX, res );
+}
 
 FD_FN_CONST static inline uint
 fd_uint_sat_add( uint x, uint y ) {
```

### src/waltz/quic/fd_quic.c
```diff
@@ -2710,7 +2710,7 @@ fd_quic_apply_peer_params( fd_quic_conn_t *                   conn,
 
   /* set the max_idle_timeout to the min of our and peer max_idle_timeout */
   if( peer_tp->max_idle_timeout_ms ) {
-    long peer_max_idle_timeout_ns = (long)peer_tp->max_idle_timeout_ms * (long)1e6;
+    long peer_max_idle_timeout_ns = fd_long_sat_mul( (long)peer_tp->max_idle_timeout_ms, (long)1e6);
     conn->idle_timeout_ns         = fd_long_min( peer_max_idle_timeout_ns, conn->idle_timeout_ns );
   }
 
```
