# [?] server: fix panic bug when looking for cf checkpoint cache intersection w/ chain

## Summary
Severity: Unknown
Chain: Bitcoin
Component: btcsuite/btcd
Published: 2018-08-28
Source: https://github.com/btcsuite/btcd/commit/222a6dac0d99f222bbe95f2c055888d87baec07c
Type: security-commit

## Details
server: fix panic bug when looking for cf checkpoint cache intersection w/ chain

In this commit, we fix a panic bug that can arise when we attempt to
process a cf checkpoint message from a remote peer. Before this commit,
if the size of the checkpoint cache was large than the number of
checkpoints requested by the peer, we would panic with an out of bounds
error. In order to prevent, this we'll now use the size of the requested
set of hashes as our bound to ensure that we don't panic.
