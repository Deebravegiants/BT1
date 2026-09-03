# [M] User can lose funds

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-05-vetoken
Published: 2022-05-27
Source: https://github.com/code-423n4/2022-05-vetoken-findings/issues/13
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-05-vetoken/blob/main/contracts/VE3DRewardPool.sol#L102


# Vulnerability details

## Impact
If _rewardToken is set as _stakingToken by mistake then user funds would get lost (staking token will get sent as reward token). Need to be fixed for BaseRewardPool.sol as well

## Proof of Concept
1. User A and B makes deposit of amount 100 each
2. Owner calls addReward and queueNewRewards to add 1 reward amount with _rewardToken as stakingToken (by mistake)
3. After some time reward is calculated as 5 for User A (total reward amount is same as staking amount which is 100+100+1). 
4. User A makes the withdraw and obtains 105 amount and now User B is stuck since contract does not have enough funds 


## Recommended Mitigation Steps
Add below check in constructor

```
require(_stakingToken!=_rewardToken, "Incorrect reward token");
```
