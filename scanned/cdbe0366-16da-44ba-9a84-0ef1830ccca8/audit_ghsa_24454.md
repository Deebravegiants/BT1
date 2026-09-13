# [H] AttesterSlashing number overflow

## Summary
Severity: High
Advisory: GHSA-cvj7-5f3c-9vg9
CVE: CVE-2022-29219
CWE: CWE-190
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-cvj7-5f3c-9vg9
Type: github-advisory

## Affected
- npm: `@chainsafe/lodestar` — affected >=0 <0.36.0

## Details
### Impact

Possible consensus split given maliciously-crafted `AttesterSlashing` or `ProposerSlashing` being included on-chain.

Since we represent `uint64` values as native javascript `number`s, there is an issue when those variables with large (greater than 2^53) `uint64` values are included on chain. In those cases, Lodestar may view _valid_ `AttesterSlashing` or `ProposerSlashing` as _invalid_, due to rounding errors in large `number` values. This causes a consensus split, where Lodestar nodes are forked away from the main network.

Similarly Lodestar may consider _invalid_ `ProposerSlashing` as _valid_, thus including in proposed blocks that will be considered invalid by the network.

### Patches

https://github.com/ChainSafe/lodestar/pull/3977

### Workarounds

Use `BigInt` to represent `Slot` and `Epoch` values in `AttesterSlashing` and `ProposerSlashing` objects. `BigInt` is too slow to be used in all `Slot` and `Epoch` cases, so we will carefully use `BigInt` just where necessary for consensus.

## References
- https://github.com/ChainSafe/lodestar/security/advisories/GHSA-cvj7-5f3c-9vg9
- https://nvd.nist.gov/vuln/detail/CVE-2022-29219
- https://github.com/ChainSafe/lodestar/pull/3977
- https://github.com/ChainSafe/lodestar
- https://github.com/ChainSafe/lodestar/releases/tag/v0.36.0
