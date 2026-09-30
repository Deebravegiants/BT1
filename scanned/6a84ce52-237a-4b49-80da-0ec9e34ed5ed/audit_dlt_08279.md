# [?] pidns: fix race condition in child collection

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-10-13
Source: https://github.com/firedancer-io/firedancer/commit/90f599861ab2bf0b94e088aa0523bf9a5d9484df
Type: security-commit

## Details
pidns: fix race condition in child collection

## Patch
### src/app/shared/commands/run/run.c
```diff
@@ -255,6 +255,8 @@ main_pid_namespace( void * _args ) {
     FD_LOG_ERR(( "fd_cpuset_getaffinity failed (%i-%s)", errno, fd_io_strerror( errno ) ));
 
   pid_t child_pids[ FD_TOPO_MAX_TILES+1 ];
+  ulong actual_pids[ FD_TOPO_MAX_TILES+1 ];
+  for( ulong i=0UL; i<FD_TOPO_MAX_TILES+1; i++ ) actual_pids[ i ] = ULONG_MAX;
   char  child_names[ FD_TOPO_MAX_TILES+1 ][ 32 ];
   ulong child_idxs[ FD_TOPO_MAX_TILES+1 ];
   struct pollfd fds[ FD_TOPO_MAX_TILES+2 ];
@@ -272,6 +274,9 @@ main_pid_namespace( void * _args ) {
     if( FD_UNLIKELY( pipe2( pipefd, O_CLOEXEC ) ) ) FD_LOG_ERR(( "pipe2() failed (%i-%s)", errno, fd_io_strerror( errno ) ));
     fds[ child_cnt ] = (struct pollfd){ .fd = pipefd[ 0 ], .events = 0 };
     child_pids[ child_cnt ] = execve_agave( config_memfd, pipefd[ 1 ] );
+    FD_TEST( child_pids[ child_cnt ]>0 );
+    actual_pids[ child_cnt ] = (ulong)child_pids[ child_cnt ];
+    child_idxs[ child_cnt ] = ULONG_MAX;
     if( FD_UNLIKELY( close( pipefd[ 1 ] ) ) ) FD_LOG_ERR(( "close() failed (%i-%s)", errno, fd_io_strerror( errno ) ));
     strncpy( child_names[ child_cnt ], "agave", 32 );
     child_cnt++;
@@ -317,6 +322,12 @@ main_pid_namespace( void * _args ) {
     child_cnt++;
   }
 
+  /* Obtain the actual grandchild PID from the pipe */
+  for( ulong i=0UL; i<child_cnt; i++ ) {
+    if( FD_UNLIKELY( actual_pids[ i ]!=ULONG_MAX ) ) continue;
+    FD_TEST( 8UL==read( fds[ i ].fd, &actual_pids[ i ], 8UL ) );
+  }
+
   if( FD_UNLIKELY( -1==setpriority( PRIO_PROCESS, 0, save_priority ) ) ) FD_LOG_ERR(( "setpriority() failed (%i-%s)", errno, fd_io_strerror( errno ) ));
   if( FD_UNLIKELY( fd_cpuset_setaffinity( 0, floating_cpu_set ) ) )
     FD_LOG_ERR(( "fd_cpuset_setaffinity failed (%i-%s)", errno, fd_io_strerror( errno ) ));
@@ -334,7 +345,7 @@ main_pid_namespace( void * _args ) {
   if( FD_LIKELY( fd_log_private_logfile_fd()!=-1 ) )
     allow_fds[ allow_fds_cnt++ ] = fd_log_private_logfile_fd(); /* logfile */
   allow_fds[ allow_fds_cnt++ ] = args->pipefd[ 1 ]; /* write end of main pipe */
-  for( ulong i=0; i<child_cnt; i++ )
+  for( ulong i=0UL; i<child_cnt; i++ )
     allow_fds[ allow_fds_cnt++ ] = fds[ i ].fd; /* read end of child pipes */
 
   struct sock_filter seccomp_filter[ 128UL ];
@@ -375,7 +386,7 @@ main_pid_namespace( void * _args ) {
   /* Reap child process PIDs so they don't show up in `ps` etc.  All of
      these children should have exited immediately after clone(2)'ing
      another child with a huge page based stack. */
-  for( ulong i=0; i<child_cnt; i++ ) {
+  for( ulong i=0UL; i<child_cnt; i++ ) {
     int wstatus;
     int exited_pid = wait4( child_pids[ i ], &wstatus, (int)__WALL, NULL );
     if( FD_UNLIKELY( -1==exited_pid ) ) {
@@ -393,6 +404,8 @@ main_pid_namespace( void * _args ) {
   }
 
   fds[ child_cnt ] = (struct pollfd){ .fd = args->pipefd[ 1 ], .events = 0 };
+  strncpy( child_names[ child_cnt ], "parent", 32UL );
+  child_idxs[ child_cnt ] = ULONG_MAX;
 
   /* We are now the init process of the pid namespace.  If the init
      process dies, all children are terminated.  If any child dies, we
@@ -401,45 +414,52 @@ main_pid_namespace( void * _args ) {
      a group.  The parent process will also die if this process dies,
      due to getting SIGHUP on the pipe. */
   while( 1 ) {
-    if( FD_UNLIKELY( -1==poll( fds, 1+child_cnt, -1 ) ) ) FD_LOG_ERR(( "poll() failed (%i-%s)", errno, fd_io_strerror( errno ) ));
-
-    for( ulong i=0UL; i<1UL+child_cnt; i++ ) {
-      if( FD_UNLIKELY( fds[ i ].revents ) ) {
-        /* Must have been POLLHUP, POLLERR and POLLNVAL are not possible. */
-        if( FD_UNLIKELY( i==child_cnt ) ) {
-          /* Parent process died, probably SIGINT, exit gracefully. */
-          fd_sys_util_exit_group( 0 );
-        }
+    if( FD_UNLIKELY( -1==poll( fds, 1UL+child_cnt, -1 ) ) ) FD_LOG_ERR(( "poll() failed (%i-%s)", errno, fd_io_strerror( errno ) ));
 
-        char * tile_name = child_names[ i ];
-        ulong  tile_idx = child_idxs[ i ];
-        ulong  tile_id = config->topo.tiles[ tile_idx ].kind_id;
-
-        /* Child process died, reap it to figure out exit code. */
-        int wstatus;
-        int exited_pid = wait4( -1, &wstatus, (int)__WALL | (int)WNOHANG, NULL );
-        if( FD_UNLIKELY( -1==exited_pid ) ) {
-          FD_LOG_ERR(( "pidns wait4() failed (%i-%s) %lu %hu", errno, fd_io_strerror( errno ), i, fds[ i ].revents ));
-        } else if( FD_UNLIKELY( !exited_pid ) ) {
-          /* Spurious wakeup, no child actually dead yet. */
-          continue;
-        }
+    /* Parent process died, probably SIGINT, exit gracefully. */
+    if( FD_UNLIKELY( fds[ child_cnt ].revents ) ) fd_sys_util_exit_group( 0 );
+
+    /* Child process died, reap it to figure out exit code. */
+    int wstatus;
+    int exited_pid = wait4( -1, &wstatus, (int)__WALL | (int)WNOHANG, NULL );
+    if( FD_UNLIKELY( -1==exited_pid ) ) {
+      FD_LOG_ERR(( "pidns wait4() failed (%i-%s)", errno, fd_io_strerror( errno ) ));
+    } else if( FD_UNLIKELY( !exited_pid ) ) {
+      /* Spurious wakeup, no child actually dead yet. */
+      continue;
+    }
+
+    /* Now find the tile corresponding to that PID */
+    FD_TEST( exited_pid>0 );
+    int found = 0;
+    for( ulong i=0UL; i<child_cnt; i++ ) {
+      if( FD_LIKELY( actual_pids[ i ]!=(ulong)exited_pid ) ) continue;
+
+      found = 1;
+      fds[ i ].fd = -1; /* Don't poll on this tile anymore */
+
+      char * tile_name = child_names[ i ];
+      ulong  tile_idx = child_idxs[ i ];
+      ulong  tile_id = config->topo.tiles[ tile_idx ].kind_id;
 
-        if( FD_UNLIKELY( !WIFEXITED( wstatus ) ) ) {
-          FD_LOG_ERR_NOEXIT(( "tile %s:%lu exited with signal %d (%s)", tile_name, tile_id, WTERMSIG( wstatus ), fd_io_strsignal( WTERMSIG( wstatus ) ) ));
-          fd_sys_util_exit_group( WTERMSIG( wstatus ) ? WTERMSIG( wstatus ) : 1 );
+      if( FD_UNLIKELY( !WIFEXITED( wstatus ) ) ) {
+        FD_LOG_ERR_NOEXIT(( "tile %s:%lu exited with signal %d (%s)", tile_name, tile_id, WTERMSIG( wstatus ), fd_io_strsignal( WTERMSIG( wstatus ) ) ));
+        fd_sys_util_exit_group( WTERMSIG( wstatus ) ? WTERMSIG( wstatus ) : 1 );
+      } else {
+        int exit_code = WEXITSTATUS( wstatus );
+        if( FD_LIKELY( !exit_code && tile_idx!=ULONG_MAX && config->topo.tiles[ tile_idx ].allow_shutdown ) ) {
+          found = 1;
+          FD_LOG_INFO(( "tile %s:%lu exited gracefully with code %d", tile_name, tile_id, exit_code ));
         } else {
-          int exit_code = WEXITSTATUS( wstatus );
-          if( FD_LIKELY( !exit_code && config->topo.tiles[ tile_idx ].allow_shutdown ) ) {
-            FD_LOG_INFO(( "tile %s:%lu exited gracefully with code %d", tile_name, tile_id, exit_code ));
-          } else {
-            FD_LOG_ERR_NOEXIT(( "tile %s:%lu exited with code %d", tile_name, tile_id, exit_code ));
-            fd_sys_util_exit_group( exit_code ? exit_code : 1 );
-          }
+          FD_LOG_ERR_NOEXIT(( "tile %s:%lu exited with code %d", tile_name, tile_id, exit_code ));
+          fd_sys_util_exit_group( exit_code ? exit_code : 1 );
         }
       }
     }
+
+    if( FD_UNLIKELY( !found ) ) FD_LOG_ERR(( "wait4() returned unexpected pid %d", exited_pid ));
   }
+
   return 0;
 }
 
```

### src/app/shared/commands/run/run1.c
```diff
@@ -104,4 +104,9 @@ run1_cmd_fn( args_t *   args,
   int flags = config->development.sandbox ? CLONE_NEWPID : 0;
   pid_t clone_pid = clone( tile_main, (uchar *)stack + FD_TILE_PRIVATE_STACK_SZ, flags, &clone_args );
   if( FD_UNLIKELY( clone_pid<0 ) ) FD_LOG_ERR(( "clone() failed (%i-%s)", errno, fd_io_strerror( errno ) ));
+
+  if( FD_LIKELY( args->run1.pipe_fd!=-1 ) ) {
+    ulong pid = (ulong)clone_pid;
+    if( FD_UNLIKELY( 8UL!=write( args->run1.pipe_fd, &pid, 8UL ) ) ) FD_LOG_ERR(( "write() failed (%i-%s)", errno, fd_io_strerror( errno ) ));
+  }
 }
```

### src/app/shared/commands/watch/generated/watch_seccomp.h
```diff
@@ -21,32 +21,28 @@
 #else
 # error "Target architecture is unsupported by seccomp."
 #endif
-static const unsigned int sock_filter_policy_watch_instr_cnt = 26;
+static const unsigned int sock_filter_policy_watch_instr_cnt = 24;
 
 static void populate_sock_filter_policy_watch( ulong out_cnt, struct sock_filter * out, unsigned int logfile_fd, unsigned int drain_output_fd ) {
-  FD_TEST( out_cnt >= 26 );
-  struct sock_filter filter[26] = {
+  FD_TEST( out_cnt >= 24 );
+  struct sock_filter filter[24] = {
     /* Check: Jump to RET_KILL_PROCESS if the script's arch != the runtime arch */
     BPF_STMT( BPF_LD | BPF_W | BPF_ABS, ( offsetof( struct seccomp_data, arch ) ) ),
-    BPF_JUMP( BPF_JMP | BPF_JEQ | BPF_K, ARCH_NR, 0, /* RET_KILL_PROCESS */ 22 ),
+    BPF_JUMP( BPF_JMP | BPF_JEQ | BPF_K, ARCH_NR, 0, /* RET_KILL_PROCESS */ 20 ),
     /* loading syscall number in accumulator */
     BPF_STMT( BPF_LD | BPF_W | BPF_ABS, ( offsetof( struct seccomp_data, nr ) ) ),
     /* allow write based on expression */
-    BPF_JUMP( BPF_JMP | BPF_JEQ | BPF_K, SYS_write, /* check_write */ 8, 0 ),
+    BPF_JUMP( BPF_JMP | BPF_JEQ | BPF_K, SYS_write, /* check_write */ 6, 0 ),
     /* allow fsync based on expression */
-    BPF_JUMP( BPF_JMP | BPF_JEQ | BPF_K, SYS_fsync, /* check_fsync */ 13, 0 ),
+    BPF_JUMP( BPF_JMP | BPF_JEQ | BPF_K, SYS_fsync, /* check_fsync */ 11, 0 ),
     /* simply allow nanosleep */
-    BPF_JUMP( BPF_JMP | BPF_JEQ | BPF_K, SYS_nanosleep, /* RET_ALLOW */ 19, 0 ),
+    BPF_JUMP( BPF_JMP | BPF_JEQ | BPF_K, SYS_nanosleep, /* RET_ALLOW */ 17, 0 ),
     /* simply allow sched_yield */
-    BPF_JUMP( BPF_JMP | BPF_JEQ | BPF_K, SYS_sched_yield, /* RET_ALLOW */ 18, 0 ),
+    BPF_JUMP( BPF_JMP | BPF_JEQ | BPF_K, SYS_sched_yield, /* RET_ALLOW */ 16, 0 ),
     /* simply allow exit_group */
-    BPF_JUMP( BPF_JMP | BPF_JEQ | BPF_K, SYS_exit_group, /* RET_ALLOW */ 17, 0 ),
+    BPF_JUMP( BPF_JMP | BPF_JEQ | BPF_K, SYS_exit_group, /* RET_ALLOW */ 15, 0 ),
     /* allow read based on expression */
-    BPF_JUMP( BPF_JMP | BPF_JEQ | BPF_K, SYS_read, /* check_read */ 11, 0 ),
-    /* simply allow nanosleep */
-    BPF_JUMP( BPF_JMP | BPF_JEQ | BPF_K, SYS_nanosleep, /* RET_ALLOW */ 15, 0 ),
-    /* simply allow clock_nanosleep */
-    BPF_JUMP( BPF_JMP | BPF_JEQ | BPF_K, SYS_clock_nanosleep, /* RET_ALLOW */ 14, 0 ),
+    BPF_JUMP( BPF_JMP | BPF_JEQ | BPF_K, SYS_read, /* check_read */ 9, 0 ),
     /* none of the syscalls matched */
     { BPF_JMP | BPF_JA, 0, 0, /* RET_KILL_PROCESS */ 12 },
 //  check_write:
```
