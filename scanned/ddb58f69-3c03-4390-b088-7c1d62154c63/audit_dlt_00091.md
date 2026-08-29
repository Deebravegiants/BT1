# [M] ASA-2024-002: Default `PrepareProposalHandler` may produce invalid proposals when used with default `SenderNonceMempool`

## Summary
Severity: Medium
Chain: Cosmos
Component: cosmos/cosmos-sdk
CWE: Improper Validation of Specified Index, Position, or Offset in Input
Published: 2024-02-20
Source: https://github.com/cosmos/cosmos-sdk/security/advisories/GHSA-2557-x9mg-76w8
Type: github-advisory

## Details
## ASA-2024-002: Default `PrepareProposalHandler` may produce invalid proposals when used with default `SenderNonceMempool`

**Component**: Cosmos SDK
**Criticality**: Medium
**Affected** Versions: Cosmos SDK versions <= 0.50.3; <= 0.47.8
**Affected** Users: Chain developers, Validator and Node operators
**Impact**: Denial of Service

## Summary

When using the default `PrepareProposalHandler` and the default `SenderNonceMempool`, an issue was identified which may allow invalid blocks to be proposed when a single sender includes multiple transactions with non-sequential sequence numbers in certain conditions. If this state is reached, it can lead to a reduction in block production for a network.

## Next Steps for Impacted Parties

If you are a chain developer on an affected version of the Cosmos SDK, it is advised to update to the latest available version of the Cosmos SDK for your project.  Once a patched version is available, it is recommended that network operators upgrade.

A Github Security Advisory for this issue is available in the Cosmos-SDK [repository](https://github.com/cosmos/cosmos-sdk/security/advisories). For more information about Cosmos SDK, see https://docs.cosmos.network/.

This issue was found by [KonradStaniec](https://github.com/KonradStaniec), [gitferry](https://github.com/gitferry), [SebastianElvis](https://github.com/SebastianElvis), and [vitsalis](https://github.com/vitsalis) who reported it to the Cosmos Bug Bounty Program on HackerOne on January 16, 2024. If you believe you have found a bug in the Interchain Stack or would like to contribute to the program by reporting a bug, please see https://hackerone.com/cosmos.
