# [H] Failure to validate signature during handshake

## Summary
Severity: High
Chain: @chainsafe/libp2p-noise
Component: @chainsafe/libp2p-noise, @chainsafe/libp2p-noise
CVE: CVE-2022-24759
CWE: Improper Verification of Cryptographic Signature
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-j3ff-xp6c-6gcc
Type: github-advisory

## Details
### Impact
`@chainsafe/libp2p-noise` before 4.1.2 and 5.0.3 was not correctly validating signatures during the handshake process.
This may allow a man-in-the-middle to pose as other peers and get those peers banned.

### Patches
Users should upgrade to 4.1.2 or 5.0.3

### Workarounds
No workarounds, just patch upgrade

### References
https://github.com/ChainSafe/js-libp2p-noise/pull/130
