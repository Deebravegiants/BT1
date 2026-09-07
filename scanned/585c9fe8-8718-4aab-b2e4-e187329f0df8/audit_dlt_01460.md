# [?] channeldb: fix race condition in link node pruning

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
Published: 2025-12-22
Source: https://github.com/lightningnetwork/lnd/commit/51f3c6f5286f5c6bfbc906b1861c647e5fcba61f
Type: security-commit

## Details
channeldb: fix race condition in link node pruning

This commit fixes a critical race condition in MarkChanFullyClosed and
pruneLinkNode where link nodes could be incorrectly deleted despite
having pending or open channels.

The race occurred because the check for open channels and the link node
deletion happened in separate database transactions:

  Thread A: TX1 checks open channels → [] (empty)
  Thread A: TX1 commits
  Thread B: Opens new channel with same peer
  Thread A: TX2 deletes link node (using stale data)
  Result: Link node deleted despite pending channel existing

This creates a TOCTOU (time-of-check to time-of-use) vulnerability where
database state changes between reading the channel count and deleting
the node.

Fix for MarkChanFullyClosed:
- Move link node deletion into the same transaction as the channel
  closing check, making the check-and-delete operation atomic

Fix for pruneLinkNode:
- Add double-check within the write transaction to verify no channels
  were opened since the caller's initial check
- Maintains performance by keeping early return for common case
- Prevents deletion if channels exist at delete time

This ensures the invariant: "link node exists iff channels exist"
is never violated, preventing database corruption and potential
connection issues.
