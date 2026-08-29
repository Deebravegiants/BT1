# [?] Improve double spend error strings.

## Summary
Severity: Unknown
Chain: Bitcoin
Component: btcsuite/btcd
Published: 2015-01-07
Source: https://github.com/btcsuite/btcd/commit/c257da934e51dabbec5b2397092faed249e7ad26
Type: security-commit

## Details
Improve double spend error strings.

The mempool's MaybeAcceptTransaction methods have also been modified
to return a slice of transaction hashes referenced by the transaction
inputs which are unknown (totally spent or never seen).  While this is
currently used to include the first hash in a ProcessTransaction error
message if inserting orphans is not allowed, it may also be used in
the future to request orphan transactions from peers.
