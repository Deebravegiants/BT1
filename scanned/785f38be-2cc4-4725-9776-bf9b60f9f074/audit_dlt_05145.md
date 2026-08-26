# [?] Fix race condition causing async payment failure

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2025-09-18
Source: https://github.com/lightningdevkit/rust-lightning/commit/ade1f3484aebf17dc9bae1633dec2d3350d4ea4d
Type: security-commit

## Details
Fix race condition causing async payment failure

As the LSP of an async sender, when we receive an update_add with the hold_htlc
flag set, after its onion is decoded we transition the pending HTLC to the
ChannelManager::pending_intercepted_htlcs.  However, if we receive the
release_held_htlc message from the receiver *before* we've had a chance to make
this transition, we'll fail to release the HTLC and it will sit in the pending
intercepts map until it is failed backwards.

To fix this race condition, if we receive release_held_htlc from the recipient
we'll not only check the pending_intercepted_htlcs map for the presence of this
HTLC but also check the map where we keep HTLCs prior to their onions being
decoded.
