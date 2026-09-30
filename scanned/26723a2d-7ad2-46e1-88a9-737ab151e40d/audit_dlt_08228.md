# [?] backup: fix crash with excessive send_buffer_size

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-09-15
Source: https://github.com/firedancer-io/firedancer/commit/b881688b8bbaa029f17b9182597998465ece8fea
Type: security-commit

## Details
backup: fix crash with excessive send_buffer_size

## Patch
### src/discof/backup/fd_snapsv_tile.c
```diff
@@ -565,10 +565,12 @@ unprivileged_init( fd_topo_t const *      topo,
 
   /* io bufs */
 
-  FD_CHECK_ERR( tile->snapsv.send_buffer_size_kib, "send_buffer_size_kib is zero" );
-  FD_CHECK_ERR( (tile->snapsv.send_buffer_size_kib<<10)>=RES_HDR_MAX, "send_buffer_size_kib is too small" );
+  ulong iobuf_sz = tile->snapsv.send_buffer_size_kib<<10;
+  FD_CHECK_ERR( iobuf_sz, "send_buffer_size_kib is zero" );
+  FD_CHECK_ERR( iobuf_sz>=RES_HDR_MAX, "send_buffer_size_kib is too small" );
+  FD_CHECK_ERR( iobuf_sz<=UINT_MAX, "[snapshots.server.send_buffer_size_kib] is too large, must be at most 4194303 KiB" );
   ulong iobuf_cnt = tile->snapsv.conn_max * 2;
-  ctx->iobuf_sz       = (uint)( tile->snapsv.send_buffer_size_kib<<10 );
+  ctx->iobuf_sz       = (uint)iobuf_sz;
   ctx->iobuf0         = iobuf0;
   ctx->iobuf_free     = iobuf_free;
   ctx->iobuf_free_cnt = (uint)iobuf_cnt;
```
