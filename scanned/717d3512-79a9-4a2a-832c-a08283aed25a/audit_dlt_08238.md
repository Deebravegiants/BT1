# [?] blake3: fix oob read on larger inputs

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-08-20
Source: https://github.com/firedancer-io/firedancer/commit/b3616f222ae70747304cd4e390f5e1f0cdfec328
Type: security-commit

## Details
blake3: fix oob read on larger inputs

## Patch
### src/ballet/blake3/fd_blake3.c
```diff
@@ -769,7 +769,7 @@ fd_blake3_hash( void const * data,
 #if FD_BLAKE3_PARA_MAX>1
   for(;;) {
     fd_blake3_op_t op[1];
-    if( !fd_blake3_prepare_fast( s, tbl, op, FD_BLAKE3_PARA_MAX, 4 ) )
+    if( !fd_blake3_prepare_fast( s, tbl, op, FD_BLAKE3_PARA_MAX, FD_BLAKE3_PARA_MAX ) )
       break;
 #if FD_HAS_AVX512
     fd_blake3_avx512_compress16_fast( op->msg, op->out, op->counter, op->flags );
```

### src/ballet/blake3/test_blake3.c
```diff
@@ -1,4 +1,6 @@
 #include "../fd_ballet.h"
+#include <stdlib.h>
+#include <string.h>
 #include "fd_blake3.h"
 #include "fd_blake3_private.h"
 #include "fd_blake3_test_vector.c"
@@ -771,13 +773,40 @@ struct test_fn {
   void (* fn)( void );
 };
 
+static void
+test_blake3_hash_para_tail( void ) {
+  ulong const para = (ulong)FD_BLAKE3_PARA_MAX;
+
+  for( ulong chunks=1UL; chunks<=3UL*para; chunks++ ) {
+    ulong sz = chunks<<FD_BLAKE3_CHUNK_LG_SZ;
+
+    uchar * data = malloc( sz );
+    FD_TEST( data );
+    for( ulong i=0UL; i<sz; i++ ) data[i] = (uchar)( i*7UL+chunks );
+
+    uchar one_shot[ 32 ];
+    fd_blake3_hash( data, sz, one_shot );
+
+    fd_blake3_t _sha[1];
+    fd_blake3_t * sha = fd_blake3_join( fd_blake3_new( _sha ) );
+    FD_TEST( sha );
+    uchar streamed[ 32 ];
+    fd_blake3_fini( fd_blake3_append( fd_blake3_init( sha ), data, sz ), streamed );
+    fd_blake3_delete( fd_blake3_leave( sha ) );
+
+    FD_TEST( !memcmp( one_shot, streamed, 32UL ) );
+    free( data );
+  }
+}
+
 static struct test_fn const tests[] = {
   { "lthash",           test_lthash },
   { "constructor",      test_constructor },
   { "small_fixtures",   test_small_fixtures },
   { "rand_fixtures",    test_rand_fixtures },
   { "reduced",          test_reduced },
   { "reduced xof2048",  test_reduced_xof2048 },
+  { "hash_para_tail",   test_blake3_hash_para_tail },
 
 #if FD_HAS_AVX512
   { "test avx512_compress16_fast",         test_avx512_compress16_fast },
```
