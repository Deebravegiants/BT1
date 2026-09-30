# [?] Fix rare SIGABRT stack use-after-free

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-12-16
Source: https://github.com/firedancer-io/firedancer/commit/2d85fcc1ef0eb8b616a0437d1b2a200fb7f97f6a
Type: security-commit

## Details
Fix rare SIGABRT stack use-after-free

fd_log_private_sig_abort updates a global pointer to point to a
local stack variable.  This is almost never a good idea.

There exists the following race condition:
- fd_log_private_sig_abort returns, causing
  fd_log_private_shared_lock to be a dangling pointer to the abort
  handler's stack
- Some other thread/process in the app tries to log and writes to
  *fd_log_private_shared_lock

The issue is probably only theoretical and requires specific timing
to trigger.

Reported-by: Cavey Cool <caveycool@gmail.com>

## Patch
### src/util/log/fd_log.c
```diff
@@ -1029,7 +1029,7 @@ fd_log_private_sig_abort( int         sig,
   /* Thread could have caught signal while holding a lock.
      Hack around this re-entrancy problem by pointing the log lock to
      a dummy buffer. */
-  int lock = 0;
+  static FD_TL int lock = 0;
   fd_log_private_shared_lock = &lock;
 
 #define FD_LOG_ERR_NOEXIT(a) do { long _fd_log_msg_now = fd_log_wallclock(); fd_log_private_1( 4, _fd_log_msg_now, __FILE__, __LINE__, __func__, fd_log_private_0 a ); } while(0)
```
