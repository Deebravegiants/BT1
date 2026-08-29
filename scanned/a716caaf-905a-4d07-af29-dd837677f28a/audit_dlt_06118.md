# [?] Claim of AURA rewards can be griefed  by claiming for the contract (low severity)

## Summary
Severity: Unknown
Chain: Smart contract
Component: VMEX
Published: 2023-07-25
Source: https://github.com/hats-finance/VMEX-0xb6861bdeb368a1bf628fc36a36cec62d04fb6a77/issues/4
Type: hats-finding

## Details
**Communication channel:** GalloDaSballo (discord)

**Description**\
We can harvest without emitting the `HarvestedReward` event by performing a claim on behalf of the staking contract


```solidity
    function getReward(address _account, bool _claimExtras) public updateReward(_account) returns(bool){
        uint256 reward = earned(_account);
        if (reward > 0) {
            rewards[_account] = 0;
            rewardToken.safeTransfer(_account, reward);
            IDeposit(operator).rewardClaimed(pid, _account, reward);
            emit RewardPaid(_account, reward);
        }

        //also get rewards from linked rewards
        if(_claimExtras){
            for(uint i=0; i < extraRewards.length; i++){
                IRewards(extraRewards[i]).getReward(_account);
            }
        }
        return true;
    }
```
https://optimistic.etherscan.io/address/0x9f43f726df654e033b04c39989af90ab44875feb#code#F14#L296

**Attack Scenario**\
This can be done to grief the reward tracking, a more appropriate tracking should be done in the reward pool by filtering for the address of the staking contract
##
