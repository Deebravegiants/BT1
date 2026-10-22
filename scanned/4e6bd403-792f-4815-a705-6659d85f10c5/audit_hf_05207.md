# [H] Slashing doesn't workif any reward distributor is paused

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23346
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Description: Karma::_slash iterates over all reward distributors and claims rewards by calling IRewardDistributor::redeemRewards:
```solidity
function _slash(address account, address rewardRecipient) internal virtual returns (uint256) {
...
for (uint256 i = 0; i < rewardDistributors.length(); i++) {
    address distributor = rewardDistributors.at(i);
    22
    uint256 currentDistributorAccountBalance =
        IRewardDistributor(distributor).rewardsBalanceOfAccount(account);,!
    // then, calculate the amount to slash from each reward distributor
    totalAmountToSlash += _calculateSlashAmount(currentDistributorAccountBalance);
    // turn virtual Karma into real Karma for slashing
    @> IRewardDistributor(distributor).redeemRewards(account);
}
...
}
```
Problem is that StakeManager::redeemRewards is pausable:
```solidity
function redeemRewards(address account) external onlyNotEmergencyMode whenNotPaused returns (uint256) {,!
```
So users can't be slashed if any reward distributor is paused.

## Recommendation
Consider adding function isPaused() returns (bool) to interface IRewardDistributor and skip paused during slashing.
