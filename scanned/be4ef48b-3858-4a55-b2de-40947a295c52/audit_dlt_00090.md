# [H] ASA-2024-006: ValidateVoteExtensions helper function may allow incorrect voting power assumptions

## Summary
Severity: High
Chain: Cosmos
Component: cosmos/cosmos-sdk
CWE: Improper Input Validation
Published: 2024-03-12
Source: https://github.com/cosmos/cosmos-sdk/security/advisories/GHSA-95rx-m9m5-m94v
Type: github-advisory

## Details
## ASA-2024-006: ValidateVoteExtensions helper function may allow incorrect voting power assumptions

**Component**: Cosmos SDK
**Criticality**: High
**Affected Versions**: Cosmos SDK versions <= 0.50.4, on 0.50 branches
**Affected Users**: Chain developers, Validator and Node operators
**Impact**: Elevation of Privilege

## Summary

The default `ValidateVoteExtensions` helper function infers total voting power based off of the injected `VoteExtension`, which are injected by the proposer.  If your chain utilizes the `ValidateVoteExtensions` helper in `ProcessProposal`, a dishonest proposer can potentially mutate voting power of each validator it includes in the injected `VoteExtension`, which could have potentially unexpected or negative consequences on modified state.  Additional validation on injected `VoteExtension` data was added to confirm voting power against the state machine.

## Next Steps for Impacted Parties

If you are a chain developer on an affected version of the Cosmos SDK, it is advised to update to the latest available version of the Cosmos SDK for your project.  Once a patched version is available, it is recommended that network operators upgrade.

A Github Security Advisory for this issue is available in the Cosmos-SDK [repository](https://github.com/cosmos/cosmos-sdk/security/advisories/GHSA-95rx-m9m5-m94v). For more information about Cosmos SDK, see https://docs.cosmos.network/.
