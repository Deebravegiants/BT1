# [?] fix: resolve database deadlock: (#4989)

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2024-04-18
Source: https://github.com/XRPLF/rippled/commit/cd737ad7d31be228b00d81c7ad121b6fbcbb00ce
Type: security-commit

## Details
fix: resolve database deadlock: (#4989)

The `rotateWithLock` function holds a lock while it calls a callback
function that's passed in by the caller. This is a problematic design
that needs to be used very carefully. In this case, at least one caller
passed in a callback that eventually relocks the mutex on the same
thread, causing UB (a deadlock was observed). The caller was from
SHAMapStoreImpl, and it called `clearCaches`. This `clearCaches` can
potentially call `fetchNodeObject`, which tried to relock the mutex.

This patch resolves the issue by changing the mutex type to a
`recursive_mutex`. Ideally, the code should be rewritten so it doesn't
hold the mutex during the callback and the mutex should be changed back
to a regular mutex.

Co-authored-by: Ed Hennis <ed@ripple.com>
