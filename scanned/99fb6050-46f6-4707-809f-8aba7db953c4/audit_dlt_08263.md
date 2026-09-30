# [?] rpc: fix overflow

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-03-05
Source: https://github.com/firedancer-io/firedancer/commit/45defc79860405f6d798b07d1a2483adcab6474d
Type: security-commit

## Details
rpc: fix overflow

## Patch
### src/discof/rpc/fd_rpc_tile.c
```diff
@@ -49,6 +49,8 @@
 #define FD_RPC_TAR_SZ (FD_GENESIS_MAX_MESSAGE_SIZE + 4UL*512UL)
 #define FD_RPC_TAR_BZ_SZ (FD_RPC_TAR_SZ + ((FD_RPC_TAR_SZ + 100UL - 1UL) / 100UL) + 600UL)
 
+#define FD_RPC_BASE58_ENCODED_128_LEN (175UL) /* ceil(128*log58(256)) */
+
 #define FD_RPC_COMMITMENT_PROCESSED (0)
 #define FD_RPC_COMMITMENT_CONFIRMED (1)
 #define FD_RPC_COMMITMENT_FINALIZED (2)
@@ -649,8 +651,9 @@ fd_rpc_base58_encode_128( char * b58, ulong * b58sz, const void *data, ulong bin
 
   while( zcount<binsz && !bin[ zcount ] ) zcount++;
 
-  size = (binsz-zcount)*138/100+1;
-  uchar buf[ 175UL ] = { 0 };
+  size = (binsz-zcount)*138/100+1; /* strict overestimate */
+  size = fd_ulong_min( size, FD_RPC_BASE58_ENCODED_128_LEN ); /* theoretical max */
+  uchar buf[ FD_RPC_BASE58_ENCODED_128_LEN ] = { 0 };
 
   for( i=zcount, high=size-1UL; i<binsz; i++, high=j ) {
     for( carry=bin[ i ], j=size-1UL; (j>high) || carry; j-- ) {
@@ -1017,10 +1020,10 @@ getAccountInfo( fd_rpc_tile_t * ctx,
     return PRINTF_JSON( ctx, "{\"jsonrpc\":\"2.0\",\"result\":{\"context\":{\"slot\":%lu},\"value\":null},\"id\":%s}\n", info->slot, id_cstr );
   }
 
-  ulong const data_sz = fd_accdb_ref_data_sz( ro );
-  uchar const * compressed    = (uchar const *)fd_accdb_ref_data_const( ro )+fd_ulong_if(slice_offset<data_sz, slice_offset, 0UL );
-  ulong         snip_sz       = fd_ulong_min( fd_ulong_if( slice_offset<data_sz, data_sz-slice_offset, 0UL ), slice_length );
-  ulong         compressed_sz = snip_sz;
+  ulong const data_sz   = fd_accdb_ref_data_sz( ro );
+  uchar const * out     = (uchar const *)fd_accdb_ref_data_const( ro )+fd_ulong_if(slice_offset<data_sz, slice_offset, 0UL );
+  ulong         snip_sz = fd_ulong_min( fd_ulong_if( slice_offset<data_sz, data_sz-slice_offset, 0UL ), slice_length );
+  ulong         out_sz  = snip_sz;
 
   int is_binary = !strncmp( encoding_cstr, "binary", strlen("binary") );
   int is_base58 = !strncmp( encoding_cstr, "base58", strlen("base58") );
@@ -1033,14 +1036,14 @@ getAccountInfo( fd_rpc_tile_t * ctx,
 
 # if FD_HAS_ZSTD
   if( is_zstd ) {
-    ulong zstd_res = ZSTD_compress( ctx->compress_buf, sizeof(ctx->compress_buf), compressed, snip_sz, 0 );
+    ulong zstd_res = ZSTD_compress( ctx->compress_buf, sizeof(ctx->compress_buf), out, snip_sz, 0 );
     if( ZSTD_isError( zstd_res ) ) {
       fd_accdb_close_ro( ctx->accdb, ro );
       CSTR_JSON( id, id_cstr );
       return PRINTF_JSON( ctx, "{\"jsonrpc\":\"2.0\",\"error\":{\"code\":-32065,\"message\":\"Firedancer Error: zstandard compression failed (%s)\"},\"id\":%s}\n", ZSTD_getErrorName( zstd_res ), id_cstr );
     }
-    compressed    = ctx->compress_buf;
-    compressed_sz = (ulong)zstd_res;
+    out = ctx->compress_buf;
+    out_sz     = (ulong)zstd_res;
   }
 # else
   if( is_zstd ) {
@@ -1068,7 +1071,7 @@ getAccountInfo( fd_rpc_tile_t * ctx,
       owner_b58,
       data_sz );
 
-  ulong encoded_sz = fd_ulong_if( is_base58 || is_binary, 175UL, FD_BASE64_ENC_SZ( snip_sz ) );
+  ulong encoded_sz = fd_ulong_if( is_base58 || is_binary, FD_RPC_BASE58_ENCODED_128_LEN, FD_BASE64_ENC_SZ( out_sz ) );
   if( FD_UNLIKELY( is_binary ) ) {
     fd_http_server_printf( ctx->http, "\"" );
   } else {
@@ -1083,9 +1086,14 @@ getAccountInfo( fd_rpc_tile_t * ctx,
   }
 
   if( FD_UNLIKELY( is_base58 || is_binary ) ) {
-    fd_rpc_base58_encode_128( (char *)encoded, &encoded_sz, compressed, compressed_sz );
+    if( FD_UNLIKELY( !fd_rpc_base58_encode_128( (char *)encoded, &encoded_sz, out, out_sz ) ) ) {
+      fd_http_server_unstage( ctx->http );
+      fd_accdb_close_ro( ctx->accdb, ro );
+      FD_LOG_WARNING(( "base58 encode failed out_sz=%lu", out_sz ));
+      return PRINTF_JSON( ctx, "{\"jsonrpc\":\"2.0\",\"error\":{\"code\":-32065,\"message\":\"Firedancer Error: base58 encode failed\"},\"id\":%s}\n", id_cstr );
+    }
   } else {
-    encoded_sz = fd_base64_encode( (char *)encoded, compressed, compressed_sz );
+    encoded_sz = fd_base64_encode( (char *)encoded, out, out_sz );
   }
 
   fd_accdb_close_ro( ctx->accdb, ro );
```
