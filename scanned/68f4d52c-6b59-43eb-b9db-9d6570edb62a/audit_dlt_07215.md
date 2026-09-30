# [?] log: fix signal lock reentrancy bug

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-08-19
Source: https://github.com/firedancer-io/firedancer/commit/65b1641beeb87b861aa68200fd1505739d506d11
Type: security-commit

## Details
log: fix signal lock reentrancy bug

Fixes a bug in fd_log where a thread starts infinite looping if it
catches a signal while already holding a log lock.  This affects
all regular executables (e.g. unit tests) but not fdctl.

## Patch
### src/util/log/fd_log.c
```diff
@@ -1008,6 +1008,13 @@ fd_log_private_sig_abort( int         sig,
                           void *      context ) {
   (void)info; (void)context;
 
+  /* Thread could have caught signal while holding a lock.
+     Hack around this re-entrancy problem by pointing the log lock to
+     a dummy buffer. */
+  int * old_lock = fd_log_private_shared_lock;
+  static FD_TL int lock = 0;
+  fd_log_private_shared_lock = &lock;
+
   /* Hopefully all out streams are idle now and we have flushed out
      all non-logging activity ... log a backtrace */
 
@@ -1042,6 +1049,7 @@ fd_log_private_sig_abort( int         sig,
 
   usleep( (useconds_t)1000000 ); /* Give some time to let streams drain */
 
+  fd_log_private_shared_lock = old_lock;
   raise( sig ); /* Continue with the original handler (probably the default and that will produce the core) */
 }
 
```
