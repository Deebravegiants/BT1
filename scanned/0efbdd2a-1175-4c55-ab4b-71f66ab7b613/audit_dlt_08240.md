# [?] backup: fix crash with --no-clone

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-08-10
Source: https://github.com/firedancer-io/firedancer/commit/c7529e35ddc2da4e833741ca795e8eacb80e0203
Type: security-commit

## Details
backup: fix crash with --no-clone

## Patch
### src/app/shared_dev/commands/dev.c
```diff
@@ -123,6 +123,9 @@ run_firedancer_threaded( config_t * config,
   }
 
   initialize_accdb_fd( config );
+  if( FD_LIKELY( config->is_firedancer ) ) {
+    initialize_snapshot_fds( config );
+  }
 
   /* This is kind of a hack, but we have to join all the workspaces as
      read-write if we are running things threaded.  The reason is that
```

### src/discof/restore/fd_snapct_tile.c
```diff
@@ -2048,11 +2048,13 @@ privileged_init( fd_topo_t const *      topo,
     FD_TEST( ctx->local_out.full_snapshot_fd!=ctx->local_out.incremental_snapshot_fd );
   }
 
-  for( uint i=0U; i<snap_max; i++ ) {
-    int fd = FD_SNAP_FD( i );
-    if( fd==ctx->local_out.full_snapshot_fd || fd==ctx->local_out.incremental_snapshot_fd ) continue;
-    if( FD_UNLIKELY( close( fd ) ) )
-      FD_LOG_ERR(( "close(snapshot pool fd %d) failed (%i-%s)", fd, errno, fd_io_strerror( errno ) ));
+  if( FD_LIKELY( fd_sandbox_gettid()==fd_sandbox_getpid() ) ) {
+    for( uint i=0U; i<snap_max; i++ ) {
+      int fd = FD_SNAP_FD( i );
+      if( fd==ctx->local_out.full_snapshot_fd || fd==ctx->local_out.incremental_snapshot_fd ) continue;
+      if( FD_UNLIKELY( close( fd ) ) )
+        FD_LOG_ERR(( "close(snapshot pool fd %d) failed (%i-%s)", fd, errno, fd_io_strerror( errno ) ));
+    }
   }
 
   FD_TEST( fd_rng_secure( &ctx->selector_seed, 8UL ) );
```
