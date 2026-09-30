# [M] BlockTimeTooNew should not be considered as invalid block

## Summary
Severity: Medium
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2020-07-03
Source: https://github.com/nervosnetwork/ckb/security/advisories/GHSA-r9rv-9mh8-pxf4
Type: github-advisory

## Details
### Impact

Currently, when a node receives a block in future according to its local wall clock, it will mark the block as invalid and ban the peer. 

If the header's timestamp is more than 15 seconds ahead of our current time. In that case, the header may become valid in the future, and we don't want to disconnect a peer merely for serving us one too-far-ahead block header, to prevent an attacker from splitting the network by mining a block right at the  15 seconds boundary.

### Patches

Upgrade to v0.33.1 or above.

### Workarounds
Don't ban peer serving too-far-ahead block header.
