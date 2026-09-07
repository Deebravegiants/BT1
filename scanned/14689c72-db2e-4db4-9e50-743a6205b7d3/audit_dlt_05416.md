# [?] [event] fix race condition in event ring create

## Summary
Severity: Unknown
Chain: Monad
Component: monad-crypto/monad
Published: 2025-11-14
Source: https://github.com/category-labs/monad/commit/41fbfc128a7a5a9e6cd3c8512dff2d3110dc3aea
Type: security-commit

## Details
[event] fix race condition in event ring create

Currently, nothing about an event ring indicates whether the file is
properly initialized or not. A race exists where consumers can try
to mmap a partially-initialized file, and get strange errors. The new
"more robust" blockcap daemon (blockcapd) encountered this.

This commit solves the issue, using a file system atomic operation
provided by the kernel. Now a user will never see a partial file but
could still see a truncated (to zero) file.

The long comment at the top of `create_owned_event_ring` explains how
it works.
