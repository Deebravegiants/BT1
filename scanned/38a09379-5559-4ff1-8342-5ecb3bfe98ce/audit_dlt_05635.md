# [?] anacrolix/torrent: Serve peerconn panic fix (#20748)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-04-23
Source: https://github.com/erigontech/erigon/commit/2b1856faffd43ff1ab283d2200f6249eea6d5dd7
Type: security-commit

## Details
anacrolix/torrent: Serve peerconn panic fix (#20748)

Addresses https://github.com/erigontech/erigon-qa/issues/403 in main.
Needs to also be backported to 3.4.

Looks like a rare path where if there's an issue reading torrent data in
order to serve a peer request, then an invariant was broken and
triggered a logic panic. The fix ensures that on a bad read the
invariants are maintained.

Make sure to trigger the first 2 workflows per the issue to verify.
