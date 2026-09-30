# [?] fdctl: prevent hang exiting after tile crash

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-02-27
Source: https://github.com/firedancer-io/firedancer/commit/066cd3fe9f718fe156d130585c2b6272beea68a9
Type: security-commit

## Details
fdctl: prevent hang exiting after tile crash

## Patch
### src/app/fdctl/run/run.c
```diff
@@ -347,6 +347,12 @@ main_pid_namespace( void * _args ) {
     fd_sandbox_switch_uid_gid( config->uid, config->gid );
   }
 
+  /* The supervsior process should not share the log lock, because a
+     child process might die while holding it and we still need to
+     reap and print errors. */
+  int lock = 0;
+  fd_log_private_shared_lock = &lock;
+
   /* Reap child process PIDs so they don't show up in `ps` etc.  All of
      these children should have exited immediately after clone(2)'ing
      another child with a huge page based stack. */
@@ -358,12 +364,6 @@ main_pid_namespace( void * _args ) {
     } else if( FD_UNLIKELY( child_pids[ i ]!=exited_pid ) ) {
       FD_LOG_ERR(( "pidns wait4() returned unexpected pid %d %d", child_pids[ i ], exited_pid ));
     } else if( FD_UNLIKELY( !WIFEXITED( wstatus ) ) ) {
-      /* If the tile died with a signal like SIGSEGV or SIGSYS it might
-         still be holding the lock, which would cause us to hang when
-         writing out the error, so don't require the lock here. */
-      int lock = 0;
-      fd_log_private_shared_lock = &lock;
-
       FD_LOG_ERR_NOEXIT(( "tile %lu (%s) exited while booting with signal %d (%s)\n", i, child_names[ i ], WTERMSIG( wstatus ), fd_io_strsignal( WTERMSIG( wstatus ) ) ));
       exit_group( WTERMSIG( wstatus ) ? WTERMSIG( wstatus ) : 1 );
     }
@@ -865,6 +865,12 @@ run_firedancer( config_t * const config,
     fd_sandbox_switch_uid_gid( config->uid, config->gid );
   }
 
+  /* The supervsior process should not share the log lock, because a
+     child process might die while holding it and we still need to
+     reap and print errors. */
+  int lock = 0;
+  fd_log_private_shared_lock = &lock;
+
   /* the only clean way to exit is SIGINT or SIGTERM on this parent process,
      so if wait4() completes, it must be an error */
   int wstatus;
```
