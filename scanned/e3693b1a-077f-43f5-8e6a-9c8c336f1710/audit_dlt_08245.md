# [?] genesis and rpc: integer overflow protection

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-06-15
Source: https://github.com/firedancer-io/firedancer/commit/1106845a28c6b4323b306831986154e87119efe4
Type: security-commit

## Details
genesis and rpc: integer overflow protection

## Patch
### src/discof/genesis/fd_genesi_tile.c
```diff
@@ -27,7 +27,11 @@ bz2_malloc( void * opaque,
             int    size ) {
   fd_alloc_t * alloc = (fd_alloc_t *)opaque;
 
-  void * result = fd_alloc_malloc( alloc, alignof(max_align_t), (ulong)(items*size) );
+  if( FD_UNLIKELY( items<=0 || size<=0 ) ) {
+    FD_LOG_WARNING(( "bz2_malloc: invalid items=%d or size=%d", items, size ));
+    return NULL;
+  }
+  void * result = fd_alloc_malloc( alloc, alignof(max_align_t), (ulong)items*(ulong)size );
   if( FD_UNLIKELY( !result ) ) return NULL;
   return result;
 }
@@ -194,6 +198,10 @@ after_credit( fd_genesi_tile_t *  ctx,
   if( FD_LIKELY( ctx->local_genesis ) ) {
     FD_TEST( -1!=ctx->in_fd );
 
+    if( FD_UNLIKELY( ctx->genesis_blob_sz>FD_GENESIS_MAX_MESSAGE_SIZE ) ) {
+      FD_LOG_ERR(( "Genesis file `%s` exceeds maximum size (blob_sz=%lu max=%lu)",
+                   ctx->genesis_path, ctx->genesis_blob_sz, (ulong)FD_GENESIS_MAX_MESSAGE_SIZE ));
+    }
     ulong msg_sz = sizeof(fd_genesis_meta_t) + ctx->genesis_blob_sz;
     if( FD_UNLIKELY( msg_sz>FD_GENESIS_TILE_MTU ) ) {
       FD_LOG_ERR(( "The genesis file `%s` is too large for this Firedancer build (msg_sz=%lu exceeds FD_GENESIS_TILE_MTU=%lu).\n"
@@ -258,6 +266,14 @@ after_credit( fd_genesi_tile_t *  ctx,
     FD_TEST( !strcmp( meta->name, "genesis.bin" ) );
     uchar const * blob    = decompressed+512UL;
     ulong         blob_sz = fd_tar_meta_get_size( meta );
+    if( FD_UNLIKELY( blob_sz==ULONG_MAX ) ) {
+      FD_LOG_ERR(( "Genesis blob from peer at `http://" FD_IP4_ADDR_FMT ":%hu` has invalid tar header size",
+                   FD_IP4_ADDR_FMT_ARGS( peer.addr ), fd_ushort_bswap( peer.port ) ));
+    }
+    if( FD_UNLIKELY( blob_sz>FD_GENESIS_MAX_MESSAGE_SIZE ) ) {
+      FD_LOG_ERR(( "Genesis blob from peer at `http://" FD_IP4_ADDR_FMT ":%hu` exceeds maximum size (blob_sz=%lu max=%lu)",
+                   FD_IP4_ADDR_FMT_ARGS( peer.addr ), fd_ushort_bswap( peer.port ), blob_sz, (ulong)FD_GENESIS_MAX_MESSAGE_SIZE ));
+    }
     FD_TEST( actual_decompressed_sz>=fd_ulong_sat_add( 512UL, blob_sz ) );
 
     fd_hash_t hash[1];
@@ -286,7 +302,7 @@ after_credit( fd_genesi_tile_t *  ctx,
       verify_cluster_type( genesis, hash, ctx->genesis_path );
     }
 
-    ulong msg_sz; FD_TEST( !__builtin_uaddl_overflow( sizeof(fd_genesis_meta_t), blob_sz, &msg_sz ) );
+    ulong msg_sz = sizeof(fd_genesis_meta_t) + blob_sz;
     if( FD_UNLIKELY( msg_sz>FD_GENESIS_TILE_MTU ) ) {
       FD_LOG_ERR(( "The genesis blob downloaded from peer at `http://" FD_IP4_ADDR_FMT ":%hu` is too large for this Firedancer build (msg_sz=%lu exceeds FD_GENESIS_TILE_MTU=%lu).\n"
                    "Cannot start Firedancer. Please use a different genesis config or increase FD_GENESIS_TILE_MTU.",
```

### src/discof/rpc/fd_rpc_tile.c
```diff
@@ -343,7 +343,11 @@ bz2_malloc( void * opaque,
             int    size ) {
   fd_alloc_t * alloc = (fd_alloc_t *)opaque;
 
-  void * result = fd_alloc_malloc( alloc, alignof(max_align_t), (ulong)(items*size) );
+  if( FD_UNLIKELY( items<=0 || size<=0 ) ) {
+    FD_LOG_WARNING(( "bz2_malloc: invalid items=%d or size=%d", items, size ));
+    return NULL;
+  }
+  void * result = fd_alloc_malloc( alloc, alignof(max_align_t), (ulong)items*(ulong)size );
   if( FD_UNLIKELY( !result ) ) return NULL;
   return result;
 }
@@ -368,17 +372,22 @@ fd_rpc_file_as_tarball( fd_rpc_tile_t * ctx,
                         ulong           out_sz ) {
   ulong padding_sz = 2*512UL;
   if( FD_LIKELY( data_sz % 512UL ) ) padding_sz += 512UL - (data_sz % 512UL);
-  FD_TEST( sizeof(fd_tar_meta_t)+data_sz+padding_sz <= scratch_sz );
+
+  if( FD_UNLIKELY( data_sz>FD_GENESIS_MAX_MESSAGE_SIZE ) ) {
+    FD_LOG_ERR(( "Genesis data exceeds maximum size (data_sz=%lu max=%lu)", data_sz, (ulong)FD_GENESIS_MAX_MESSAGE_SIZE ));
+  }
+  ulong tar_sz = sizeof(fd_tar_meta_t) + data_sz + padding_sz;
+  if( FD_UNLIKELY( tar_sz>scratch_sz ) ) {
+    FD_LOG_WARNING(( "tar_sz exceeds scratch_sz (tar_sz=%lu scratch_sz=%lu)", tar_sz, scratch_sz ));
+    return ULONG_MAX;
+  }
 
   fd_tar_meta_init_file_default( (fd_tar_meta_t *)scratch, filename_cstr, data_sz, fd_log_wallclock() );
   fd_memcpy( scratch+sizeof(fd_tar_meta_t), data, data_sz );
   memset( scratch+sizeof(fd_tar_meta_t)+data_sz, 0, padding_sz );
 
   /* NOTE: Agave's genesis.tar also contains a `rocksdb` folder */
 
-  ulong tar_sz = sizeof(fd_tar_meta_t)+data_sz+padding_sz;
-  FD_TEST( tar_sz<=scratch_sz );
-
   bz_stream bzstrm = {0};
   bzstrm.bzalloc = bz2_malloc;
   bzstrm.bzfree  = bz2_free;
@@ -744,6 +753,9 @@ returnable_frag( fd_rpc_tile_t *     ctx,
       blob, blob_sz,
       ctx->genesis_tar, sizeof(ctx->genesis_tar),
       ctx->genesis_tar_bz, sizeof(ctx->genesis_tar_bz) );
+    if( FD_UNLIKELY( ctx->genesis_tar_bz_sz==ULONG_MAX ) ) {
+      FD_LOG_ERR(( "failed to create genesis tarball (blob_sz=%lu)", blob_sz ));
+    }
   }
 
   return 0;
```
