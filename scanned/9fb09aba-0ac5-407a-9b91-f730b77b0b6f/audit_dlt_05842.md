# [?] fix(index): avoid deadlock on close (#12950)

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2025-03-14
Source: https://github.com/filecoin-project/lotus/commit/c1e5f5ddf664cdfd5c5ad63ea1156f3ceefc7257
Type: security-commit

## Details
fix(index): avoid deadlock on close (#12950)

We can't hold the write lock while waiting on close because isClosed was
taking the read lock (and called while closing).

Instead, I just got rid of the locks entirely. Now, we just check the
context. Really, I'm not sure why we even have such an "is closed"
check. I _think_ what we actually want is to lock to prevent closing
until we've finished all atomic operations, but that's a larger change
and I don't have enough understanding of this code to easily make that
change.
