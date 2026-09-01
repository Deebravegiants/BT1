# [C] Identity Spoofing in libp2p-secio

## Summary
Severity: Critical
Chain: libp2p-secio
Component: libp2p-secio
CWE: Authentication Bypass by Spoofing
Published: 2019-08-23
Source: https://github.com/advisories/GHSA-rch7-f4h5-x9rj
Type: github-advisory

## Details
Affected versions of `libp2p-secio` does not correctly verify that the `PeerId` of `DstPeer` matches the `PeerId` discovered in the crypto handshake, resulting in a high severity identity spoofing vulnerability. 


## Recommendation

Update to version 0.9.0 or later.
