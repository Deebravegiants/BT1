# [M] User looses StakeDao rewards, if he misses to call `claimCvgCvxRewards` for cycle

## Summary
Severity: Medium
Chain: Smart contract
Component: Convergence---Convex-integration
Published: 2024-05-02
Source: https://github.com/hats-finance/Convergence---Convex-integration-0xb3df23e155b74ad2b93777f58980d6727e8b40bb/issues/37
Type: hats-finding

## Details
**Github username:** @NicolaMirchev
**Twitter username:** nmirchev8
**Submission hash (on-chain):** 0x717420947f892992e5dee400f9de7036cb151c4e1ac30a3f99ee9215e7895e9e
**Severity:** medium

**Description:**
**Description**\

Inside [StakingServiceBase::_claimCvgCvxRewards](https://github.com/hats-finance/Convergence---Convex-integration-0xb3df23e155b74ad2b93777f58980d6727e8b40bb/blob/b3c66b1323cd555f5fa784b12736fd9b8f9ddfc5/contracts/Staking/Convex/StakingServiceBase.sol#L346) we set `maxLengthRewards` to the cycle, when was the last user interaction with contract, which is not correct, because we cannot be sure when will position owner claim his rewards. The impact is that user looses rewards, which are stucked in the contract

**Attack Scenario**\
Imagine the following scenario:
After cycle 0, on [processCvxRewards](https://github.com/hats-finance/Convergence---Convex-integration-0xb3df23e155b74ad2b93777f58980d6727e8b40bb/blob/b3c66b1323cd555f5fa784b12736fd9b8f9ddfc5/contracts/Staking/Convex/StakingServiceBase.sol#L450) is called and in this moment [CvxAssetStakerBuffer::pullReward](https://github.com/hats-finance/Convergence---Convex-integration-0xb3df23e155b74ad2b93777f58980d6727e8b40bb/blob/b3c66b1323cd555f5fa784b12736fd9b8f9ddfc5/contracts/Staking/Convex/cvxAsset/CvxAssetStakerBuffer.sol#L145-L197) set only token "A" as a reward token related to Stake Dao 
```
            _cvxRewardsByCycle[_cvgStakingCycle][erc20Id] = ICommonStruct.TokenAmount({
                token: _token,
                amount: _cvxRewardsByCycle[_cvgStakingCycle][erc20Id].amount + _rewardAssets[i].amount
            });
```
[So token A `erc20Id` is set as 1](https://github.com/hats-finance/Convergence---Convex-integration-0xb3df23e155b74ad2b93777f58980d6727e8b40bb/blob/b3c66b1323cd555f5fa784b12736fd9b8f9ddfc5/contracts/Staking/Convex/StakingServiceBase.sol#L461-L467).

After cycles 2 and 3, we have respectively new reward tokens B and C, which are set as 2 and 3 inside `_tokenToId[_token]` mapping.

The problem now is that if Bob misses to call `claimCvgCvxRewards` for a couple of cycles, he would miss to receive those tokens and they are stuck in the contract, because Bob's stakings are taken into [consideration while calculating each user reward share](https://github.com/hats-finance/Convergence---Convex-integration-0xb3df23e155b74ad2b93777f58980d6727e8b40bb/blob/b3c66b1323cd555f5fa784b12736fd9b8f9ddfc5/contracts/Staking/Convex/StakingServiceBase.sol#L385-L389).

- If Bob stakes at cycle = 0,
- 5 cycles have passed and he calls `claimCvgCvxRewards`:
[nextClaimableCvx = 1](https://github.com/hats-finance/Convergence---Convex-integration-0xb3df23e155b74ad2b93777f58980d6727e8b40bb/blob/b3c66b1323cd555f5fa784b12736fd9b8f9ddfc5/contracts/Staking/Convex/StakingServiceBase.sol#L337-L339) (nextCycle when he has staked)
[uint256 maxLengthRewards = 1(nextClaimableCvx);](https://github.com/hats-finance/Convergence---Convex-integration-0xb3df23e155b74ad2b93777f58980d6727e8b40bb/blob/b3c66b1323cd555f5fa784b12736fd9b8f9ddfc5/contracts/Staking/Convex/StakingServiceBase.sol#L346-L348)
`ICommonStruct.TokenAmount[] memory _totalRewardsClaimable = new ICommonStruct.TokenAmount[](1(maxLengthRewards));`

Inisde `StakeDAO` part we will only handle first reward token:
`_cvxRewardsByCycle[nextClaimableCvx][1]` (which is token A) for all missed cycles, while there are more  `erc20id`s ,which holds rewards for bob inside `_cvxRewardsByCycle[nextClaimableCvx][erc20Id + 1]`, but we won't handle them, because the [for loop](https://github.com/hats-finance/Convergence---Convex-integration-0xb3df23e155b74ad2b93777f58980d6727e8b40bb/blob/b3c66b1323cd555f5fa784b12736fd9b8f9ddfc5/contracts/Staking/Convex/StakingServiceBase.sol#L371) iterates only for the first `erc20id` (because we have set `maxLengthRewards` to the first cycle bob has staked)

At the end of the function we set `_nextClaims[tokenId].nextClaimableCvx = 5(actualCycle);` , which means that we have processed all pending rewards for all previous cycles, which is not true. 

For comparison, if user calls `claimCvgCvxRewards` for each cycle, he would receive more of  his rewards, because maxRewardLength is obtained from [here](https://github.com/hats-finance/Convergence---Convex-integration-0xb3df23e155b74ad2b93777f58980d6727e8b40bb/blob/b3c66b1323cd555f5fa784b12736fd9b8f9ddfc5/contracts/Staking/Convex/StakingServiceBase.sol#L332), but even in this case, some rewards may be missed.
**Attachments**

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Convergence---Convex-integration-0xb3df23e155b74ad2b93777f58980d6727e8b40bb/issues/37_
