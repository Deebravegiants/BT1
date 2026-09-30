# [?] gossip: fix crds parsing overflow check

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-08-25
Source: https://github.com/firedancer-io/firedancer/commit/1efec62c0d6367d491349ee1ac4c14261ac2e3ab
Type: security-commit

## Details
gossip: fix crds parsing overflow check

Ensures 16-bit addition cannot overflow by checking the sum in a wider type against USHORT_MAX, avoiding incorrect results due to integer promotions.

## Patch
### src/flamenco/gossip/fd_gossip_msg_parse.c
```diff
@@ -354,7 +354,7 @@ fd_gossip_msg_crds_contact_info_parse( fd_gossip_view_crds_value_t * crds_val,
     CHECK_LEFT( 1U ); socket->key   = FD_LOAD( uchar, CURSOR )                                                                 ; INC( 1U );
     CHECK_LEFT( 1U ); socket->index = FD_LOAD( uchar, CURSOR )                                                                 ; INC( 1U );
     READ_CHECKED_COMPACT_U16( decode_sz, socket->offset, CUR_OFFSET )                                                          ; INC( decode_sz );
-    CHECK( socket->offset+offset>=offset ); /* Check for overflow */
+    CHECK( ((uint)offset + (uint)socket->offset)<=(uint)USHORT_MAX ); /* overflow check */
     offset = (ushort)(offset + socket->offset);
     CHECK( !socket_tag_set_test( socket_tag_hits, socket->key ) ); socket_tag_set_insert( socket_tag_hits, socket->key );
     CHECK( socket->index<crds_val->contact_info->addrs_len );
```
