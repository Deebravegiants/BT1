# [M] User can lose funds

## Summary
Severity: Medium
Contest weight: 0.4070
Dataset id: 9686
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability originates from a misconfiguration in the reward pool contract where the address used for the reward token can be set to the same ERC‑20 token that users deposit as the staking token. Because the contract does not enforce a distinction between these two roles, the reward distribution logic treats the staking token as a source of rewards and transfers it out of the pool when a user withdraws. The root cause is the absence of a constructor check that would reject a configuration in which _stakingToken equals _rewardToken, allowing an owner—or a malicious admin—to call addReward or queueNewRewards with the staking token as the reward token. When this occurs, early withdrawers receive an inflated amount that includes the staking tokens taken as rewards, while the total token balance remaining in the contract is reduced accordingly. Subsequent users attempting to withdraw later find that the contract no longer holds enough tokens to satisfy their principal, leading to a situation where their balance appears to be zero or they receive only a fraction of what they deposited. From the user's perspective the interface may show a successful withdrawal but the returned amount is lower than expected, or the UI may simply refuse the withdrawal due to insufficient pool funds. The impact is a loss of funds for honest participants, a breach of the accounting assumptions that rewards are drawn from a separate reserve, and a potential erosion of trust in the protocol. The issue was discovered during a Code4rena audit, where the warden demonstrated that by mistakenly configuring the reward token as the staking token, the contract would transfer staking tokens to early withdrawers and leave later participants stranded. Because the problem manifests only when the admin makes a specific configuration error, it may be hard to notice in normal operation where reward and staking tokens differ. The appropriate remediation is to add an explicit constructor validation (require(_stakingToken != _rewardToken)) and to enforce the same invariant in any function that sets or updates the reward token, thereby ensuring that reward distribution never drains the pool of deposited assets.

## Proof of Concept
1. User A and B makes deposit of amount 100 each
2. Owner calls addReward and queueNewRewards to add 1 reward amount with _rewardToken as stakingToken (by mistake)
3. After some time reward is calculated as 5 for User A (total reward amount is same as staking amount which is 100+100+1).
4. User A makes the withdraw and obtains 105 amount and now User B is stuck since contract does not have enough funds

## Recommendation
Add below check in constructor
```solidity
require(_stakingToken != _rewardToken, "Incorrect reward token");
```
It’s set by owner, so there is no issue, but it is nice to have and it is a quick fix.

The warden has shown how, due to a misconfiguration, the deposit token `stakingToken` could be transferred away to early withdrawers.

For end users the basic due diligence would be to ensure that the `stakingToken` is not added as reward.

Because the finding is contingent on a malicious admin / misconfiguration, I believe Medium Severity to be appropriate.
