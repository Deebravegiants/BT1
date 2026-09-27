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
