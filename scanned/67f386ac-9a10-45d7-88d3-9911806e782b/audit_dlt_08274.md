# [?] snapshots: more accurate ssping latencies and fix crash

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-10-31
Source: https://github.com/firedancer-io/firedancer/commit/b7ce350fabbe542d5ac392d568e56e36233605c5
Type: security-commit

## Details
snapshots: more accurate ssping latencies and fix crash

## Patch
### src/discof/restore/utils/fd_ssping.c
```diff
@@ -297,8 +297,7 @@ fd_ssping_invalidate( fd_ssping_t * ssping,
 }
 
 static inline void
-recv_pings( fd_ssping_t * ssping,
-            long          now ) {
+recv_pings( fd_ssping_t * ssping ) {
   for( ulong i=0UL; i<PING_BURST_MAX; i++ ) {
     struct ssping_pkt  pkt;
     struct sockaddr_in addr;
@@ -313,9 +312,10 @@ recv_pings( fd_ssping_t * ssping,
     fd_ssping_peer_t * peer = peer_map_ele_query( ssping->map, &key, NULL, ssping->pool );
     if( FD_UNLIKELY( peer==NULL || ( peer->state!=PEER_STATE_PINGED && peer->state!=PEER_STATE_REFRESHING ) ) ) continue;
 
+    long now = fd_log_wallclock();
+
     deadline_list_ele_remove( peer->state==PEER_STATE_PINGED ? ssping->pinged : ssping->refreshing, peer, ssping->pool );
-    FD_TEST( peer->deadline_nanos-PEER_DEADLINE_NANOS_PING<now );
-    peer->latency_nanos  = (ulong)(now - (peer->deadline_nanos - PEER_DEADLINE_NANOS_PING));
+    peer->latency_nanos  = (ulong)fd_long_max( now - (peer->deadline_nanos - PEER_DEADLINE_NANOS_PING), 1L );
     peer->state          = PEER_STATE_VALID;
     peer->deadline_nanos = now + PEER_DEADLINE_NANOS_VALID;
     deadline_list_ele_push_tail( ssping->valid, peer, ssping->pool );
@@ -430,5 +430,5 @@ fd_ssping_advance( fd_ssping_t *          ssping,
     deadline_list_ele_push_tail( ssping->unpinged, peer, ssping->pool );
   }
 
-  recv_pings( ssping, now );
+  recv_pings( ssping );
 }
```
