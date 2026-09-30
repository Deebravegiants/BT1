# [?] votor: fix bls agg identity exploit and rework API (#10933)

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-08-23
Source: https://github.com/firedancer-io/firedancer/commit/6f5edf6f533682ffd4e5706bc4f5945e8a65cc08
Type: security-commit

## Details
votor: fix bls agg identity exploit and rework API (#10933)

## Patch
### src/choreo/votor/ag_bls.c
```diff
@@ -1,5 +1,3 @@
-/* TODO remove an replace with proper BLS lib */
-
 #include "ag_bls.h"
 
 #include "../../ballet/bls/fd_bls12_381.h"
@@ -15,8 +13,8 @@
 FD_STATIC_ASSERT( AG_BLS_VERIFY_MAX+1UL<=FD_BLS12_381_PAIRING_BATCH_SZ, pairing_batch );
 
 void
-ag_bls_sec_to_pub( ag_bls_pub_t       pk,
-                   ag_bls_sec_t const sk ) {
+ag_bls_sec_to_pub( ag_bls_sec_t const sk,
+                   ag_bls_pub_t       pk ) {
   blst_scalar    scalar[1];
   blst_p1        p[1];
   blst_p1_affine a[1];
@@ -27,22 +25,10 @@ ag_bls_sec_to_pub( ag_bls_pub_t       pk,
 }
 
 void
-ag_bls_sec_to_pub_compressed( uchar              out[ AG_BLS_PUB_COMPRESSED_SZ ],
-                              ag_bls_sec_t const sk ) {
-  blst_scalar    scalar[1];
-  blst_p1        p[1];
-  blst_p1_affine a[1];
-  blst_scalar_from_lendian( scalar, sk );
-  blst_sk_to_pk_in_g1( p, scalar );
-  blst_p1_to_affine( a, p );
-  blst_p1_affine_compress( out, a );
-}
-
-void
-ag_bls_sec_sign_bytes( ag_bls_sig_t       sig,
-                       ag_bls_sec_t const sk,
-                       uchar const *      msg,
-                       ulong              msg_sz ) {
+ag_bls_sec_sign( ag_bls_sec_t const sk,
+                 ag_bls_sig_t       sig,
+                 uchar const *      msg,
+                 ulong              msg_sz ) {
   blst_scalar    scalar[1];
   blst_p2        hash[1];
   blst_p2        s[1];
@@ -65,7 +51,7 @@ ag_bls_sec_derive( ag_bls_sec_t  sk,
 }
 
 static int
-ag_bls_pub_usable( uchar const * pk ) {
+pub_validate( uchar const * pk ) {
   if( FD_UNLIKELY( !fd_bls12_381_g1_validate_syscall( pk, 1 ) ) ) return 0;
 
   blst_p1_affine a[1];
@@ -74,14 +60,14 @@ ag_bls_pub_usable( uchar const * pk ) {
 }
 
 static int
-ag_bls_pub_aggregate( uchar *       out,
-                      uchar const * pks,
-                      ulong         cnt ) {
+pub_aggregate( uchar *       out,
+               uchar const * pks,
+               ulong         cnt ) {
   if( FD_UNLIKELY( !cnt ) ) return -1;
 
   for( ulong i=0UL; i<cnt; i++ ) {
     uchar const * pk = pks + i*AG_BLS_PUB_SZ;
-    if( FD_UNLIKELY( !ag_bls_pub_usable( pk ) ) ) return -1;
+    if( FD_UNLIKELY( !pub_validate( pk ) ) ) return -1;
     if( FD_UNLIKELY( !i ) ) { fd_memcpy( out, pk, AG_BLS_PUB_SZ ); continue; }
     if( FD_UNLIKELY( fd_bls12_381_g1_add_syscall( out, out, pk, 1 ) ) ) return -1;
   }
@@ -103,15 +89,15 @@ ag_bls_pub_try_from_bytes( ag_bls_pub_t  out,
   default:
     return -1;
   }
-  if( FD_UNLIKELY( !ag_bls_pub_usable( affine ) ) ) return -1;
+  if( FD_UNLIKELY( !pub_validate( affine ) ) ) return -1;
   fd_memcpy( out, affine, AG_BLS_PUB_SZ );
   return 0;
 }
 
 static void
-ag_bls_hash_to_g2( uchar *       out,
-                   uchar const * msg,
-                   ulong         msg_sz ) {
+hash_to_g2( uchar *       out,
+            uchar const * msg,
+            ulong         msg_sz ) {
   blst_p2        h[1];
   blst_p2_affine a[1];
   blst_hash_to_g2( h, msg, msg_sz, (uchar const *)AG_BLS_DST, AG_BLS_DST_SZ, NULL, 0UL );
@@ -120,20 +106,20 @@ ag_bls_hash_to_g2( uchar *       out,
 }
 
 static int
-ag_bls_verify_pairs( uchar const * const * pks,
-                     uchar const * const * msgs,
-                     ulong const *         msg_szs,
-                     ulong                 cnt,
-                     uchar const *         sig ) {
+verify_pairs( uchar const * const * pks,
+              uchar const * const * msgs,
+              ulong const *         msg_szs,
+              ulong                 cnt,
+              uchar const *         sig ) {
   if( FD_UNLIKELY( !cnt || cnt>AG_BLS_VERIFY_MAX ) ) return 0;
 
   uchar a[ (AG_BLS_VERIFY_MAX+1UL)*AG_BLS_PUB_SZ ];
   uchar b[ (AG_BLS_VERIFY_MAX+1UL)*AG_BLS_SIG_SZ ];
 
   for( ulong i=0UL; i<cnt; i++ ) {
-    if( FD_UNLIKELY( !ag_bls_pub_usable( pks[ i ] ) ) ) return 0;
+    if( FD_UNLIKELY( !pub_validate( pks[ i ] ) ) ) return 0;
     fd_memcpy        ( a + i*AG_BLS_PUB_SZ, pks [ i ], AG_BLS_PUB_SZ );
-    ag_bls_hash_to_g2( b + i*AG_BLS_SIG_SZ, msgs[ i ], msg_szs[ i ]  );
+    hash_to_g2( b + i*AG_BLS_SIG_SZ, msgs[ i ], msg_szs[ i ]  );
   }
   blst_p1_affine_serialize( a + cnt*AG_BLS_PUB_SZ, &BLS12_381_NEG_G1 );
   fd_memcpy               ( b + cnt*AG_BLS_SIG_SZ, sig, AG_BLS_SIG_SZ );
@@ -147,42 +133,31 @@ ag_bls_verify_pairs( uchar const * const * pks,
 }
 
 int
-ag_bls_sig_verify_bytes( ag_bls_sig_t const self,
-                         ag_bls_pub_t const pk,
-                         uchar const *      msg,
-                         ulong              msg_sz ) {
+ag_bls_sig_verify( ag_bls_sig_t const self,
+                   ag_bls_pub_t const pk,
+                   uchar const *      msg,
+                   ulong              msg_sz ) {
   uchar const * pks    [1] = { pk  };
   uchar const * msgs   [1] = { msg    };
   ulong         msg_szs[1] = { msg_sz };
-  return ag_bls_verify_pairs( pks, msgs, msg_szs, 1UL, self );
+  return verify_pairs( pks, msgs, msg_szs, 1UL, self );
 }
 
 void
-ag_bls_sign_local( void *        ctx,
-                   ag_bls_sig_t  sig,
-                   uchar const * payload,
-                   ulong         payload_sz ) {
-  ag_bls_sec_sign_bytes( sig, (uchar const *)ctx, payload, payload_sz );
-}
-
-void
-ag_bls_agg_init( ag_bls_agg_t * agg,
-                 ulong          nbits ) {
-  FD_TEST( nbits<=AG_BLS_MAX_SIGNERS );
+ag_bls_agg_zero( ag_bls_agg_t * agg ) {
   fd_memset( agg->sig, 0, AG_BLS_SIG_SZ );
-  agg->nbits = nbits;
-  voter_set_null( agg->bitmask );
+  signer_set_null( agg->bitmask );
 }
 
 void
 ag_bls_agg_add( ag_bls_agg_t *     self,
                 ulong              signer_idx,
                 ag_bls_sig_t const sig ) {
-  FD_TEST( signer_idx<self->nbits );
-  FD_TEST( !voter_set_test( self->bitmask, signer_idx ) );
+  FD_TEST( signer_idx<AG_BLS_SIGNERS_MAX );
+  FD_TEST( !signer_set_test( self->bitmask, signer_idx ) );
 
-  int first = ( voter_set_cnt( self->bitmask )==0UL );
-  voter_set_insert( self->bitmask, signer_idx );
+  int first = ( signer_set_cnt( self->bitmask )==0UL );
+  signer_set_insert( self->bitmask, signer_idx );
 
   if( FD_UNLIKELY( first ) ) {
     fd_memcpy( self->sig, sig, AG_BLS_SIG_SZ );
@@ -195,61 +170,50 @@ ag_bls_agg_add( ag_bls_agg_t *     self,
 void
 ag_bls_agg_merge( ag_bls_agg_t * dst,
                   ag_bls_agg_t * src ) {
-  if( FD_UNLIKELY( voter_set_cnt( src->bitmask )==0UL ) ) return;
+  if( FD_UNLIKELY( signer_set_cnt( src->bitmask )==0UL ) ) return;
 
-  if( voter_set_cnt( dst->bitmask )==0UL ) {
+  if( signer_set_cnt( dst->bitmask )==0UL ) {
     fd_memcpy( dst->sig, src->sig, AG_BLS_SIG_SZ );
   } else {
     fd_bls12_381_g2_add_syscall( dst->sig, dst->sig, src->sig, 1 );
   }
   fd_memset( src->sig, 0, AG_BLS_SIG_SZ );
 }
 
-void
-ag_bls_agg_new( ag_bls_agg_t *       agg,
-                ag_bls_sig_t const * sigs,
-                ulong const *        indices,
-                ulong                cnt,
-                ulong                nbits ) {
-  FD_TEST( cnt>0UL );
-  FD_TEST( nbits<=AG_BLS_MAX_SIGNERS );
-  ag_bls_agg_init( agg, nbits );
-  for( ulong i=0UL; i<cnt; i++ ) ag_bls_agg_add( agg, indices[i], sigs[i] );
+int
+ag_bls_agg_is_identity( ag_bls_agg_t const * self ) {
+  blst_p2_affine a[1];
+  if( FD_UNLIKELY( blst_p2_deserialize( a, self->sig )!=BLST_SUCCESS ) ) return 0;
+  return !!blst_p2_affine_is_inf( a );
 }
 
 int
-ag_bls_agg_verify_bytes( ag_bls_agg_t const * self,
-                         uchar const *        msg,
-                         ulong                msg_sz,
-                         uchar const *        pk0,
-                         ulong                pk_stride,
-                         ulong                pk_cnt ) {
-  /* aggsig.rs rejects unless bitmask.len()==pks.len(), but that holds only
-     because its codec writes the UNtrimmed bitmask.  Our wire format is
-     agave's: ag_signer_store trims the bit count to (highest signer rank+1),
-     so nbits is routinely < validator_cnt.  agave's verifier ignores the
-     length entirely (bls-cert-verify collect_pubkeys iterates iter_ones), so
-     we only reject a bitmask wider than the key set. */
-  if( FD_UNLIKELY( self->nbits > pk_cnt ) ) return 0;
-  if( FD_UNLIKELY( !pk0                 ) ) return 0;
-
-  static FD_TL uchar gathered[ AG_BLS_MAX_SIGNERS * AG_BLS_PUB_SZ ];
+ag_bls_agg_verify( ag_bls_agg_t const * self,
+                   uchar const *        msg,
+                   ulong                msg_sz,
+                   uchar const *        pk0,
+                   ulong                pk_stride,
+                   ulong                pk_cnt ) {
+  if( FD_UNLIKELY( fd_ulong_min( AG_BLS_SIGNERS_MAX, signer_set_last( self->bitmask )+1UL )>pk_cnt ) ) return 0;
+  if( FD_UNLIKELY( !pk0                                                                            ) ) return 0;
+
+  static FD_TL uchar gathered[ AG_BLS_SIGNERS_MAX * AG_BLS_PUB_SZ ];
   ulong k = 0UL;
   for( ulong i=0UL; i<pk_cnt; i++ ) {
-    if( FD_LIKELY( voter_set_test( self->bitmask, i ) ) ) {
+    if( FD_LIKELY( signer_set_test( self->bitmask, i ) ) ) {
       fd_memcpy( gathered + k*AG_BLS_PUB_SZ, pk0 + i*pk_stride, AG_BLS_PUB_SZ );
       k++;
     }
   }
   if( FD_UNLIKELY( k==0UL ) ) return 0;
 
   uchar apk[ AG_BLS_PUB_SZ ];
-  if( FD_UNLIKELY( ag_bls_pub_aggregate( apk, gathered, k ) ) ) return 0;
+  if( FD_UNLIKELY( pub_aggregate( apk, gathered, k ) ) ) return 0;
 
   uchar const * pks    [1] = { apk    };
   uchar const * msgs   [1] = { msg    };
   ulong         msg_szs[1] = { msg_sz };
-  return ag_bls_verify_pairs( pks, msgs, msg_szs, 1UL, self->sig );
+  return verify_pairs( pks, msgs, msg_szs, 1UL, self->sig );
 }
 
 int
@@ -262,46 +226,47 @@ ag_bls_agg_verify_without_bitmask( ag_bls_agg_t const * self,
   if( FD_UNLIKELY( ag_bls_agg_signer_cnt( self )!=pk_cnt ) ) return 0;
   if( FD_UNLIKELY( !pk0 || !pk_cnt                          ) ) return 0;
 
-  static FD_TL uchar gathered[ AG_BLS_MAX_SIGNERS * AG_BLS_PUB_SZ ];
-  if( FD_UNLIKELY( pk_cnt>AG_BLS_MAX_SIGNERS ) ) return 0;
+  static FD_TL uchar gathered[ AG_BLS_SIGNERS_MAX * AG_BLS_PUB_SZ ];
+  if( FD_UNLIKELY( pk_cnt>AG_BLS_SIGNERS_MAX ) ) return 0;
   for( ulong i=0UL; i<pk_cnt; i++ ) {
     fd_memcpy( gathered + i*AG_BLS_PUB_SZ, pk0 + i*pk_stride, AG_BLS_PUB_SZ );
   }
 
   uchar apk[ AG_BLS_PUB_SZ ];
-  if( FD_UNLIKELY( ag_bls_pub_aggregate( apk, gathered, pk_cnt ) ) ) return 0;
+  if( FD_UNLIKELY( pub_aggregate( apk, gathered, pk_cnt ) ) ) return 0;
 
   uchar const * pks    [1] = { apk    };
   uchar const * msgs   [1] = { msg    };
   ulong         msg_szs[1] = { msg_sz };
-  return ag_bls_verify_pairs( pks, msgs, msg_szs, 1UL, self->sig );
+  return verify_pairs( pks, msgs, msg_szs, 1UL, self->sig );
 }
 
 int
-ag_bls_agg_verify_mixed_bytes( ag_bls_agg_t const * agg_base,
-                               uchar const *        msg_base,
-                               ulong                msg_base_sz,
-                               ag_bls_agg_t const * agg_fb,
-                               uchar const *        msg_fb,
-                               ulong                msg_fb_sz,
-                               uchar const *        pk0,
-                               ulong                pk_stride,
-                               ulong                pk_cnt ) {
-  if( FD_UNLIKELY( agg_base->nbits>pk_cnt || agg_fb->nbits>pk_cnt ) ) return 0; /* trimmed nbits, see above */
-  if( FD_UNLIKELY( !pk0                                          ) ) return 0;
-
-  static FD_TL uchar gathered[ AG_BLS_MAX_SIGNERS * AG_BLS_PUB_SZ ];
+ag_bls_agg_verify_merged( ag_bls_agg_t const * agg_base,
+                         uchar const *        msg_base,
+                         ulong                msg_base_sz,
+                         ag_bls_agg_t const * agg_fb,
+                         uchar const *        msg_fb,
+                         ulong                msg_fb_sz,
+                         uchar const *        pk0,
+                         ulong                pk_stride,
+                         ulong                pk_cnt ) {
+  if( FD_UNLIKELY( fd_ulong_min( AG_BLS_SIGNERS_MAX, signer_set_last( agg_base->bitmask )+1UL )>pk_cnt ) ) return 0;
+  if( FD_UNLIKELY( fd_ulong_min( AG_BLS_SIGNERS_MAX, signer_set_last( agg_fb->bitmask   )+1UL )>pk_cnt ) ) return 0;
+  if( FD_UNLIKELY( !pk0                                                                                ) ) return 0;
+
+  static FD_TL uchar gathered[ AG_BLS_SIGNERS_MAX * AG_BLS_PUB_SZ ];
   uchar apk[ 2*AG_BLS_PUB_SZ ];
 
-  voter_set_t const * masks[2] = { agg_base->bitmask, agg_fb->bitmask };
+  signer_set_t const * masks[2] = { agg_base->bitmask, agg_fb->bitmask };
   ulong cnt[2] = { 0UL, 0UL };
   for( ulong g=0UL; g<2UL; g++ ) {
     ulong k = 0UL;
     for( ulong i=0UL; i<pk_cnt; i++ ) {
-      if( voter_set_test( masks[g], i ) ) { fd_memcpy( gathered + k*AG_BLS_PUB_SZ, pk0 + i*pk_stride, AG_BLS_PUB_SZ ); k++; }
+      if( signer_set_test( masks[g], i ) ) { fd_memcpy( gathered + k*AG_BLS_PUB_SZ, pk0 + i*pk_stride, AG_BLS_PUB_SZ ); k++; }
     }
     cnt[g] = k;
-    if( k && FD_UNLIKELY( ag_bls_pub_aggregate( apk + g*AG_BLS_PUB_SZ, gathered, k ) ) ) return 0;
+    if( k && FD_UNLIKELY( pub_aggregate( apk + g*AG_BLS_PUB_SZ, gathered, k ) ) ) return 0;
   }
 
   if( FD_UNLIKELY( cnt[0]==0UL && cnt[1]==0UL ) ) return 0;
@@ -313,5 +278,5 @@ ag_bls_agg_verify_mixed_bytes( ag_bls_agg_t const * agg_base,
   if( cnt[0] ) { pks[n] = apk;               msgs[n] = msg_base; msg_szs[n] = msg_base_sz; n++; }
   if( cnt[1] ) { pks[n] = apk+AG_BLS_PUB_SZ; msgs[n] = msg_fb;   msg_szs[n] = msg_fb_sz;   n++; }
 
-  return ag_bls_verify_pairs( pks, msgs, msg_szs, n, agg_base->sig );
+  return verify_pairs( pks, msgs, msg_szs, n, agg_base->sig );
 }
```

### src/choreo/votor/ag_bls.h
```diff
@@ -1,43 +1,33 @@
-/* TODO remove an replace with proper BLS lib */
-
 #ifndef HEADER_fd_src_choreo_votor_ag_bls_h
 #define HEADER_fd_src_choreo_votor_ag_bls_h
 
-#include "ag_votor_base.h"
-
-#define SET_NAME voter_set
-#define SET_MAX  AG_VAT_MAX
-#include "../../util/tmpl/fd_set.c"
+#include "../../util/fd_util.h"
 
 #define AG_BLS_SEC_SZ            (32UL)
 #define AG_BLS_PUB_SZ            (96UL)
 #define AG_BLS_PUB_COMPRESSED_SZ (48UL)
 #define AG_BLS_SIG_SZ            (192UL)
 #define AG_BLS_SIG_COMPRESSED_SZ (96UL)
-#define AG_BLS_MAX_SIGNERS       (2000UL)
+#define AG_BLS_SIGNERS_MAX       (2048UL)
 
-/* A BLS secret key, public key and individual signature.  These are
-   fixed size byte blobs with no value semantics: pass them by decay and
-   copy them with fd_memcpy, never by assignment. */
+#define SET_NAME signer_set
+#define SET_MAX  AG_BLS_SIGNERS_MAX
+#include "../../util/tmpl/fd_set.c"
 
 typedef uchar ag_bls_sec_t[ AG_BLS_SEC_SZ ];
 typedef uchar ag_bls_pub_t[ AG_BLS_PUB_SZ ];
 typedef uchar ag_bls_sig_t[ AG_BLS_SIG_SZ ];
 
-/* An aggregate signature: the aggregated curve point plus the bitmask
-   naming which validator ranks contributed to it. */
-
 struct ag_bls_agg {
   ag_bls_sig_t sig;
-  ulong        nbits;
-  voter_set_t  bitmask[ voter_set_word_cnt ];
+  signer_set_t bitmask[ signer_set_word_cnt ];
 };
 typedef struct ag_bls_agg ag_bls_agg_t;
 
-#define AG_BLS_WORDS_FOR_BITS(nbits) (((nbits)+63UL)/64UL)
-#define AG_BLS_SERIALIZED_SZ(nbits)  (AG_BLS_SIG_SZ + 8UL + 8UL + 8UL*AG_BLS_WORDS_FOR_BITS(nbits))
+#define AG_BLS_WORDS_FOR_BITS(bit_cnt) (((bit_cnt)+63UL)/64UL)
+#define AG_BLS_SERIALIZED_SZ(bit_cnt)  (AG_BLS_SIG_SZ + 8UL + 8UL + 8UL*AG_BLS_WORDS_FOR_BITS(bit_cnt))
 
-#define AG_BLS_SERIALIZED_MAX        (AG_BLS_SERIALIZED_SZ(AG_BLS_MAX_SIGNERS))
+#define AG_BLS_SERIALIZED_MAX        (AG_BLS_SERIALIZED_SZ(AG_BLS_SIGNERS_MAX))
 
 typedef void
 (* ag_bls_sign_fn)( void *        ctx,
@@ -47,82 +37,76 @@ typedef void
 
 FD_PROTOTYPES_BEGIN
 
-void
-ag_bls_sign_local( void *        ctx,
-                   ag_bls_sig_t  sig,
-                   uchar const * payload,
-                   ulong         payload_sz );
+/* SecretKey::to_pk */
 
 void
-ag_bls_sec_to_pub( ag_bls_pub_t       pub,
-                   ag_bls_sec_t const sec );
+ag_bls_sec_to_pub( ag_bls_sec_t const sec,
+                   ag_bls_pub_t       pub );
 
-void
-ag_bls_sec_to_pub_compressed( uchar              out[ AG_BLS_PUB_COMPRESSED_SZ ],
-                              ag_bls_sec_t const sec );
+/* solana_bls_signatures::SecretKey::derive */
 
 void
 ag_bls_sec_derive( ag_bls_sec_t  sec,
                    uchar const * ikm,
                    ulong         ikm_sz );
 
-/* ag_bls_pub_try_from_bytes mirrors PublicKey::try_from_bytes: it
-   validates that `in` is a well formed, prime-order, non-infinity G1
-   point and materialises it uncompressed.  Accepts either the
-   compressed (AG_BLS_PUB_COMPRESSED_SZ) or affine (AG_BLS_PUB_SZ)
-   encoding.  Returns 0 on success, -1 otherwise, in which case out is
-   untouched. */
+/* SecretKey::sign_bytes */
+
+void
+ag_bls_sec_sign( ag_bls_sec_t const sec,
+                 ag_bls_sig_t       sig,
+                 uchar const *      msg,
+                 ulong              msg_sz );
+
+/* PublicKey::try_from_bytes */
 
 int
 ag_bls_pub_try_from_bytes( ag_bls_pub_t  out,
                            uchar const * in,
                            ulong         in_sz );
 
-void
-ag_bls_sec_sign_bytes( ag_bls_sig_t       sig,
-                       ag_bls_sec_t const sec,
-                       uchar const *      msg,
-                       ulong              msg_sz );
+/* IndividualSignature::verify_bytes */
 
 int
-ag_bls_sig_verify_bytes( ag_bls_sig_t const sig,
-                         ag_bls_pub_t const pub,
-                         uchar const *      msg,
-                         ulong              msg_sz );
+ag_bls_sig_verify( ag_bls_sig_t const sig,
+                   ag_bls_pub_t const pub,
+                   uchar const *      msg,
+                   ulong              msg_sz );
 
-void
-ag_bls_agg_new( ag_bls_agg_t *       agg,
-                ag_bls_sig_t const * sigs,
-                ulong const *        indices,
-                ulong                cnt,
-                ulong                nbits );
+/* AggregateSignature::new */
 
 void
-ag_bls_agg_init( ag_bls_agg_t * agg,
-                 ulong          nbits );
+ag_bls_agg_zero( ag_bls_agg_t * agg );
+
+/* AggregateSignature::new */
 
 void
 ag_bls_agg_add( ag_bls_agg_t *     self,
                 ulong              signer_idx,
                 ag_bls_sig_t const sig );
 
+/* agave AggregateAccumulator::add_aggregate */
+
 void
 ag_bls_agg_merge( ag_bls_agg_t * dst,
                   ag_bls_agg_t * src );
 
+/* agave AggregateAccumulator::is_identity */
+
 int
-ag_bls_agg_verify_bytes( ag_bls_agg_t const * self,
-                         uchar const *        msg,
-                         ulong                msg_sz,
-                         uchar const *        pk0,
-                         ulong                pk_stride,
-                         ulong                pk_cnt );
+ag_bls_agg_is_identity( ag_bls_agg_t const * self );
 
-/* ag_bls_agg_verify_without_bitmask mirrors
-   AggregateSignature::verify_without_bitmask: the caller supplies
-   exactly the signers' keys rather than the whole validator set, so the
-   bitmask selects nothing and every supplied key is aggregated.  Fails
-   unless signer_cnt equals pk_cnt. */
+/* AggregateSignature::verify_bytes */
+
+int
+ag_bls_agg_verify( ag_bls_agg_t const * self,
+                   uchar const *        msg,
+                   ulong                msg_sz,
+                   uchar const *        pk0,
+                   ulong                pk_stride,
+                   ulong                pk_cnt );
+
+/* AggregateSignature::verify_without_bitmask */
 
 int
 ag_bls_agg_verify_without_bitmask( ag_bls_agg_t const * self,
@@ -132,51 +116,49 @@ ag_bls_agg_verify_without_bitmask( ag_bls_agg_t const * self,
                                    ulong                pk_stride,
                                    ulong                pk_cnt );
 
+/* agave verify_base3 */
+
 int
-ag_bls_agg_verify_mixed_bytes( ag_bls_agg_t const * agg_base,
-                               uchar const *        msg_base,
-                               ulong                msg_base_sz,
-                               ag_bls_agg_t const * agg_fb,
-                               uchar const *        msg_fb,
-                               ulong                msg_fb_sz,
-                               uchar const *        pk0,
-                               ulong                pk_stride,
-                               ulong                pk_cnt );
+ag_bls_agg_verify_merged( ag_bls_agg_t const * agg_base,
+                         uchar const *        msg_base,
+                         ulong                msg_base_sz,
+                         ag_bls_agg_t const * agg_fb,
+                         uchar const *        msg_fb,
+                         ulong                msg_fb_sz,
+                         uchar const *        pk0,
+                         ulong                pk_stride,
+                         ulong                pk_cnt );
+
+/* AggregateSignature::is_signer */
 
 FD_FN_PURE static inline int
 ag_bls_agg_is_signer( ag_bls_agg_t const * self,
                       ulong                validator_idx ) {
-  if( FD_UNLIKELY( validator_idx>=self->nbits ) ) return 0;
-  return voter_set_test( self->bitmask, validator_idx );
+  if( FD_UNLIKELY( validator_idx>=AG_BLS_SIGNERS_MAX ) ) return 0;
+  return signer_set_test( self->bitmask, validator_idx );
 }
 
+/* AggregateSignature::signers */
+
 FD_FN_PURE static inline ulong
 ag_bls_agg_signer_cnt( ag_bls_agg_t const * self ) {
-  return voter_set_cnt( self->bitmask );
+  return signer_set_cnt( self->bitmask );
 }
 
-/* ag_bls_agg_signers_* mirror AggregateSignature::signers(): they
-   iterate the validator indices whose signature is in the aggregate, so
-   callers need not reach into the bitmask.  Usage:
-
-     for( ulong i=ag_bls_agg_signers_init( agg );
-          !ag_bls_agg_signers_done( i );
-          i=ag_bls_agg_signers_next( agg, i ) ) ... */
-
 FD_FN_PURE static inline ulong
-ag_bls_agg_signers_init( ag_bls_agg_t const * self ) {
-  return voter_set_const_iter_init( self->bitmask );
+ag_bls_agg_signers_iter_init( ag_bls_agg_t const * self ) {
+  return signer_set_const_iter_init( self->bitmask );
 }
 
 FD_FN_CONST static inline int
-ag_bls_agg_signers_done( ulong i ) {
-  return !!voter_set_const_iter_done( i ); /* tmpl returns ulong; narrow to 0/1 */
+ag_bls_agg_signers_iter_done( ulong i ) {
+  return !!signer_set_const_iter_done( i );
 }
 
 FD_FN_PURE static inline ulong
-ag_bls_agg_signers_next( ag_bls_agg_t const * self,
-                         ulong                i ) {
-  return voter_set_const_iter_next( self->bitmask, i );
+ag_bls_agg_signers_iter_next( ag_bls_agg_t const * self,
+                              ulong                i ) {
+  return signer_set_const_iter_next( self->bitmask, i );
 }
 
 FD_PROTOTYPES_END
```

### src/choreo/votor/ag_bls_serde.c
```diff
@@ -7,14 +7,15 @@ ag_bls_ser( ag_bls_agg_t const * agg,
             uchar *              buf,
             ulong                buf_max,
             ulong *              buf_sz ) {
-  ulong word_cnt = AG_BLS_WORDS_FOR_BITS( agg->nbits );
-  ulong sz       = AG_BLS_SERIALIZED_SZ( agg->nbits );
+  ulong bits     = fd_ulong_min( AG_BLS_SIGNERS_MAX, signer_set_last( agg->bitmask )+1UL );
+  ulong word_cnt = AG_BLS_WORDS_FOR_BITS( bits );
+  ulong sz       = AG_BLS_SERIALIZED_SZ( bits );
   if( FD_UNLIKELY( buf_max<sz ) ) return -1;
 
   ag_bls_serde_t * out = (ag_bls_serde_t *)buf;
 
   fd_memcpy( out->signature, agg->sig, AG_BLS_SIG_SZ );
-  out->bit_cnt  = agg->nbits;
+  out->bit_cnt  = bits;
   out->word_cnt = word_cnt;
 
   uchar * p = (uchar *)( out+1 );
@@ -36,27 +37,26 @@ ag_bls_de( ag_bls_agg_t * agg,
   ulong                  bit_cnt  = serde->bit_cnt;
   ulong                  word_cnt = serde->word_cnt;
 
-  if( FD_UNLIKELY( word_cnt>AG_BLS_WORDS_FOR_BITS( AG_BLS_MAX_SIGNERS ) ) ) return 0UL;
-  if( FD_UNLIKELY( bit_cnt >AG_BLS_MAX_SIGNERS                          ) ) return 0UL;
-  if( FD_UNLIKELY( bit_cnt >word_cnt*64UL                               ) ) return 0UL;
-  if( FD_UNLIKELY( buf_max <sizeof(ag_bls_serde_t)+word_cnt*8UL         ) ) return 0UL;
+  if( FD_UNLIKELY( word_cnt>signer_set_word_cnt                 ) ) return 0UL;
+  if( FD_UNLIKELY( bit_cnt >AG_BLS_SIGNERS_MAX                  ) ) return 0UL;
+  if( FD_UNLIKELY( bit_cnt >word_cnt*64UL                       ) ) return 0UL;
+  if( FD_UNLIKELY( buf_max <sizeof(ag_bls_serde_t)+word_cnt*8UL ) ) return 0UL;
 
   fd_memcpy( agg->sig, serde->signature, AG_BLS_SIG_SZ );
-  voter_set_null( agg->bitmask );
-  agg->nbits = bit_cnt;
+  signer_set_null( agg->bitmask );
 
   uchar const * p = (uchar const *)( serde+1 );
   for( ulong w=0UL; w<word_cnt; w++ ) {
-    agg->bitmask[w] = (voter_set_t)FD_LOAD( ulong, p ); p += 8UL;
+    agg->bitmask[w] = (signer_set_t)FD_LOAD( ulong, p ); p += 8UL;
   }
 
   /* aggsig.rs read_bitvec ends with `bitmask.truncate(num_bits)`; drop any
      bit the sender set above the declared count so the set stays valid and
-     signer_cnt/signers() cannot report a rank >= nbits. */
+     signer_cnt/signers() cannot report a rank >= bits. */
   ulong tail = bit_cnt & 63UL;
   ulong last = bit_cnt >> 6;
-  if( tail ) agg->bitmask[ last ] &= (voter_set_t)( (1UL<<tail)-1UL );
-  for( ulong w=(tail ? last+1UL : last); w<word_cnt; w++ ) agg->bitmask[ w ] = (voter_set_t)0UL;
+  if( tail ) agg->bitmask[ last ] &= (signer_set_t)( (1UL<<tail)-1UL );
+  for( ulong w=(tail ? last+1UL : last); w<word_cnt; w++ ) agg->bitmask[ w ] = (signer_set_t)0UL;
 
   return sizeof(ag_bls_serde_t) + word_cnt*8UL;
 }
```

### src/choreo/votor/ag_cert.c
```diff
@@ -36,86 +36,40 @@ check_sig( ag_cert_t const *       self,
   switch( self->kind ) {
   case AG_CERT_TYPE_NOTAR:
     sz = ag_vote_payload_bytes_to_sign( buf, AG_VOTE_TYPE_NOTAR, self->inner.notar.slot, self->inner.notar.block_hash, shred_version );
-    return ag_bls_agg_verify_bytes( &self->inner.notar.agg_sig, buf, sz, pk0, pk_stride, validator_cnt );
+    return ag_bls_agg_verify( &self->inner.notar.agg_sig, buf, sz, pk0, pk_stride, validator_cnt );
   case AG_CERT_TYPE_FAST_FINAL:
     sz = ag_vote_payload_bytes_to_sign( buf, AG_VOTE_TYPE_NOTAR, self->inner.fast_final.slot, self->inner.fast_final.block_hash, shred_version );
-    return ag_bls_agg_verify_bytes( &self->inner.fast_final.agg_sig, buf, sz, pk0, pk_stride, validator_cnt );
+    return ag_bls_agg_verify( &self->inner.fast_final.agg_sig, buf, sz, pk0, pk_stride, validator_cnt );
   case AG_CERT_TYPE_FINAL:
     sz = ag_vote_payload_bytes_to_sign( buf, AG_VOTE_TYPE_FINAL, self->inner.final.slot, NULL, shred_version );
-    return ag_bls_agg_verify_bytes( &self->inner.final.agg_sig, buf, sz, pk0, pk_stride, validator_cnt );
+    return ag_bls_agg_verify( &self->inner.final.agg_sig, buf, sz, pk0, pk_stride, validator_cnt );
   case AG_CERT_TYPE_NOTAR_FALLBACK: {
     ag_notar_fallback_cert_t const * n = &self->inner.notar_fallback;
     uchar buf_fb[ AG_VOTE_PAYLOAD_MAX ]; ulong sz_fb;
     sz    = ag_vote_payload_bytes_to_sign( buf,    AG_VOTE_TYPE_NOTAR,          n->slot, n->block_hash, shred_version );
     sz_fb = ag_vote_payload_bytes_to_sign( buf_fb, AG_VOTE_TYPE_NOTAR_FALLBACK, n->slot, n->block_hash, shred_version );
-    return ag_bls_agg_verify_mixed_bytes( &n->agg_sig_notar,          buf,    sz,
-                                          &n->agg_sig_notar_fallback, buf_fb, sz_fb,
-                                          pk0, pk_stride, validator_cnt );
+    return ag_bls_agg_verify_merged( &n->agg_sig_notar,          buf,    sz,
+                                     &n->agg_sig_notar_fallback, buf_fb, sz_fb,
+                                     pk0, pk_stride, validator_cnt );
   }
   case AG_CERT_TYPE_SKIP: {
     ag_skip_cert_t const * s = &self->inner.skip;
     uchar buf_fb[ AG_VOTE_PAYLOAD_MAX ]; ulong sz_fb;
     sz    = ag_vote_payload_bytes_to_sign( buf,    AG_VOTE_TYPE_SKIP,          s->slot, NULL, shred_version );
     sz_fb = ag_vote_payload_bytes_to_sign( buf_fb, AG_VOTE_TYPE_SKIP_FALLBACK, s->slot, NULL, shred_version );
-    return ag_bls_agg_verify_mixed_bytes( &s->agg_sig_skip,          buf,    sz,
-                                          &s->agg_sig_skip_fallback, buf_fb, sz_fb,
-                                          pk0, pk_stride, validator_cnt );
+    return ag_bls_agg_verify_merged( &s->agg_sig_skip,          buf,    sz,
+                                    &s->agg_sig_skip_fallback, buf_fb, sz_fb,
+                                    pk0, pk_stride, validator_cnt );
   }
   default: __builtin_unreachable();
   }
 }
 
-static void
-aggregate_notar_votes( ag_notar_vote_t const * notar_votes,
-                       ulong                   notar_vote_cnt,
-                       ulong                   validator_cnt,
-                       ag_bls_agg_t *          agg ) {
-  ag_bls_agg_init( agg, validator_cnt );
-  for( ulong i=0UL; i<notar_vote_cnt; i++ ) ag_bls_agg_add( agg, notar_votes[i].signer, notar_votes[i].sig );
-}
-
-static void
-aggregate_notar_fallback_votes( ag_notar_fallback_vote_t const * notar_fallback_votes,
-                                ulong                            notar_fallback_vote_cnt,
-                                ulong                            validator_cnt,
-                                ag_bls_agg_t *                   agg ) {
-  ag_bls_agg_init( agg, validator_cnt );
-  for( ulong i=0UL; i<notar_fallback_vote_cnt; i++ ) ag_bls_agg_add( agg, notar_fallback_votes[i].signer, notar_fallback_votes[i].sig );
-}
-
-static void
-aggregate_skip_votes( ag_skip_vote_t const * skip_votes,
-                      ulong                  skip_vote_cnt,
-                      ulong                  validator_cnt,
-                      ag_bls_agg_t *         agg ) {
-  ag_bls_agg_init( agg, validator_cnt );
-  for( ulong i=0UL; i<skip_vote_cnt; i++ ) ag_bls_agg_add( agg, skip_votes[i].signer, skip_votes[i].sig );
-}
-
-static void
-aggregate_skip_fallback_votes( ag_skip_fallback_vote_t const * skip_fallback_votes,
-                               ulong                           skip_fallback_vote_cnt,
-                               ulong                           validator_cnt,
-                               ag_bls_agg_t *                  agg ) {
-  ag_bls_agg_init( agg, validator_cnt );
-  for( ulong i=0UL; i<skip_fallback_vote_cnt; i++ ) ag_bls_agg_add( agg, skip_fallback_votes[i].signer, skip_fallback_votes[i].sig );
-}
-
-static void
-aggregate_final_votes( ag_final_vote_t const * final_votes,
-                       ulong                   final_vote_cnt,
-                       ulong                   validator_cnt,
-                       ag_bls_agg_t *          agg ) {
-  ag_bls_agg_init( agg, validator_cnt );
-  for( ulong i=0UL; i<final_vote_cnt; i++ ) ag_bls_agg_add( agg, final_votes[i].signer, final_votes[i].sig );
-}
-
 ag_notar_cert_t
 ag_notar_cert_construct( ag_notar_vote_t const * notar_votes,
                          ulong                   notar_vote_cnt,
                          ag_epoch_info_t const * epoch_info ) {
-  ag_validator_info_t const * validators    = ag_epoch_info_validators( epoch_info );
-  ulong                       validator_cnt = epoch_info->validator_cnt;
+  ag_validator_info_t const * validators = ag_epoch_info_validators( epoch_info );
   FD_TEST( notar_vote_cnt>0UL );
   ulong           slot  = notar_votes[0].slot;
   ulong           stake = 0UL;
@@ -129,16 +83,16 @@ ag_notar_cert_construct( ag_notar_vote_t const * notar_votes,
   ag_notar_cert_t cert;
   cert.slot = slot; cert.stake = stake;
   memcpy( cert.block_hash, block_hash, sizeof(ag_block_hash_t) );
-  aggregate_notar_votes( notar_votes, notar_vote_cnt, validator_cnt, &cert.agg_sig );
+  ag_bls_agg_zero( &cert.agg_sig );
+  for( ulong i=0UL; i<notar_vote_cnt; i++ ) ag_bls_agg_add( &cert.agg_sig, notar_votes[i].signer, notar_votes[i].sig );
   return cert;
 }
 
 ag_fast_final_cert_t
 ag_fast_final_cert_construct( ag_notar_vote_t const * notar_votes,
                               ulong                   notar_vote_cnt,
                               ag_epoch_info_t const * epoch_info ) {
-  ag_validator_info_t const * validators    = ag_epoch_info_validators( epoch_info );
-  ulong                       validator_cnt = epoch_info->validator_cnt;
+  ag_validator_info_t const * validators = ag_epoch_info_validators( epoch_info );
   FD_TEST( notar_vote_cnt>0UL );
   ulong           slot  = notar_votes[0].slot;
   ulong           stake = 0UL;
@@ -152,16 +106,16 @@ ag_fast_final_cert_construct( ag_notar_vote_t const * notar_votes,
   ag_fast_final_cert_t cert;
   cert.slot = slot; cert.stake = stake;
   memcpy( cert.block_hash, block_hash, sizeof(ag_block_hash_t) );
-  aggregate_notar_votes( notar_votes, notar_vote_cnt, validator_cnt, &cert.agg_sig );
+  ag_bls_agg_zero( &cert.agg_sig );
+  for( ulong i=0UL; i<notar_vote_cnt; i++ ) ag_bls_agg_add( &cert.agg_sig, notar_votes[i].signer, notar_votes[i].sig );
   return cert;
 }
 
 ag_final_cert_t
 ag_final_cert_construct( ag_final_vote_t const * final_votes,
                          ulong                   final_vote_cnt,
                          ag_epoch_info_t const * epoch_info ) {
-  ag_validator_info_t const * validators    = ag_epoch_info_validators( epoch_info );
-  ulong                       validator_cnt = epoch_info->validator_cnt;
+  ag_validator_info_t const * validators = ag_epoch_info_validators( epoch_info );
   FD_TEST( final_vote_cnt>0UL );
   ulong slot  = final_votes[0].slot;
   ulong stake = 0UL;
@@ -171,7 +125,8 @@ ag_final_cert_construct( ag_final_vote_t const * final_votes,
   }
   ag_final_cert_t cert;
   cert.slot = slot; cert.stake = stake;
-  aggregate_final_votes( final_votes, final_vote_cnt, validator_cnt, &cert.agg_sig );
+  ag_bls_agg_zero( &cert.agg_sig );
+  for( ulong i=0UL; i<final_vote_cnt; i++ ) ag_bls_agg_add( &cert.agg_sig, final_votes[i].signer, final_votes[i].sig );
   return cert;
 }
 
@@ -181,8 +136,7 @@ ag_notar_fallback_cert_construct( ag_notar_vote_t const *          notar_votes,
                                   ag_notar_fallback_vote_t const * notar_fallback_votes,
                                   ulong                            notar_fallback_vote_cnt,
                                   ag_epoch_info_t const *          epoch_info ) {
-  ag_validator_info_t const * validators    = ag_epoch_info_validators( epoch_info );
-  ulong                       validator_cnt = epoch_info->validator_cnt;
+  ag_validator_info_t const * validators = ag_epoch_info_validators( epoch_info );
   FD_TEST( notar_vote_cnt>0UL || notar_fallback_vote_cnt>0UL );
   ulong           slot;
   ag_block_hash_t block_hash;
@@ -195,18 +149,30 @@ ag_notar_fallback_cert_construct( ag_notar_vote_t const *          notar_votes,
     FD_TEST( !memcmp( notar_votes[i].block_hash, block_hash, sizeof(ag_block_hash_t) ) );
     stake += validators[ notar_votes[i].signer ].stake;
   }
+  ulong stake_fb = 0UL;
   for( ulong i=0UL; i<notar_fallback_vote_cnt; i++ ) {
     FD_TEST( notar_fallback_votes[i].slot==slot );
     FD_TEST( !memcmp( notar_fallback_votes[i].block_hash, block_hash, sizeof(ag_block_hash_t) ) );
-    stake += validators[ notar_fallback_votes[i].signer ].stake;
+    stake_fb += validators[ notar_fallback_votes[i].signer ].stake;
   }
 
   ag_notar_fallback_cert_t cert;
-  cert.slot = slot; cert.stake = stake;
+  cert.slot = slot;
   memcpy( cert.block_hash, block_hash, sizeof(ag_block_hash_t) );
-  aggregate_notar_votes         ( notar_votes,          notar_vote_cnt,          validator_cnt, &cert.agg_sig_notar          );
-  aggregate_notar_fallback_votes( notar_fallback_votes, notar_fallback_vote_cnt, validator_cnt, &cert.agg_sig_notar_fallback );
+  ag_bls_agg_zero( &cert.agg_sig_notar );
+  for( ulong i=0UL; i<notar_vote_cnt; i++ ) ag_bls_agg_add( &cert.agg_sig_notar, notar_votes[i].signer, notar_votes[i].sig );
+  if( FD_UNLIKELY( ag_bls_agg_is_identity( &cert.agg_sig_notar ) ) ) {
+    ag_bls_agg_zero( &cert.agg_sig_notar );
+    stake = 0UL;
+  }
+  ag_bls_agg_zero( &cert.agg_sig_notar_fallback );
+  for( ulong i=0UL; i<notar_fallback_vote_cnt; i++ ) ag_bls_agg_add( &cert.agg_sig_notar_fallback, notar_fallback_votes[i].signer, notar_fallback_votes[i].sig );
+  if( FD_UNLIKELY( ag_bls_agg_is_identity( &cert.agg_sig_notar_fallback ) ) ) {
+    ag_bls_agg_zero( &cert.agg_sig_notar_fallback );
+    stake_fb = 0UL;
+  }
   ag_bls_agg_merge( &cert.agg_sig_notar, &cert.agg_sig_notar_fallback );
+  cert.stake = stake + stake_fb;
   return cert;
 }
 
@@ -216,8 +182,7 @@ ag_skip_cert_construct( ag_skip_vote_t const *          skip_votes,
                         ag_skip_fallback_vote_t const * skip_fallback_votes,
                         ulong                           skip_fallback_vote_cnt,
                         ag_epoch_info_t const *         epoch_info ) {
-  ag_validator_info_t const * validators    = ag_epoch_info_validators( epoch_info );
-  ulong                       validator_cnt = epoch_info->validator_cnt;
+  ag_validator_info_t const * validators = ag_epoch_info_validators( epoch_info );
   FD_TEST( skip_vote_cnt>0UL || skip_fallback_vote_cnt>0UL );
   ulong slot = skip_vote_cnt>0UL ? skip_votes[0].slot : skip_fallback_votes[0].slot;
 
@@ -226,15 +191,27 @@ ag_skip_cert_construct( ag_skip_vote_t const *          skip_votes,
     FD_TEST( skip_votes[i].slot==slot );
     stake += validators[ skip_votes[i].signer ].stake;
   }
+  ulong stake_fb = 0UL;
   for( ulong i=0UL; i<skip_fallback_vote_cnt; i++ ) {
     FD_TEST( skip_fallback_votes[i].slot==slot );
-    stake += validators[ skip_fallback_votes[i].signer ].stake;
+    stake_fb += validators[ skip_fallback_votes[i].signer ].stake;
   }
 
   ag_skip_cert_t cert;
-  cert.slot = slot; cert.stake = stake;
-  aggregate_skip_votes         ( skip_votes,          skip_vote_cnt,          validator_cnt, &cert.agg_sig_skip          );
-  aggregate_skip_fallback_votes( skip_fallback_votes, skip_fallback_vote_cnt, validator_cnt, &cert.agg_sig_skip_fallback );
+  cert.slot = slot;
+  ag_bls_agg_zero( &cert.agg_sig_skip );
+  for( ulong i=0UL; i<skip_vote_cnt; i++ ) ag_bls_agg_add( &cert.agg_sig_skip, skip_votes[i].signer, skip_votes[i].sig );
+  if( FD_UNLIKELY( ag_bls_agg_is_identity( &cert.agg_sig_skip ) ) ) {
+    ag_bls_agg_zero( &cert.agg_sig_skip );
+    stake = 0UL;
+  }
+  ag_bls_agg_zero( &cert.agg_sig_skip_fallback );
+  for( ulong i=0UL; i<skip_fallback_vote_cnt; i++ ) ag_bls_agg_add( &cert.agg_sig_skip_fallback, skip_fallback_votes[i].signer, skip_fallback_votes[i].sig );
+  if( FD_UNLIKELY( ag_bls_agg_is_identity( &cert.agg_sig_skip_fallback ) ) ) {
+    ag_bls_agg_zero( &cert.agg_sig_skip_fallback );
+    stake_fb = 0UL;
+  }
+  cert.stake = stake + stake_fb;
   ag_bls_agg_merge( &cert.agg_sig_skip, &cert.agg_sig_skip_fallback );
   return cert;
 }
```

### src/choreo/votor/ag_cert_serde.c
```diff
@@ -11,20 +11,29 @@ FD_STATIC_ASSERT( sizeof(ag_cert_block_final_serde_t    )==8UL+sizeof(ag_block_h
 #define BASE2_BITMAP (0)
 #define BASE3_BITMAP (1)
 
+/* One past the highest signer, or zero when nobody signed.  Agave trims
+   the rank bitvec to exactly this width when it builds a certificate, and
+   to the wider of the two partitions for base3. */
+
+static ulong
+bit_cnt( ag_bls_agg_t const * agg ) {
+  return fd_ulong_min( AG_BLS_SIGNERS_MAX, signer_set_last( agg->bitmask )+1UL );
+}
+
 static ulong
 base2_bitmap_ser( uchar *              out,
                   ag_bls_agg_t const * agg ) {
   ag_cert_bitmap_serde_t * bm      = (ag_cert_bitmap_serde_t *)out;
-  ulong                    nbits   = agg->nbits;
-  ulong                    payload = (nbits+7UL)/8UL;
+  ulong                    bits    = bit_cnt( agg );
+  ulong                    payload = (bits+7UL)/8UL;
 
   bm->version = (uchar)BASE2_BITMAP;
-  bm->bit_cnt = (ushort)nbits;
+  bm->bit_cnt = (ushort)bits;
 
   uchar * p = (uchar *)( bm+1 );
   fd_memset( p, 0, payload );
-  for( ulong i=0UL; i<nbits; i++ ) {
-    if( voter_set_test( agg->bitmask, i ) ) p[ i>>3 ] |= (uchar)( 1U << (i&7U) );
+  for( ulong i=0UL; i<bits; i++ ) {
+    if( signer_set_test( agg->bitmask, i ) ) p[ i>>3 ] |= (uchar)( 1U << (i&7U) );
   }
   return sizeof(ag_cert_bitmap_serde_t) + payload;
 }
@@ -34,21 +43,21 @@ base3_bitmap_ser( uchar *              out,
                   ag_bls_agg_t const * base,
                   ag_bls_agg_t const * fb ) {
   ag_cert_bitmap_serde_t * bm      = (ag_cert_bitmap_serde_t *)out;
-  ulong                    nbits   = base->nbits;
-  ulong                    nchunks = (nbits+4UL)/5UL;
+  ulong                    bits    = fd_ulong_max( bit_cnt( base ), bit_cnt( fb ) );
+  ulong                    nchunks = (bits+4UL)/5UL;
 
   bm->version = (uchar)BASE3_BITMAP;
-  bm->bit_cnt = (ushort)nbits;
+  bm->bit_cnt = (ushort)bits;
 
   uchar * p = (uchar *)( bm+1 );
   for( ulong chunk=0UL; chunk<nchunks; chunk++ ) {
     ulong start = chunk*5UL;
-    ulong end   = fd_ulong_min( start+5UL, nbits );
+    ulong end   = fd_ulong_min( start+5UL, bits );
     uint  block = 0U;
     uint  place = 1U;
     for( ulong i=start; i<end; i++ ) {
-      uint digit = voter_set_test( base->bitmask, i ) ? 1U
-                 : voter_set_test( fb->bitmask,   i ) ? 2U : 0U;
+      uint digit = signer_set_test( base->bitmask, i ) ? 1U
+                 : signer_set_test( fb->bitmask,   i ) ? 2U : 0U;
       block += digit*place;
       place *= 3U;
     }
@@ -70,17 +79,17 @@ base2_bitmap_de( ag_bls_agg_t * agg,
   if( FD_UNLIKELY( b_sz<sizeof(ag_cert_bitmap_serde_t) ) ) return AG_CERT_DE_ERR_TRUNCATED;
 
   ag_cert_bitmap_serde_t const * bm      = (ag_cert_bitmap_serde_t const *)b;
-  ulong                          nbits   = (ulong)bm->bit_cnt;
+  ulong                          bits    = (ulong)bm->bit_cnt;
   ulong                          payload = b_sz - sizeof(ag_cert_bitmap_serde_t);
-  if( FD_UNLIKELY( bm->version!=BASE2_BITMAP     ) ) return AG_CERT_DE_ERR_MALFORMED;
-  if( FD_UNLIKELY( nbits>AG_BLS_MAX_SIGNERS   ) ) return AG_CERT_DE_ERR_MALFORMED;
-  if( FD_UNLIKELY( payload!=(nbits+7UL)/8UL      ) ) return AG_CERT_DE_ERR_MALFORMED;
+  if( FD_UNLIKELY( bm->version!=BASE2_BITMAP ) ) return AG_CERT_DE_ERR_MALFORMED;
+  if( FD_UNLIKELY( bits>AG_BLS_SIGNERS_MAX   ) ) return AG_CERT_DE_ERR_MALFORMED;
+  if( FD_UNLIKELY( payload!=(bits+7UL)/8UL   ) ) return AG_CERT_DE_ERR_MALFORMED;
 
-  ag_bls_agg_init( agg, nbits );
+  ag_bls_agg_zero( agg );
 
   uchar const * p = (uchar const *)( bm+1 );
-  for( ulong i=0UL; i<nbits; i++ ) {
-    if( (p[ i>>3 ] >> (i&7U)) & 1U ) voter_set_insert( agg->bitmask, i );
+  for( ulong i=0UL; i<bits; i++ ) {
+    if( (p[ i>>3 ] >> (i&7U)) & 1U ) signer_set_insert( agg->bitmask, i );
   }
   return AG_CERT_DE_SUCCESS;
 }
@@ -93,25 +102,25 @@ base3_bitmap_de( ag_bls_agg_t * base,
   if( FD_UNLIKELY( b_sz<sizeof(ag_cert_bitmap_serde_t) ) ) return AG_CERT_DE_ERR_TRUNCATED;
 
   ag_cert_bitmap_serde_t const * bm      = (ag_cert_bitmap_serde_t const *)b;
-  ulong                          nbits   = (ulong)bm->bit_cnt;
+  ulong                          bits    = (ulong)bm->bit_cnt;
   ulong                          payload = b_sz - sizeof(ag_cert_bitmap_serde_t);
-  ulong                          nchunks = (nbits+4UL)/5UL;
-  if( FD_UNLIKELY( bm->version!=BASE3_BITMAP   ) ) return AG_CERT_DE_ERR_MALFORMED;
-  if( FD_UNLIKELY( nbits>AG_BLS_MAX_SIGNERS ) ) return AG_CERT_DE_ERR_MALFORMED;
-  if( FD_UNLIKELY( payload!=nchunks            ) ) return AG_CERT_DE_ERR_MALFORMED;
+  ulong                          nchunks = (bits+4UL)/5UL;
+  if( FD_UNLIKELY( bm->version!=BASE3_BITMAP ) ) return AG_CERT_DE_ERR_MALFORMED;
+  if( FD_UNLIKELY( bits>AG_BLS_SIGNERS_MAX   ) ) return AG_CERT_DE_ERR_MALFORMED;
+  if( FD_UNLIKELY( payload!=nchunks          ) ) return AG_CERT_DE_ERR_MALFORMED;
 
-  ag_bls_agg_init( base, nbits );
-  ag_bls_agg_init( fb,   nbits );
+  ag_bls_agg_zero( base );
+  ag_bls_agg_zero( fb   );
 
   uchar const * p = (uchar const *)( bm+1 );
   for( ulong chunk=0UL; chunk<nchunks; chunk++ ) {
     uint  block = (uint)p[ chunk ];
     ulong start = chunk*5UL;
-    ulong end   = fd_ulong_min( start+5UL, nbits );
+    ulong end   = fd_ulong_min( start+5UL, bits );
     for( ulong i=start; i<end; i++ ) {
       uint digit = block % 3U; block /= 3U;
-      if(      digit==1U ) voter_set_insert( base->bitmask, i );
-      else if( digit==2U ) voter_set_insert( fb->bitmask,   i );
+      if(      digit==1U ) signer_set_insert( base->bitmask, i );
+      else if( digit==2U ) signer_set_insert( fb->bitmask,   i );
     }
   }
   return AG_CERT_DE_SUCCESS;
@@ -174,7 +183,8 @@ ag_cert_ser( ag_cert_t const * self,
 
   if( fb && !ag_bls_agg_signer_cnt( fb ) ) fb = NULL;
 
-  ulong bm_sz   = sizeof(ag_cert_bitmap_serde_t) + ( fb ? (base->nbits+4UL)/5UL : (base->nbits+7UL)/8UL );
+  ulong bits    = fb ? fd_ulong_max( bit_cnt( base ), bit_cnt( fb ) ) : bit_cnt( base );
+  ulong bm_sz   = sizeof(ag_cert_bitmap_serde_t) + ( fb ? (bits+4UL)/5UL : (bits+7UL)/8UL );
   ulong head_sz = sizeof(ag_cert_serde_t) - ( hash ? 0UL : sizeof(ag_block_hash_t) );
   ulong sz      = head_sz + bm_sz + sizeof(ushort);
   if( FD_UNLIKELY( buf_max<sz ) ) return -1;
@@ -266,7 +276,7 @@ ag_cert_de( ag_cert_t *   cert,
     cert->inner.notar_fallback.slot = slot;
     memcpy( cert->inner.notar_fallback.block_hash, cert_->block_cert.block_id, sizeof(ag_block_hash_t) );
     if( FD_UNLIKELY( bm_cnt<1UL ) ) return AG_CERT_DE_ERR_TRUNCATED;
-    if( bm[0]==BASE2_BITMAP ) { if( FD_UNLIKELY( err = base2_bitmap_de( b,    bm, bm_cnt ) ) ) return err; ag_bls_agg_init( f, b->nbits ); }
+    if( bm[0]==BASE2_BITMAP ) { if( FD_UNLIKELY( err = base2_bitmap_de( b,    bm, bm_cnt ) ) ) return err; ag_bls_agg_zero( f ); }
     else                      { if( FD_UNLIKELY( err = base3_bitmap_de( b, f, bm, bm_cnt ) ) ) return err; }
     fd_memcpy( b->sig, sig, AG_BLS_SIG_SZ );
     break;
@@ -276,7 +286,7 @@ ag_cert_de( ag_cert_t *   cert,
     ag_bls_agg_t * f = &cert->inner.skip.agg_sig_skip_fallback;
     cert->inner.skip.slot = slot;
     if( FD_UNLIKELY( bm_cnt<1UL ) ) return AG_CERT_DE_ERR_TRUNCATED;
-    if( bm[0]==BASE2_BITMAP ) { if( FD_UNLIKELY( err = base2_bitmap_de( b,    bm, bm_cnt ) ) ) return err; ag_bls_agg_init( f, b->nbits ); }
+    if( bm[0]==BASE2_BITMAP ) { if( FD_UNLIKELY( err = base2_bitmap_de( b,    bm, bm_cnt ) ) ) return err; ag_bls_agg_zero( f ); }
     else                      { if( FD_UNLIKELY( err = base3_bitmap_de( b, f, bm, bm_cnt ) ) ) return err; }
     fd_memcpy( b->sig, sig, AG_BLS_SIG_SZ );
     break;
```

### src/choreo/votor/ag_slot_state.c
```diff
@@ -277,7 +277,7 @@ count_notar_stake( ag_slot_state_t *     slot_state,
       ulong nf_cnt = gather_nf_votes   ( slot_state, block_hash );
       ag_cert_t cert; cert.kind = AG_CERT_TYPE_NOTAR_FALLBACK;
       cert.inner.notar_fallback = ag_notar_fallback_cert_construct( gather_notar, n_cnt, gather_nf, nf_cnt, epoch_info );
-      out_push_cert( &outputs, &cert );
+      if( FD_LIKELY( ag_epoch_info_is_quorum( epoch_info, cert.inner.notar_fallback.stake ) ) ) out_push_cert( &outputs, &cert );
     } else {
       log_own_agg_complete( slot_state, AG_CERT_TYPE_NOTAR_FALLBACK, nf_stake + notar_stake );
     }
@@ -323,7 +323,7 @@ count_notar_fallback_stake( ag_slot_state_t *     slot_state,
       ulong nf_cnt = gather_nf_votes   ( slot_state, block_hash );
       ag_cert_t cert; cert.kind = AG_CERT_TYPE_NOTAR_FALLBACK;
       cert.inner.notar_fallback = ag_notar_fallback_cert_construct( gather_notar, n_cnt, gather_nf, nf_cnt, epoch_info );
-      out_push_cert( &outputs, &cert );
+      if( FD_LIKELY( ag_epoch_info_is_quorum( epoch_info, cert.inner.notar_fallback.stake ) ) ) out_push_cert( &outputs, &cert );
     } else {
       log_own_agg_complete( slot_state, AG_CERT_TYPE_NOTAR_FALLBACK, nf_stake + notar_stake );
     }
@@ -370,7 +370,7 @@ count_skip_stake( ag_slot_state_t * slot_state,
       }
       ag_cert_t cert; cert.kind = AG_CERT_TYPE_SKIP;
       cert.inner.skip = ag_skip_cert_construct( gather_skip, skip_cnt, gather_sf, sf_cnt, epoch_info );
-      out_push_cert( &outputs, &cert );
+      if( FD_LIKELY( ag_epoch_info_is_quorum( epoch_info, cert.inner.skip.stake ) ) ) out_push_cert( &outputs, &cert );
     } else {
       log_own_agg_complete( slot_state, AG_CERT_TYPE_SKIP, total_skip_stake );
     }
```

### src/choreo/votor/ag_vote.c
```diff
@@ -26,7 +26,7 @@ sign_payload( ag_bls_sig_t          sig,
               ushort                shred_version ) {
   uchar buf[ AG_VOTE_PAYLOAD_MAX ];
   ulong sz = ag_vote_payload_bytes_to_sign( buf, kind, slot, h, shred_version );
-  ag_bls_sec_sign_bytes( sig, sk, buf, sz );
+  ag_bls_sec_sign( sk, sig, buf, sz );
 }
 
 static int
@@ -38,7 +38,7 @@ verify_payload( ag_bls_sig_t const    sig,
                 ushort                shred_version ) {
   uchar buf[ AG_VOTE_PAYLOAD_MAX ];
   ulong sz = ag_vote_payload_bytes_to_sign( buf, kind, slot, h, shred_version );
-  return ag_bls_sig_verify_bytes( sig, pk, buf, sz );
+  return ag_bls_sig_verify( sig, pk, buf, sz );
 }
 
 void
```

### src/choreo/votor/test_ag_bls.c
```diff
@@ -1,5 +1,18 @@
 #include "ag_bls_serde.h"
 
+#include "../../third_party/blst/bindings/blst.h"
+
+/* Compressed public keys are only needed to exercise the compressed arm
+   of ag_bls_pub_try_from_bytes; ag_bls has no compressor of its own. */
+
+static void
+pub_compress( uchar              out[ AG_BLS_PUB_COMPRESSED_SZ ],
+              ag_bls_pub_t const pub ) {
+  blst_p1_affine a[1];
+  FD_TEST( blst_p1_deserialize( a, pub )==BLST_SUCCESS );
+  blst_p1_affine_compress( out, a );
+}
+
 /* ag_bls_pub_t / ag_bls_sig_t are array typedefs, so they have no value
    semantics -- gather them explicitly rather than by brace initialiser. */
 
@@ -31,16 +44,17 @@ test_signers( void ) {
   ag_bls_sig_t sig[3];
   for( ulong i=0UL; i<3UL; i++ ) {
     fd_memset( sk[i], (int)(i+1UL), AG_BLS_SEC_SZ );
-    ag_bls_sec_to_pub( pk[i], sk[i] );
-    ag_bls_sec_sign_bytes( sig[i], sk[i], msg, msg_sz );
-    FD_TEST( ag_bls_sig_verify_bytes( sig[i], pk[i], msg, msg_sz ) );
+    ag_bls_sec_to_pub( sk[i], pk[i] );
+    ag_bls_sec_sign( sk[i], sig[i], msg, msg_sz );
+    FD_TEST( ag_bls_sig_verify( sig[i], pk[i], msg, msg_sz ) );
   }
 
   ag_bls_sig_t sigs[2];
   { ulong _sel[2] = { 0UL, 2UL }; pick_sig( sigs, sig, _sel, 2UL ); }
   ulong        idx [2] = { 0UL, 2UL };
   ag_bls_agg_t agg[1];
-  ag_bls_agg_new( agg, (ag_bls_sig_t const *)sigs, idx, 2UL, 3UL );
+  ag_bls_agg_zero( agg );
+  for( ulong i=0UL; i<2UL; i++ ) ag_bls_agg_add( agg, idx[i], sigs[i] );
 
   FD_TEST( ag_bls_agg_signer_cnt( agg )==2UL );
   FD_TEST(  ag_bls_agg_is_signer( agg, 0UL ) );
@@ -49,28 +63,28 @@ test_signers( void ) {
   FD_TEST( !ag_bls_agg_is_signer( agg, 3UL ) );
 
   ulong seen = 0UL, cnt = 0UL;
-  for( ulong i=voter_set_const_iter_init( agg->bitmask );
-       !voter_set_const_iter_done( i );
-       i=voter_set_const_iter_next( agg->bitmask, i ) ) {
+  for( ulong i=signer_set_const_iter_init( agg->bitmask );
+       !signer_set_const_iter_done( i );
+       i=signer_set_const_iter_next( agg->bitmask, i ) ) {
     seen |= (1UL<<i); cnt++;
   }
   FD_TEST( cnt==2UL );
   FD_TEST( seen==((1UL<<0)|(1UL<<2)) );
 
   ag_bls_pub_t pks[3];
   { ulong _sel[3] = { 0UL, 1UL, 2UL }; pick_pub( pks, pk, _sel, 3UL ); }
-  FD_TEST(  ag_bls_agg_verify_bytes( agg, msg, msg_sz, pks[0], sizeof(ag_bls_pub_t), 3UL ) );
-  FD_TEST( !ag_bls_agg_verify_bytes( agg, msg, msg_sz, pks[0], sizeof(ag_bls_pub_t), 2UL ) );
+  FD_TEST(  ag_bls_agg_verify( agg, msg, msg_sz, pks[0], sizeof(ag_bls_pub_t), 3UL ) );
+  FD_TEST( !ag_bls_agg_verify( agg, msg, msg_sz, pks[0], sizeof(ag_bls_pub_t), 2UL ) );
 }
 
 FD_FN_UNUSED static void
 test_incremental( void ) {
   uchar const * msg = (uchar const *)"incremental";
   ag_bls_sec_t  sk; fd_memset( sk, 7, AG_BLS_SEC_SZ );
-  ag_bls_sig_t  s; ag_bls_sec_sign_bytes( s, sk, msg, 11UL );
+  ag_bls_sig_t  s; ag_bls_sec_sign( sk, s, msg, 11UL );
 
   ag_bls_agg_t agg[1];
-  ag_bls_agg_init( agg, 8UL );
+  ag_bls_agg_zero( agg );
   FD_TEST( ag_bls_agg_signer_cnt( agg )==0UL );
   ag_bls_agg_add( agg, 5UL, s );
   ag_bls_agg_add( agg, 1UL, s );
@@ -81,26 +95,25 @@ test_incremental( void ) {
 
 FD_FN_UNUSED static void
 test_serde( void ) {
-  ulong        nbits = 200UL;
+  ulong        bits  = 200UL;
   ag_bls_sec_t sk; fd_memset( sk, 3, AG_BLS_SEC_SZ );
-  ag_bls_sig_t s; ag_bls_sec_sign_bytes( s, sk, (uchar const *)"x", 1UL );
+  ag_bls_sig_t s; ag_bls_sec_sign( sk, s, (uchar const *)"x", 1UL );
 
   ag_bls_agg_t agg[1];
-  ag_bls_agg_init( agg, nbits );
+  ag_bls_agg_zero( agg );
   ulong want[5] = { 0UL, 63UL, 64UL, 130UL, 199UL };
   for( ulong i=0UL; i<5UL; i++ ) ag_bls_agg_add( agg, want[i], s );
 
   uchar buf[ AG_BLS_SERIALIZED_MAX ];
   ulong sz;
   FD_TEST( ag_bls_ser( agg, buf, sizeof(buf), &sz )==0 );
-  FD_TEST( sz==AG_BLS_SERIALIZED_SZ( nbits ) );
+  FD_TEST( sz==AG_BLS_SERIALIZED_SZ( bits ) );
 
   ag_bls_agg_t back[1];
   ulong        consumed = ag_bls_de( back, buf, sz );
   FD_TEST( consumed==sz );
-  FD_TEST( back->nbits==nbits );
   FD_TEST( !memcmp( back->sig, agg->sig, AG_BLS_SIG_SZ ) );
-  for( ulong i=0UL; i<nbits; i++ ) FD_TEST( ag_bls_agg_is_signer( back, i )==ag_bls_agg_is_signer( agg, i ) );
+  for( ulong i=0UL; i<bits; i++ ) FD_TEST( ag_bls_agg_is_signer( back, i )==ag_bls_agg_is_signer( agg, i ) );
   FD_TEST( ag_bls_agg_signer_cnt( back )==5UL );
 
   FD_TEST( ag_bls_de( back, buf, sz-1UL )==0UL );
@@ -125,12 +138,12 @@ test_roundtrip( void ) {
   for( ulong i=0UL; i<N; i++ ) {
     fd_memset( sk[i], 0, AG_BLS_SEC_SZ );
     sk[i][0] = (uchar)( i+1UL );
-    ag_bls_sec_to_pub( pk[i], sk[i] );
-    ag_bls_sec_sign_bytes ( sig[i], sk[i], msg, msg_sz );
+    ag_bls_sec_to_pub( sk[i], pk[i] );
+    ag_bls_sec_sign ( sk[i], sig[i], msg, msg_sz );
 
-    FD_TEST(  ag_bls_sig_verify_bytes( sig[i], pk[i],          msg,  msg_sz ) );
-    FD_TEST( !ag_bls_sig_verify_bytes( sig[i], pk[(i+1UL)%N],  msg,  msg_sz ) );
-    FD_TEST( !ag_bls_sig_verify_bytes( sig[i], pk[i], (uchar const *)"x", 1UL ) );
+    FD_TEST(  ag_bls_sig_verify( sig[i], pk[i],          msg,  msg_sz ) );
+    FD_TEST( !ag_bls_sig_verify( sig[i], pk[(i+1UL)%N],  msg,  msg_sz ) );
+    FD_TEST( !ag_bls_sig_verify( sig[i], pk[i], (uchar const *)"x", 1UL ) );
   }
 
   ag_bls_pub_t pks[5];
@@ -140,31 +153,33 @@ test_roundtrip( void ) {
   { ulong _sel[3] = { 0UL, 2UL, 4UL }; pick_sig( sigs, sig, _sel, 3UL ); }
   ulong        idx [3] = { 0UL, 2UL, 4UL };
   ag_bls_agg_t agg[1];
-  ag_bls_agg_new( agg, (ag_bls_sig_t const *)sigs, idx, 3UL, N );
+  ag_bls_agg_zero( agg );
+  for( ulong i=0UL; i<3UL; i++ ) ag_bls_agg_add( agg, idx[i], sigs[i] );
 
-  FD_TEST( ag_bls_agg_verify_bytes( agg, msg, msg_sz, pks[0], sizeof(ag_bls_pub_t), N ) );
+  FD_TEST( ag_bls_agg_verify( agg, msg, msg_sz, pks[0], sizeof(ag_bls_pub_t), N ) );
 
-  FD_TEST( !ag_bls_agg_verify_bytes( agg, (uchar const *)"different message", 17UL, pks[0], sizeof(ag_bls_pub_t), N ) );
+  FD_TEST( !ag_bls_agg_verify( agg, (uchar const *)"different message", 17UL, pks[0], sizeof(ag_bls_pub_t), N ) );
 
   ag_bls_agg_t tampered = *agg;
   tampered.sig[0] = (uchar)( tampered.sig[0] ^ 0xFFu );
-  FD_TEST( !ag_bls_agg_verify_bytes( &tampered, msg, msg_sz, pks[0], sizeof(ag_bls_pub_t), N ) );
+  FD_TEST( !ag_bls_agg_verify( &tampered, msg, msg_sz, pks[0], sizeof(ag_bls_pub_t), N ) );
 
   ag_bls_pub_t pks_wrong[5];
   { ulong _sel[5] = { 1UL, 1UL, 2UL, 3UL, 4UL }; pick_pub( pks_wrong, pk, _sel, 5UL ); }
-  FD_TEST( !ag_bls_agg_verify_bytes( agg, msg, msg_sz, pks_wrong[0], sizeof(ag_bls_pub_t), N ) );
+  FD_TEST( !ag_bls_agg_verify( agg, msg, msg_sz, pks_wrong[0], sizeof(ag_bls_pub_t), N ) );
 
   ag_bls_agg_t mismatch = *agg;
-  voter_set_remove( mismatch.bitmask, 4UL );
+  signer_set_remove( mismatch.bitmask, 4UL );
   FD_TEST( ag_bls_agg_signer_cnt( &mismatch )==2UL );
-  FD_TEST( !ag_bls_agg_verify_bytes( &mismatch, msg, msg_sz, pks[0], sizeof(ag_bls_pub_t), N ) );
+  FD_TEST( !ag_bls_agg_verify( &mismatch, msg, msg_sz, pks[0], sizeof(ag_bls_pub_t), N ) );
 
-  FD_TEST( !ag_bls_agg_verify_bytes( agg, msg, msg_sz, pks[0], sizeof(ag_bls_pub_t), N-1UL ) );
+  FD_TEST( !ag_bls_agg_verify( agg, msg, msg_sz, pks[0], sizeof(ag_bls_pub_t), N-1UL ) );
 
   ag_bls_agg_t agg_all[1];
   ulong        idx_all[5] = { 0UL, 1UL, 2UL, 3UL, 4UL };
-  ag_bls_agg_new( agg_all, (ag_bls_sig_t const *)sig, idx_all, N, N );
-  FD_TEST( ag_bls_agg_verify_bytes( agg_all, msg, msg_sz, pks[0], sizeof(ag_bls_pub_t), N ) );
+  ag_bls_agg_zero( agg_all );
+  for( ulong i=0UL; i<N; i++ ) ag_bls_agg_add( agg_all, idx_all[i], sig[i] );
+  FD_TEST( ag_bls_agg_verify( agg_all, msg, msg_sz, pks[0], sizeof(ag_bls_pub_t), N ) );
 
   FD_LOG_NOTICE(( "blst agg sig round trip pass" ));
 }
@@ -182,11 +197,11 @@ test_derive( void ) {
   FD_TEST(  !memcmp( sk_a, sk_a2, AG_BLS_SEC_SZ ) );
   FD_TEST(   memcmp( sk_a, sk_b,  AG_BLS_SEC_SZ ) );
 
-  ag_bls_pub_t  pk; ag_bls_sec_to_pub( pk, sk_a );
+  ag_bls_pub_t  pk; ag_bls_sec_to_pub( sk_a, pk );
   uchar const * msg = (uchar const *)"derived key vote";
   ulong         msg_sz = 16UL;
-  ag_bls_sig_t  sig; ag_bls_sec_sign_bytes( sig, sk_a, msg, msg_sz );
-  FD_TEST( ag_bls_sig_verify_bytes( sig, pk, msg, msg_sz ) );
+  ag_bls_sig_t  sig; ag_bls_sec_sign( sk_a, sig, msg, msg_sz );
+  FD_TEST( ag_bls_sig_verify( sig, pk, msg, msg_sz ) );
 
   FD_LOG_NOTICE(( "bls sk derive round trip pass" ));
 }
@@ -205,13 +220,13 @@ test_ref_api( void ) {
   for( ulong i=0UL; i<N; i++ ) {
     fd_memset( sk[i], 0, AG_BLS_SEC_SZ );
     sk[i][0] = (uchar)( i+1UL );
-    ag_bls_sec_to_pub   ( pk[i], sk[i] );
-    ag_bls_sec_sign_bytes( sig[i], sk[i], msg, msg_sz );
+    ag_bls_sec_to_pub   ( sk[i], pk[i] );
+    ag_bls_sec_sign( sk[i], sig[i], msg, msg_sz );
   }
 
   /* PublicKey::try_from_bytes -- compressed and affine both round trip */
   uchar comp[ AG_BLS_PUB_COMPRESSED_SZ ];
-  ag_bls_sec_to_pub_compressed( comp, sk[0] );
+  pub_compress( comp, pk[0] );
   ag_bls_pub_t from_comp, from_aff;
   FD_TEST( !ag_bls_pub_try_from_bytes( from_comp, comp,    sizeof(comp)        ) );
   FD_TEST( !ag_bls_pub_try_from_bytes( from_aff,  pk[0], AG_BLS_PUB_SZ    ) );
@@ -226,13 +241,14 @@ test_ref_api( void ) {
   { ulong _sel[3] = { 0UL, 2UL, 4UL }; pick_sig( sigs, sig, _sel, 3UL ); }
   ulong        idx [3] = { 0UL, 2UL, 4UL };
   ag_bls_agg_t agg[1];
-  ag_bls_agg_new( agg, (ag_bls_sig_t const *)sigs, idx, 3UL, N );
+  ag_bls_agg_zero( agg );
+  for( ulong i=0UL; i<3UL; i++ ) ag_bls_agg_add( agg, idx[i], sigs[i] );
 
   /* signers() iteration agrees with is_signer */
   ulong seen = 0UL, cnt = 0UL;
-  for( ulong i=ag_bls_agg_signers_init( agg );
-       !ag_bls_agg_signers_done( i );
-       i=ag_bls_agg_signers_next( agg, i ) ) { seen |= 1UL<<i; cnt++; }
+  for( ulong i=ag_bls_agg_signers_iter_init( agg );
+       !ag_bls_agg_signers_iter_done( i );
+       i=ag_bls_agg_signers_iter_next( agg, i ) ) { seen |= 1UL<<i; cnt++; }
   FD_TEST( cnt==3UL );
   FD_TEST( seen==((1UL<<0)|(1UL<<2)|(1UL<<4)) );
   FD_TEST( cnt==ag_bls_agg_signer_cnt( agg ) );
@@ -251,20 +267,21 @@ test_ref_api( void ) {
 
   ag_bls_pub_t all_pk[5];
   { ulong _sel[5] = { 0UL, 1UL, 2UL, 3UL, 4UL }; pick_pub( all_pk, pk, _sel, 5UL ); }
-  FD_TEST(  ag_bls_agg_verify_bytes( agg, msg, msg_sz, all_pk[0], sizeof(ag_bls_pub_t), N     ) );
+  FD_TEST(  ag_bls_agg_verify( agg, msg, msg_sz, all_pk[0], sizeof(ag_bls_pub_t), N     ) );
   /* a bitmask wider than the key set is still a hard reject */
-  FD_TEST( !ag_bls_agg_verify_bytes( agg, msg, msg_sz, all_pk[0], sizeof(ag_bls_pub_t), N-1UL ) );
+  FD_TEST( !ag_bls_agg_verify( agg, msg, msg_sz, all_pk[0], sizeof(ag_bls_pub_t), N-1UL ) );
 
   /* Regression: wire certs carry a TRIMMED bit count (ag_signer_store
-     trimmed_nbits = highest signer rank + 1), so nbits is routinely below the
+     trimmed width = highest signer rank + 1), so it is routinely below the
      epoch validator count.  Rejecting that -- as aggsig.rs' strict
      bitmask.len()==pks.len() would -- discards almost every real cert. */
   ag_bls_sig_t tsigs[2];
   { ulong _sel[2] = { 0UL, 1UL }; pick_sig( tsigs, sig, _sel, 2UL ); }
   ulong        tidx [2] = { 0UL, 1UL };
   ag_bls_agg_t trimmed[1];
-  ag_bls_agg_new( trimmed, (ag_bls_sig_t const *)tsigs, tidx, 2UL, 2UL );
-  FD_TEST( ag_bls_agg_verify_bytes( trimmed, msg, msg_sz, all_pk[0], sizeof(ag_bls_pub_t), N ) );
+  ag_bls_agg_zero( trimmed );
+  for( ulong i=0UL; i<2UL; i++ ) ag_bls_agg_add( trimmed, tidx[i], tsigs[i] );
+  FD_TEST( ag_bls_agg_verify( trimmed, msg, msg_sz, all_pk[0], sizeof(ag_bls_pub_t), N ) );
 
   FD_LOG_NOTICE(( "reference api pass" ));
 }
```

### src/choreo/votor/test_ag_cert.c
```diff
@@ -1,5 +1,7 @@
 #include "ag_cert_serde.h"
 
+#include "../../third_party/blst/bindings/blst.h"
+
 #define TEST_SHRED_VERSION ((ushort)514)
 #include <stdlib.h>
 
@@ -17,7 +19,7 @@ create_signers( ulong n ) {
     memset( &g_info[i], 0, sizeof(ag_validator_info_t) );
     g_info[i].id    = i;
     g_info[i].stake = 1UL;
-    ag_bls_sec_to_pub( g_info[i].bls_key, g_sk[i] );
+    ag_bls_sec_to_pub( g_sk[i], g_info[i].bls_key );
   }
 }
 
@@ -384,17 +386,105 @@ test_sig_validity( void ) {
   free( em );
 }
 
+/* agave votor/src/aggregate_accumulator.rs:124-125
+
+   "Individually valid votes can still be chosen such that their signatures
+   cancel to the identity within one partition, making any certificate
+   containing that partition invalid.  Treat an identity partition as absent
+   and do not count its stake."  Ranks 9 and 10 hold negated keys -- proof of
+   possession does not prevent that -- so their two fallback signatures over
+   the same payload sum to the point at infinity.  The research reference has
+   no such check, so there is no test of it to mirror. */
+
+static void
+negate_sec( ag_bls_sec_t       out,
+            ag_bls_sec_t const in ) {
+  blst_scalar s[1];
+  blst_fr     f[1];
+  blst_scalar_from_lendian( s, in );
+  blst_fr_from_scalar( f, s );
+  blst_fr_cneg( f, f, 1 );
+  blst_scalar_from_fr( s, f );
+  memcpy( out, s->b, AG_BLS_SEC_SZ );
+}
+
+/* the bitmap version byte of a serialized notar-fallback cert: 0 is base2
+   (one partition), 1 is base3 (two).  The bitmap follows the head, whose
+   size includes the block hash. */
+
+static uchar
+bitmap_version( ag_cert_t const * c ) {
+  uchar buf[ 512 ];
+  FD_TEST( ag_cert_ser( c, TEST_SHRED_VERSION, buf, sizeof(buf), NULL )==0 );
+  return buf[ sizeof(ag_cert_serde_t) ];
+}
+
+static void
+test_identity_partition( void ) {
+  ulong n = 11UL;
+  create_signers( n );
+  negate_sec( g_sk[10], g_sk[9] );
+  ag_bls_sec_to_pub( g_sk[10], g_info[10].bls_key );
+  void * em; ag_epoch_info_t * e = make_epoch( n, &em );
+  ag_block_hash_t h; memset( h, 0x42, sizeof(ag_block_hash_t) );
+
+  ag_notar_vote_t          nv [ 11 ];
+  ag_notar_fallback_vote_t fv [ 11 ];
+  ag_skip_vote_t           sv [ 11 ];
+  ag_skip_fallback_vote_t  sfv[ 11 ];
+  ag_cert_t c; c.kind = AG_CERT_TYPE_NOTAR_FALLBACK;
+
+  /* control: ranks 8 and 9 do not cancel, so both partitions survive */
+  mk_notar( nv, 1UL, h, 0UL, 7UL );
+  mk_nf   ( fv, 1UL, h, 8UL, 2UL );
+  c.inner.notar_fallback = ag_notar_fallback_cert_construct( nv, 7UL, fv, 2UL, e );
+  FD_TEST( cert_stake( &c )==9UL );
+  FD_TEST( cert_is_signer( &c, 8UL ) && cert_is_signer( &c, 9UL ) );
+  FD_TEST( bitmap_version( &c )==1 );
+  FD_TEST( cert_verify( &c, e ) );
+
+  /* ranks 9 and 10 cancel: the fallback partition is absent, its stake is not
+     counted, and the cert degrades to the single partition form */
+  mk_nf( fv, 1UL, h, 9UL, 2UL );
+  c.inner.notar_fallback = ag_notar_fallback_cert_construct( nv, 7UL, fv, 2UL, e );
+  FD_TEST( ag_bls_agg_signer_cnt( &c.inner.notar_fallback.agg_sig_notar_fallback )==0UL );
+  FD_TEST( !cert_is_signer( &c, 9UL ) && !cert_is_signer( &c, 10UL ) );
+  FD_TEST( cert_stake( &c )==7UL );
+  FD_TEST( bitmap_version( &c )==0 );
+  FD_TEST( cert_verify( &c, e ) ); /* the 7 surviving notar votes still clear 60% */
+
+  /* same in a skip cert's fallback partition */
+  mk_skip( sv,  1UL, 0UL, 7UL );
+  mk_sf  ( sfv, 1UL, 9UL, 2UL );
+  c.kind = AG_CERT_TYPE_SKIP;
+  c.inner.skip = ag_skip_cert_construct( sv, 7UL, sfv, 2UL, e );
+  FD_TEST( ag_bls_agg_signer_cnt( &c.inner.skip.agg_sig_skip_fallback )==0UL );
+  FD_TEST( !cert_is_signer( &c, 9UL ) && !cert_is_signer( &c, 10UL ) );
+  FD_TEST( cert_stake( &c )==7UL );
+  FD_TEST( cert_verify( &c, e ) );
+
+  /* without the dropped partition the remaining stake can fall short, which is
+     what stops ag_slot_state.c from emitting the cert at all */
+  mk_notar( nv, 1UL, h, 0UL, 6UL );
+  c.kind = AG_CERT_TYPE_NOTAR_FALLBACK;
+  c.inner.notar_fallback = ag_notar_fallback_cert_construct( nv, 6UL, fv, 2UL, e );
+  FD_TEST( cert_stake( &c )==6UL );
+  FD_TEST( !cert_verify( &c, e ) );
+
+  free( em );
+}
+
 static ulong
-put_aggregate( uchar * p, ulong nbits, ulong signer_cnt ) {
+put_aggregate( uchar * p, ulong bits, ulong signer_cnt ) {
   memset( p, 0, AG_BLS_SIG_COMPRESSED_SZ );
   p[0] = 0xc0;
-  ulong payload = (nbits+7UL)/8UL;
+  ulong payload = (bits+7UL)/8UL;
   ulong bm_cnt  = 3UL+payload;
   p[ AG_BLS_SIG_COMPRESSED_SZ     ] = (uchar)( bm_cnt     & 0xffUL );
   p[ AG_BLS_SIG_COMPRESSED_SZ+1UL ] = (uchar)( (bm_cnt>>8) & 0xffUL );
   uchar * b = p+AG_BLS_SIG_COMPRESSED_SZ+2UL;
   b[0] = 0;
-  b[1] = (uchar)( nbits & 0xffUL ); b[2] = (uchar)( nbits>>8 );
+  b[1] = (uchar)( bits & 0xffUL ); b[2] = (uchar)( bits>>8 );
   memset( b+3UL, 0, payload );
   for( ulong i=0UL; i<signer_cnt; i++ ) b[ 3UL+(i>>3) ] = (uchar)( b[ 3UL+(i>>3) ] | (1U<<(i&7UL)) );
   return AG_BLS_SIG_COMPRESSED_SZ+2UL+bm_cnt;
@@ -459,6 +549,7 @@ main( int     argc,
   test_failure_cases();
   test_thresholds();
   test_sig_validity();
+  test_identity_partition();
 
   test_footer_de();
   FD_LOG_NOTICE(( "pass" ));
```

### src/choreo/votor/test_ag_epoch_info.c
```diff
@@ -11,7 +11,7 @@ make_epoch( ulong   n,
     v[i].id    = i;
     v[i].stake = 1UL;
     ag_bls_sec_t sk; fd_memset( sk, (int)(i+1UL), AG_BLS_SEC_SZ );
-    ag_bls_sec_to_pub( v[i].bls_key, sk );
+    ag_bls_sec_to_pub( sk, v[i].bls_key );
   }
   ag_epoch_info_t * ei = aligned_alloc( alignof(ag_epoch_info_t), sizeof(ag_epoch_info_t) );
   FD_TEST( ei );
```

### src/choreo/votor/test_ag_pool.c
```diff
@@ -129,7 +129,7 @@ create_validators( void ) {
     memset( &g_info[i], 0, sizeof(ag_validator_info_t) );
     g_info[i].id    = i;
     g_info[i].stake = 1UL;
-    ag_bls_sec_to_pub( g_info[i].bls_key, g_sk[i] );
+    ag_bls_sec_to_pub( g_sk[i], g_info[i].bls_key );
   }
 }
 
@@ -785,7 +785,7 @@ test_standstill_recovery( void ) {
   }
 
   for( ulong i=0UL; i<certs_cnt; i++ ) {
-    uchar buf[ sizeof(ag_cert_serde_t) + sizeof(ag_cert_bitmap_serde_t) + (AG_BLS_MAX_SIGNERS+4UL)/5UL + 2UL ];
+    uchar buf[ sizeof(ag_cert_serde_t) + sizeof(ag_cert_bitmap_serde_t) + (AG_BLS_SIGNERS_MAX+4UL)/5UL + 2UL ];
     ulong sz;
     FD_TEST( ag_cert_ser( &certs[i], TEST_SHRED_VERSION, buf, sizeof(buf), &sz )==0 );
     ag_cert_t rt; ulong consumed;
```

### src/choreo/votor/test_ag_slot_state.c
```diff
@@ -19,7 +19,7 @@ generate_validators( ulong n ) {
     memset( &g_info[i], 0, sizeof(ag_validator_info_t) );
     g_info[i].id    = i;
     g_info[i].stake = 1UL;
-    ag_bls_sec_to_pub( g_info[i].bls_key, g_sk[i] );
+    ag_bls_sec_to_pub( g_sk[i], g_info[i].bls_key );
   }
 }
 
```
