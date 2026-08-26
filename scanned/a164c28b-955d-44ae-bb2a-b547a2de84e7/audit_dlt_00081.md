# [C] `InterfaceAccount` allows account substitution between unexpected types

## Summary
Severity: Critical
Chain: Solana
Component: coral-xyz/anchor
CWE: Improper Input Validation
Published: 2026-05-08
Source: https://github.com/otter-sec/anchor/security/advisories/GHSA-429q-fhh4-r6hj
Type: github-advisory

## Details
### Impact
Any uses of `InterfaceAccount` allows another unexpected account type to be passed, after https://github.com/solana-foundation/anchor/pull/3837 disabled discriminator checking for this type.

The bug was originally reported and fixed in https://github.com/solana-foundation/anchor/pull/4139, see that PR for more details.

### Patches
https://github.com/solana-foundation/anchor/pull/4139 patched the issue and was released in `1.0.0-rc.2`. Users should upgrade to the latest released version of Anchor 1.0.

### References
Bug landed in: https://github.com/solana-foundation/anchor/pull/3837
Bug fixed in: https://github.com/solana-foundation/anchor/pull/4139
