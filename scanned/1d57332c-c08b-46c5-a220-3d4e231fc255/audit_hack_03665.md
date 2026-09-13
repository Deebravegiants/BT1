# [M] `StakingModule` contract's external calls can result in DoS for users

## Summary
Severity: Medium
Reporter: pashov
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L388
Type: audit-issue

## Details
# `StakingModule` contract's external calls can result in DoS for users

## Summary
On most core functionality (staking, exiting) there is a call to the internal `_notifyStakeChangeAllPlugins` method, that does an unsafe external call

## Vulnerability Detail
The `_notifyStakeChangeAllPlugins` method is called in most core functionality (`stake`, `exit`) but it iterates over all plugins and tries to call `notifyStakeChange` on each. If even one of those call reverts due to the implementation or some other factor, then the users won't be able to claim their rewards, exit the contract or even stake.

## Impact
If this happens the protocol will be unusable and the already existing users will lose their funds. It requires the call to `IPlugin::notifyStakeChange` to revert, so it should be Medium severity.

## Code Snippet
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L388
## Tool used

Manual Review

## Recommendation
Do the external call in a try-catch block and log potential errors.
