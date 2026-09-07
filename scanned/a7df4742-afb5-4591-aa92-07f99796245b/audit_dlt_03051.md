# [M] Convex `BaseRewardPool` allows Claim on Behalf which causes delta to break - Loss of all Rewards

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1425
Type: code-finding

## Details
# Lines of code

https://etherscan.io/address/0x9D5C5E364D81DaB193b72db9E9BE9D8ee669B652#code#L979
https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/convex/ConvexTricryptoStrategy.sol#L254-L277


# Vulnerability details

### Impact
The Convex `BaseRewardPool` has a function `getReward(address _account, bool _claimExtras)`, which allows claiming on behalf of other accounts:

https://etherscan.io/address/0x9D5C5E364D81DaB193b72db9E9BE9D8ee669B652#code#L979

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

The [`ConvexTryCriptoStrategy`](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/convex/ConvexTricryptoStrategy.sol#L254-L277) uses delta balances to determine the amount of tokens gained

https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/convex/ConvexTricryptoStrategy.sol#L254-L277

```solidity
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1425_
