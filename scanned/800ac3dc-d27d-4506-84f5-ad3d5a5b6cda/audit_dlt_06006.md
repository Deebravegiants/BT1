# [?] core/bloombits: fix deadlock when matcher session hits an error (#28184)

## Summary
Severity: Unknown
Chain: Ethereum Classic
Component: etclabscore/core-geth
Published: 2023-09-25
Source: https://github.com/etclabscore/core-geth/commit/c2cfe35f121cb88650b4d90c958bcc4214d0ce7f
Type: security-commit

## Details
core/bloombits: fix deadlock when matcher session hits an error (#28184)

When MatcherSession encounters an error, it attempts to close the session.
Closing waits for all goroutines to finish, including the 'distributor'. However, the
distributor will not exit until all requests have returned.

This patch fixes the issue by delivering the (empty) result to the distributor
before calling Close().
