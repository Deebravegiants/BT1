# [M] Potential Denial-of-Service condition leading to temporary disability in IBC transfers to the native chain

## Summary
Severity: Medium
Chain: github.com/cosmos/ibc-apps/middleware/packet-forward-middleware/v7
Component: github.com/cosmos/ibc-apps/middleware/packet-forward-middleware/v7, github.com/cosmos/ibc-apps/middleware/packet-forward
Published: 2025-02-12
Source: https://github.com/advisories/GHSA-6fgm-x6ff-w78f
Type: github-advisory

## Details
### Impact

Chains using affected versions of Packet Forward Middleware in their IBC Transfer stack are vulnerable to an attack in which there is a potential denial of service. This affects IBC transfers for any asset which is being transferred between another chain and its native chain.

We recommend upgrading as soon as possible.

__THIS IS A STATE BREAKING CHANGE__


### Patches
Versions [7.2.1](https://github.com/cosmos/ibc-apps/releases/tag/middleware%2Fpacket-forward-middleware%2Fv7.2.1) and [8.1.1](https://github.com/cosmos/ibc-apps/releases/tag/middleware%2Fpacket-forward-middleware%2Fv8.1.1) are patched.

### Workarounds
N/A

### References
N/A
