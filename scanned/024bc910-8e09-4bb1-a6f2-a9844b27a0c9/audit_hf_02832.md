# [M] Use of transferFrom is dangerous for non-compliant ERC 20 tokens

## Summary
Severity: Medium
Contest weight: 0.3881
Dataset id: 15758
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The ERC 20 transfer and transferFrom functions return a boolean indicating success which needs to be checked. However, some tokens do not revert if the transfer failed. Such tokens are USDC and USDT which are non-compliant to the ERC 20 standard. This could lead to stuck funds in the contract. An example of such implementation is inside CommunalFarm:  
```solidity
function _getReward()
    internal 
    updateRewardAndBalance(rewardee, true) 
    returns (uint256[] memory rewards_before) 
{
    IERC20(rewardTokens[i]).transfer(destination_address, rewards_before[i]); //@audit use safeTransfer
    emit RewardPaid(rewardee, rewards_before[i], rewardTokens[i], destination_address);
}
```

## Recommendation
Use safeTransfer of SafeERC20.
