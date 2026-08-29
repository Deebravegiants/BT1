# [?] Avoid panicking when attempting to send an oversized message

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2026-08-04
Source: https://github.com/lightningdevkit/rust-lightning/commit/c5fdc3bf018c702bf6815f45b0496df1966dcf2f
Type: security-commit

## Details
Avoid panicking when attempting to send an oversized message

While this code should remain unreachable as it likely indicates
we're going to end up force-closing a channel due to being unable
to communicate with a peer, we shouldn't bring down the whole
process for it if we can avoid it.

Co-Authored-By: Claude <noreply@anthropic.com>
