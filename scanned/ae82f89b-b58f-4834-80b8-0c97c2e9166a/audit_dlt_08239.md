# [?] quic: fix OOB read in fuzz_quic_wire encrypt_packet

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-08-12
Source: https://github.com/firedancer-io/firedancer/commit/5a1dea68cfd89ade1975f4f3dba6cbb03c1de6e6
Type: security-commit

## Details
quic: fix OOB read in fuzz_quic_wire encrypt_packet

## Patch
### src/waltz/quic/tests/fuzz_quic_wire.c
```diff
@@ -440,15 +440,15 @@ encrypt_packet( uchar * const data,
   uchar const * hdr    = data;
   ulong         hdr_sz = pkt_num_pnoff + pkt_number_sz;
 
+  if( ( out_sz          < hdr_sz ) |
+      ( out_sz - hdr_sz < FD_QUIC_CRYPTO_TAG_SZ ) )
+    return size;
+
   ulong pkt_number = 0UL;
   for( ulong j = 0UL; j < pkt_number_sz; ++j ) {
     pkt_number = ( pkt_number << 8UL ) + (ulong)( hdr[pkt_num_pnoff + j] );
   }
 
-  if( ( out_sz          < hdr_sz ) |
-      ( out_sz - hdr_sz < FD_QUIC_CRYPTO_TAG_SZ ) )
-    return size;
-
   uchar const * pay    = hdr + hdr_sz;
   ulong         pay_sz = out_sz - hdr_sz - FD_QUIC_CRYPTO_TAG_SZ;
 
```
