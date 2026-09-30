# [?] quic: prevent underflow in conn_tx with initial

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-03-01
Source: https://github.com/firedancer-io/firedancer/commit/9956c3f606892a974e33eba537316eb770bbadc0
Type: security-commit

## Details
quic: prevent underflow in conn_tx with initial

This is not actually a reachable bug today, but adds some defense
in depth, to make sure the padding calculation stays intact if
outgoing initial packet size increases.

## Patch
### src/waltz/quic/fd_quic.c
```diff
@@ -3789,7 +3789,8 @@ fd_quic_conn_tx( fd_quic_t      * quic,
        all short quic packets are padded so 16 bytes of sample are available */
     uint tot_frame_sz = (uint)( payload_ptr - frame_start );
     uint base_pkt_len = (uint)tot_frame_sz + pkt_num_len + FD_QUIC_CRYPTO_TAG_SZ;
-    uint padding      = initial_pkt ? FD_QUIC_INITIAL_PAYLOAD_SZ_MIN - base_pkt_len : 0u;
+    uint padding      = ( initial_pkt && (base_pkt_len < FD_QUIC_INITIAL_PAYLOAD_SZ_MIN) )
+                            ? FD_QUIC_INITIAL_PAYLOAD_SZ_MIN - base_pkt_len : 0u;
 
     if( base_pkt_len + padding < FD_QUIC_CRYPTO_SAMPLE_OFFSET_FROM_PKT_NUM_START + FD_QUIC_CRYPTO_SAMPLE_SZ ) {
       padding = FD_QUIC_CRYPTO_SAMPLE_SZ + FD_QUIC_CRYPTO_SAMPLE_OFFSET_FROM_PKT_NUM_START - base_pkt_len;
```
