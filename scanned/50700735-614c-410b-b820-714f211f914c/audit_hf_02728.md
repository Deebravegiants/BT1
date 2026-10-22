# [H] Incorrect activateBoost interface is

## Summary
Severity: High
Contest weight: 0.7365
Dataset id: 14841
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In Staker contract, we will activate our queued boost BGT. The interface we use is as below:  
```solidity
function activateBoost(address validator) external;
function _tryToBoost() internal {
    if (queued > 0 && blockDelta > 8191) {
        rewardCache.activateBoost(validator);
    }
}
```
When we check the BGT's implementation, we will find out that the correct interface should be like as below:  
```solidity
function activateBoost(address user, bytes calldata pubkey) external returns (bool) {
```
We use the incorrect interface, one address user parameter is needed. And this will cause that we cannot boost as expected. And this _tryToBoost() will be triggered by _updateRewardIntegral. And most functions in TroveManager will be impacted.

## Recommendation
Follow the BGT's implementation and trigger the correct activateBoost() interface.
