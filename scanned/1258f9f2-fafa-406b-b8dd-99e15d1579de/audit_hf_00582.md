# [M] M-02 | Precision Loss May Not Allow All Users To Claim

## Summary
Severity: Medium
Contest weight: 0.6726
Dataset id: 2044
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the ExitVault contract, when users attempt to claim their rewards, the contract may revert with an error indicating that a transfer amount exceeds the contract's GMX token balance by a minimal amount (e.g., 1 wei). This issue is caused by the precision loss in the calculations of reward distributions within the ExitVault contract. The critical point of failure is in the reward calculation and distribution functions, where the contract updates users' reward debts and calculates pending rewards based on accumulated per share values. For example, when calculating pending rewards:
```solidity
uint256 pendingGmx = esGmxToVest * (block.timestamp - lastClaim) / 365 days;
pendingGmx = claimedGmx + pendingGmx > esGmxToVest ? esGmxToVest - claimedGmx : pendingGmx;
```
And when updating reward debts:
```solidity
s.userInfo[_recipient].gmxStream.wethRewardDebt = shares * s.accumulatedGmxWethPerShare / 1e18;
```
These calculations can introduce rounding errors due to integer division. As a result, when the contract attempts to distribute rewards, it may calculate that it needs to transfer slightly more tokens than it actually holds, leading to a revert when calling the transfer function of the GMX token contract.

## Recommendation
Before performing a transfer, check the contract's actual token balance and adjust the transfer amount if necessary to avoid attempting to transfer more than the available balance:
```solidity
uint256 contractBalance = IERC20(TOKEN_GMX).balanceOf(address(this));
uint256 transferAmount = reward > contractBalance ? contractBalance : reward;
```
