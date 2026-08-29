# [M] Tendermint light client verification not taking into account chain ID

## Summary
Severity: Medium
Chain: tendermint-light-client-verifier
Component: tendermint-light-client-verifier, tendermint-light-client, tendermint-light-client-js
CVE: CVE-2022-23507
CWE: Improper Verification of Cryptographic Signature
Published: 2022-12-14
Source: https://github.com/advisories/GHSA-xqqc-c5gw-c5r5
Type: github-advisory

## Details
### Impact

Anyone using the `tendermint-light-client` and related packages to perform light client verification (e.g. IBC-rs, Hermes).

At present, the light client does not check that the chain IDs of the trusted and untrusted headers match, resulting in a possible attack vector where someone who finds a header from an untrusted chain that satisfies all other verification conditions (e.g. enough overlapping validator signatures) could fool a light client.

The attack vector is currently theoretical, and no proof-of-concept exists yet to exploit it on live networks.

### Patches

Users of the light client-related crates can currently upgrade to `v0.28.0`.

### Workarounds

None

### References

- [Light Client specification](https://github.com/tendermint/tendermint/tree/main/spec/light-client)
