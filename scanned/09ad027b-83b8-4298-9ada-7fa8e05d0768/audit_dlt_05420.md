# [?] [event] fix underflow read in event_ring_util.c

## Summary
Severity: Unknown
Chain: Monad
Component: monad-crypto/monad
Published: 2025-09-05
Source: https://github.com/category-labs/monad/commit/b821362c3441fdf063bd216634d46d3dd2bc8b15
Type: security-commit

## Details
[event] fix underflow read in event_ring_util.c

If the buffer can't hold the full size of the file or a short read
occurs, it won't be null-terminated, and strsep will have undefined
behavior. Because of how procfs(5) works we don't expect this to
happen, but the comment (showing the format explicitly) also documents
the code better.
