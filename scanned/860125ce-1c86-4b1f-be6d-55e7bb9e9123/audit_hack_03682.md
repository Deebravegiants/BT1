# [M] Adding too many plugins in `StakingModule` can result in DoS

## Summary
Severity: Medium
Reporter: pashov
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L409
Type: audit-issue

## Details
# Adding too many plugins in `StakingModule` can result in DoS

## Summary
If too many plugins are added then the gas costs for using the staking contract will be too much

## Vulnerability Detail
This is a pretty common issue with iteration over unbounded arrays. 
Consider the following scenario:
The `PLUGIN_EDITOR` turns malicious (or is compromised) and decides to add a lot (1000 for example) plugins.
Since on most core functionality (stake, exit) the code iterates over the whole `plugins` array, this will make the gas cost be higher than the block gas limit, essentially resulting in the impossibility of using the contract anymore. 

## Impact
The exploitation of this will result in DoS for users, so they will not be able to withdraw (or claim) their funds. 

## Code Snippet
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L409
## Tool used

Manual Review

## Recommendation
Add a maximum number of plugins allowed, for example 30.
