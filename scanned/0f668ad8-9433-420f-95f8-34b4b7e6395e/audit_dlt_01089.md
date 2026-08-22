# [H] Failure to verify the public key of a `SignedEnvelope` against the `PeerId` in a `PeerRecord`

## Summary
Severity: High
Chain: libp2p-core
Component: libp2p-core
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-wc36-xgcc-jwpr
Type: github-advisory

## Details
Affected versions of this crate did not check that the public key the signature was created with matches the peer ID of the peer record. 
Any combination was considered valid.

This allows an attacker to republish an existing `PeerRecord` with a different `PeerId`.
