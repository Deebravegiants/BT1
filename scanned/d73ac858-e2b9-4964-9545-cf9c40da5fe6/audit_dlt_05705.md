# [?] discovery: fix gossiper shutdown deadlock

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
Published: 2026-02-02
Source: https://github.com/lightningnetwork/lnd/commit/21588acb3d5b9b4bb605b0852c91f10b6bb2a1c6
Type: security-commit

## Details
discovery: fix gossiper shutdown deadlock

When processing a remote network announcement, it is possible for two
error messages to be sent back on the errChan.  Since Brontide doesn't
actually read from errChan, and since errChan only buffered one error
message, the sending goroutine would deadlock forever.  This would only
become apparent when the gossiper attempted to shut down and got hung
up.

For now, we can fix this simply by buffering up to two error messages on
errChan.  There is an existing TODO to restructure this logic entirely
to use the actor model, and we can do a more thorough fix as part of
that work.

This bug was discovered while doing full node fuzz testing and was
triggered by sending a specific channel_announcement message and then
shutting down LND.
