# [?] fix(header): Only bridge node should panic on data root mismatch in e… (#2558)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-node
Published: 2023-08-11
Source: https://github.com/celestiaorg/celestia-node/commit/87e9500120c27450e264ab4ffd59c87e92186194
Type: security-commit

## Details
fix(header): Only bridge node should panic on data root mismatch in e… (#2558)

This PR fixes a DoS first discovered by @Wondertan and then secondarily
by @vgonkivs 🤠

Only bridge nodes should panic on receiving a header where the computed
data root does not match the DataHash in the RawHeader on ExtendedHeader
validation.

Resolves #2555
