# [?] quic: fix integer underflow in ACK handler

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-03-01
Source: https://github.com/firedancer-io/firedancer/commit/0918bc166007bcd02efad0c39406b13af34d8419
Type: security-commit

## Details
quic: fix integer underflow in ACK handler

When a peer ACKs packet number 0 (the first packet in a connection),
the expression `largest_ack-1` wraps to ULONG_MAX. The subsequent
treap lookup idx_le(~0UL) returns the element with the largest key,
causing the skip_ceil computation to iterate from the wrong end of
the data structure. This incorrectly marks unrelated packets as
"lost", triggering spurious retransmissions.

## Patch
### src/waltz/quic/fd_quic.c
```diff
@@ -4792,8 +4792,8 @@ fd_quic_handle_ack_frame( fd_quic_frame_ctx_t * context,
      We unfortunately can't just use 'largest_ack-3' because 1) largest_ack'd
      may have been previously acknowledged and 2) we may have skipped pkt_nums.
    */
-  ulong skip_ceil;
-  {
+  ulong skip_ceil = 0UL;
+  if( FD_LIKELY( largest_ack > 0UL ) ) {
     #define FD_QUIC_K_PACKET_THRESHOLD 3
     fd_quic_pkt_meta_tracker_t * tracker  = &conn->pkt_meta_tracker;
     fd_quic_pkt_meta_t         * pool     = tracker->pool;
```

### src/waltz/quic/tests/test_quic_conformance.c
```diff
@@ -704,6 +704,36 @@ test_quic_pktmeta_pktnum_skip( fd_quic_sandbox_t * sandbox,
   FD_TEST( *metrics_alloc_fail_cnt == alloc_fail_cnt );
 }
 
+/* Regression test for integer underflow in ACK handler */
+
+static __attribute__ ((noinline)) void
+test_quic_ack_largest_ack_zero( fd_quic_sandbox_t * sandbox,
+                                fd_rng_t *          rng ) {
+
+  fd_quic_sandbox_init( sandbox, FD_QUIC_ROLE_SERVER );
+  fd_quic_t *       quic  = sandbox->quic;
+  fd_quic_state_t * state = fd_quic_get_state( quic );
+  fd_quic_conn_t *  conn  = fd_quic_sandbox_new_conn_established( sandbox, rng );
+
+  for( uint j = 0; j < 5; j++ ) {
+    conn->flags          = ( conn->flags & ~FD_QUIC_CONN_FLAGS_PING_SENT ) | FD_QUIC_CONN_FLAGS_PING;
+    conn->upd_pkt_number = FD_QUIC_PKT_NUM_PENDING;
+    sandbox->wallclock  += (long)10e6;
+    conn->svc_meta.next_timeout = sandbox->wallclock;
+    fd_quic_svc_timers_schedule( state->svc_timers, conn, sandbox->wallclock );
+    fd_quic_service( quic, sandbox->wallclock );
+  }
+  FD_TEST( conn->pkt_number[2] == 5UL );
+
+  ulong retx_before = quic->metrics.pkt_retransmissions_cnt[ fd_quic_enc_level_appdata_id ];
+  uchar ack_frame[] = { 0x02, 0x00, 0x00, 0x00, 0x00 };
+  fd_quic_sandbox_send_lone_frame( sandbox, conn, ack_frame, sizeof(ack_frame) );
+  FD_TEST( conn->state == FD_QUIC_CONN_STATE_ACTIVE );
+  /* No retransmissions triggered (regression test) */
+  ulong retx_after = quic->metrics.pkt_retransmissions_cnt[ fd_quic_enc_level_appdata_id ];
+  FD_TEST( retx_after == retx_before );
+}
+
 static void
 test_quic_rtt_sample( void ) {
   fd_quic_t quic = {0};
@@ -826,6 +856,7 @@ main( int     argc,
   test_quic_parse_path_challenge();
   test_quic_conn_free                    ( sandbox, rng );
   test_quic_pktmeta_pktnum_skip          ( sandbox, rng );
+  test_quic_ack_largest_ack_zero         ( sandbox, rng );
   test_quic_rtt_sample();
 
   /* Wind down */
```
