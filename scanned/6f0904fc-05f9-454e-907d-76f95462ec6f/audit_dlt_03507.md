# [M] Users may lose rewards to other users if rewards are given as fee-on-transfer tokens

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-05-aura
Published: 2022-05-23
Source: https://github.com/code-423n4/2022-05-aura-findings/issues/176
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-05-aura/blob/4989a2077546a5394e3650bf3c224669a0f7e690/contracts/ExtraRewardsDistributor.sol#L87-L98


# Vulnerability details

## Impact
If rewards are given in fee-on-transfer tokens, users may get no rewards, breaking functionality

`Med: Assets not at direct risk, but the function of the protocol or its availability could be impacted, or :::leak value with a hypothetical attack path with stated assumptions:::, but external requirements.`
(emphasis mine)

The underlying BAL protocol support fee-on-transfer tokens, so so should Aura

## Proof of Concept
```solidity
File: contracts/ExtraRewardsDistributor.sol   #1

87       function _addReward(
88           address _token,
89           uint256 _amount,
90           uint256 _epoch
91       ) internal nonReentrant {
92           // Pull before reward accrual
93           IERC20(_token).safeTransferFrom(msg.sender, address(this), _amount);
94   
95           //convert to reward per token
96           uint256 supply = auraLocker.totalSupplyAtEpoch(_epoch);
97           uint256 rPerT = (_amount * 1e20) / supply;
98           rewardData[_token][_epoch] += rPerT;
```
https://github.com/code-423n4/2022-05-aura/blob/4989a2077546a5394e3650bf3c224669a0f7e690/contracts/ExtraRewardsDistributor.sol#L87-L98

If a fee is charged the total amount available to be transferred later will be less than the `_amount` passed in.

Consider the following scenario:
User A holds 98% of the total supply of vlBAL (the system is being bootstrapped)

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-05-aura-findings/issues/176_
