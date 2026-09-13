# [M] Earned yield should be claimed on removal of a plugin

## Summary
Severity: Medium
Reporter: pashov
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L420
Type: audit-issue

## Details
# Earned yield should be claimed on removal of a plugin

## Summary
The code in `StakingModule` allows for the removal of plugins but if there was any earned yield for users it won't be possible for them to claim it

## Vulnerability Detail
The `removePlugin` method in `StakingModule` does not actually claim yield for stakers, so if they didn't call `claim` before the `PLUGIN_EDITOR` removes a plugin they will lose their accrued yield.

## Impact
Users can lose on accrued yield because of plugin removal, essentially a loss of value. 

## Code Snippet
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L420
## Tool used

Manual Review

## Recommendation
Add a separate functionality for users to be able to claim rewards from removed plugins.
