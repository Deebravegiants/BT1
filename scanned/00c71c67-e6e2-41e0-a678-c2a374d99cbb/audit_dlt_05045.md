# [M] LSM-2024-001: LSM tokenization allows for potential slashing evasion when tokenizing redegelating shares

## Summary
Severity: Medium
Chain: Cosmos Hub
Component: cosmos/gaia
Published: 2024-06-05
Source: https://github.com/cosmos/gaia/security/advisories/GHSA-r47q-464x-wx5x
Type: github-advisory

## Details
**ID**: LSM-2024-001
**Component**: Liquid Staking Module (LSM)
**Criticality**: Medium
**Affected versions**: All
**Affected users**: Chain Builders + Maintainers, LSM service providers


### Summary
An issue was identified in the Liquid Staking Module that would allow a user to evade slashing penalties by tokenizing shares in the process of redelegation. Additional validation was added to prevent shares from being tokenized if redelegations are in progress. 

### Considerations 
Given a delegator D and a validator V, if D redelegated to validator V for a duration less than the unbonding period, then the tokenization of delegator D's share on validator V will fail. As a result, if any Liquidity Staking Module user relies on this action to not be disabled, this patch will introduce this new constraint and may affect adopters of this specific flow.

After this patch is applied, current shares that are tokenized and in the process of redelegation will remain tokenized. Once the unbonding period has elapsed, a chain using the Liquidity Staking Module will no longer have any tokenized shares in this unexpected state.

### Next Steps 
If your chain is a consumer of the Liquid Staking Module, we recommend that you sign up for the [security advisory mailing list](https://interchaincirt.org/signup) to receive security notifications about issues discovered in this component. 

This issue was discovered by [@arlai_mk](https://x.com/arlai_mk) and reported to the Cosmos Bug Bounty program on Apr 1, 2024, and was resolved by the teams at Informal Systems, Amulet, Iqlusion, and Stride. If you believe that you have found a security vulnerability in the Cosmos Hub or the Interchain Stack, or if you would like to contribute to the program by reporting a bug, please see [https://hackerone.com/cosmos](https://hackerone.com/cosmos).
