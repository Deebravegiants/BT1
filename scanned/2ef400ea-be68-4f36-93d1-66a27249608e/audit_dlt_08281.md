# [?] send, writer: fix buffer overflows by fd_txn_parse

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-09-19
Source: https://github.com/firedancer-io/firedancer/commit/3d4cbe567f064724f30afa70f3a07e7e7c36da99
Type: security-commit

## Details
send, writer: fix buffer overflows by fd_txn_parse

## Patch
### src/app/firedancer-dev/commands/send_test/send_test_helpers.c
```diff
@@ -230,8 +230,8 @@ encode_vote( send_test_ctx_t * ctx, fd_tower_slot_done_t * slot_done ) {
   fd_memcpy( slot_done->vote_txn, txn->payload, txn->payload_sz );
   slot_done->vote_txn_sz = txn->payload_sz;
 
-  fd_txn_t txn_t;
-  FD_TEST( fd_txn_parse( slot_done->vote_txn, slot_done->vote_txn_sz, &txn_t, NULL ) );
+  uchar txn_mem[ FD_TXN_MAX_SZ ] __attribute__((aligned(alignof(fd_txn_t))));
+  FD_TEST( fd_txn_parse( slot_done->vote_txn, slot_done->vote_txn_sz, txn_mem, NULL ) );
 }
 
 #endif /* FD_SRC_APP_FIREDANCER_DEV_COMMANDS_SEND_TEST_HELPERS_C */
```

### src/discof/send/fd_send_tile.c
```diff
@@ -448,13 +448,14 @@ handle_vote_msg( fd_send_tile_ctx_t * ctx,
                  uchar *              signed_vote_txn,
                  ulong                vote_txn_sz ) {
 
-  fd_txn_t txn;
-  FD_TEST( fd_txn_parse( signed_vote_txn, vote_txn_sz, &txn, NULL ) );
+  uchar txn_mem[ FD_TXN_MAX_SZ ] __attribute__((aligned(alignof(fd_txn_t))));
+  fd_txn_t * txn = (fd_txn_t *)txn_mem;
+  FD_TEST( fd_txn_parse( signed_vote_txn, vote_txn_sz, txn_mem, NULL ) );
 
   /* sign the txn */
-  uchar * signature = signed_vote_txn + txn.signature_off;
-  uchar const * message   = signed_vote_txn + txn.message_off;
-  ulong message_sz  = vote_txn_sz - txn.message_off;
+  uchar * signature = signed_vote_txn + txn->signature_off;
+  uchar const * message   = signed_vote_txn + txn->message_off;
+  ulong message_sz  = vote_txn_sz - txn->message_off;
   fd_keyguard_client_sign( ctx->keyguard_client, signature, message, message_sz, FD_KEYGUARD_SIGN_TYPE_ED25519 );
 
   ulong poh_slot  = vote_slot+1;
```

### src/discof/writer/fd_writer_tile.c
```diff
@@ -280,11 +280,12 @@ during_frag( fd_writer_tile_ctx_t * ctx,
 
     fd_txn_m_t * txnm    = fd_type_pun( fd_chunk_to_laddr( in_ctx->mem, chunk ) );
     uchar *      payload = ((uchar *)txnm) + sizeof(fd_txn_m_t);
-    fd_txn_t txn;
-    if( FD_UNLIKELY( !fd_txn_parse( payload, txnm->payload_sz, &txn, NULL ) ) ) {
+    uchar        txn_mem[ FD_TXN_MAX_SZ ] __attribute__((aligned(alignof(fd_txn_t))));
+    fd_txn_t *   txn = (fd_txn_t *)txn_mem;
+    if( FD_UNLIKELY( !fd_txn_parse( payload, txnm->payload_sz, txn_mem, NULL ) ) ) {
       FD_LOG_CRIT(( "Could not parse txn from send tile" ));
     }
-    uchar * signature = payload + txn.signature_off;
+    uchar * signature = payload + txn->signature_off;
     memcpy( ctx->vote_msg, signature, 64UL );
     return;
   }
```
