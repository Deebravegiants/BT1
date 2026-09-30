# [?] fdctl: fix MSan symbolize crash loop

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-05-12
Source: https://github.com/firedancer-io/firedancer/commit/b638a910106b887bd094c6bb6072bbd5cdddad02
Type: security-commit

## Details
fdctl: fix MSan symbolize crash loop

Use private anonymous mapped stacks when compiling with MSan.

MSan does a fork() call to backtrace ("symbolize") the process,
and fork naturally requires a MAP_PRIVATE / copy-on-write stack.

## Patch
### src/app/shared/commands/run/run.c
```diff
@@ -603,6 +603,13 @@ initialize_workspaces( config_t * config ) {
 
 void
 initialize_stacks( config_t const * config ) {
+# if FD_HAS_MSAN
+  /* MSan calls an external symbolizer using fork() on crashes, which is
+     incompatible with Firedancer's MAP_SHARED stacks. */
+  (void)config;
+  return;
+# endif
+
   /* Switch to non-root uid/gid for workspace creation.  Permissions
      checks are still done as the current user. */
   uint gid = getgid();
```

### src/disco/topo/fd_topo_run.c
```diff
@@ -169,10 +169,51 @@ run_tile_thread_main( void * _args ) {
   return NULL;
 }
 
+/* fd_topo_tile_stack_join_anon is a variant of fd_topo_tile_stack_join
+   that acquires private anonymous memory instead of shared pages.
+
+   This is required for fork() to work, as the parent and child process
+   would otherwise share a stack and corrupt each other.  While fork()
+   is banned in tile user code, some dynamic analysis tools (like MSan)
+   unfortunately rely on it. */
+
+FD_FN_UNUSED static void *
+fd_topo_tile_stack_join_anon( void ) {
+
+  ulong sz    = 2*FD_TILE_PRIVATE_STACK_SZ;
+  int   prot  = PROT_READ|PROT_WRITE;
+  int   flags = MAP_PRIVATE|MAP_ANONYMOUS|MAP_STACK;
+
+  uchar * stack = mmap( NULL, sz, prot, flags|MAP_HUGETLB, -1, 0 );
+  if( FD_UNLIKELY( stack==MAP_FAILED ) ) {
+    stack = mmap( NULL, sz, prot, flags, -1, 0 );
+    if( FD_UNLIKELY( stack==MAP_FAILED ) ) {
+      FD_LOG_ERR(( "mmap() for stack failed (%i-%s)", errno, fd_io_strerror( errno ) ));
+    }
+  }
+
+  /* Create the guard regions in the extra space */
+  void * guard_lo = (void *)( stack - FD_SHMEM_NORMAL_PAGE_SZ );
+  if( FD_UNLIKELY( mmap( guard_lo, FD_SHMEM_NORMAL_PAGE_SZ, PROT_NONE,
+                         MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED, -1, (off_t)0 )!=guard_lo ) )
+    FD_LOG_ERR(( "mmap failed (%i-%s)", errno, fd_io_strerror( errno ) ));
+
+  void * guard_hi = (void *)( stack + FD_TILE_PRIVATE_STACK_SZ );
+  if( FD_UNLIKELY( mmap( guard_hi, FD_SHMEM_NORMAL_PAGE_SZ, PROT_NONE,
+                         MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED, -1, (off_t)0 )!=guard_hi ) )
+    FD_LOG_ERR(( "mmap failed (%i-%s)", errno, fd_io_strerror( errno ) ));
+
+  return stack;
+}
+
 void *
 fd_topo_tile_stack_join( char const * app_name,
                          char const * tile_name,
                          ulong        tile_kind_id ) {
+#if FD_HAS_MSAN
+  return fd_topo_tile_stack_join_anon();
+#endif
+
   char name[ PATH_MAX ];
   FD_TEST( fd_cstr_printf_check( name, PATH_MAX, NULL, "%s_stack_%s%lu", app_name, tile_name, tile_kind_id ) );
 
```
