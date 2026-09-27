# [M] AttesterSlashing number overflow

## Summary
Severity: Medium
Chain: Ethereum
Component: ChainSafe/lodestar
CVE: CVE-2022-29219
Published: 2022-05-12
Source: https://github.com/ChainSafe/lodestar/security/advisories/GHSA-cvj7-5f3c-9vg9
Type: github-advisory

## Details
### Impact

Possible consensus split given maliciously-crafted `AttesterSlashing` or `ProposerSlashing` being included on-chain.

Since we represent `uint64` values as native javascript `number`s, there is an issue when those variables with large (greater than 2^53) `uint64` values are included on chain. In those cases, Lodestar may view _valid_ `AttesterSlashing` or `ProposerSlashing` as _invalid_, due to rounding errors in large `number` values. This causes a consensus split, where Lodestar nodes are forked away from the main network.

Similarly Lodestar may consider _invalid_ `ProposerSlashing` as _valid_, thus including in proposed blocks that will be considered invalid by the network.

### Patches

https://github.com/ChainSafe/lodestar/pull/3977

### Workarounds

Use `BigInt` to represent `Slot` and `Epoch` values in `AttesterSlashing` and `ProposerSlashing` objects. `BigInt` is too slow to be used in all `Slot` and `Epoch` cases, so we will carefully use `BigInt` just where necessary for consensus.
